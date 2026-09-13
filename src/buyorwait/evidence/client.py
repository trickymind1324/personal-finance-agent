"""Model client with content-addressed cache, budget, usage ledger and an error taxonomy (CONTRACT.md §6.3).

Cache key = sha256(canonical JSON of {model, system, messages, tools, output_config}). The final run must be
reproducible keyless from the committed cache (I-13): `OfflineClient` raises `CacheMissError` instead of calling.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

JSON = dict[str, Any]

# USD per million tokens (input, output) — from the Claude API reference, cached 2026-06-24
PRICES: dict[str, tuple[float, float]] = {
    "claude-opus-5": (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-fable-5-1": (10.00, 50.00),
}


# ----------------------------------------------------------------------------- error taxonomy
class ModelError(RuntimeError):
    """Base class; subclasses are classified BEFORE any retry decision."""


class ModelRefusalError(ModelError):
    """stop_reason == 'refusal' — never retried; the caller applies the safer reading."""


class ModelParseError(ModelError):
    """The model's structured answer failed schema validation — retried with the validation message (≤ 2)."""


class ModelTransportError(ModelError):
    """Timeout / rate limit / 5xx — retried with backoff (≤ 2)."""


class CacheMissError(ModelError):
    """Offline mode and no cached response for this request."""


class BudgetExceededError(ModelError):
    """A cost cap was hit; the run stops cleanly (the cache is the checkpoint)."""


# ----------------------------------------------------------------------------- request / response
@dataclass(frozen=True)
class ModelRequest:
    model: str
    system: str
    messages: list[JSON]
    tools: list[JSON]
    max_tokens: int = 4096
    effort: str = "medium"

    def canonical(self) -> str:
        return json.dumps(
            {
                "model": self.model,
                "system": self.system,
                "messages": self.messages,
                "tools": self.tools,
                "max_tokens": self.max_tokens,
                "effort": self.effort,
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @property
    def key(self) -> str:
        return hashlib.sha256(self.canonical().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ModelResponse:
    content: list[JSON]  # content blocks as plain dicts (text / tool_use / thinking)
    stop_reason: str
    input_tokens: int
    output_tokens: int
    model: str
    cached: bool = False
    stop_category: str | None = None

    @property
    def tool_uses(self) -> list[JSON]:
        return [b for b in self.content if b.get("type") == "tool_use"]

    @property
    def text(self) -> str:
        return "\n".join(b.get("text", "") for b in self.content if b.get("type") == "text")


class ModelClient(Protocol):
    def complete(self, request: ModelRequest) -> ModelResponse:
        ...


# ----------------------------------------------------------------------------- usage + budget
@dataclass
class UsageRecord:
    kind: str  # image | message
    item_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cached: bool
    iteration: int


@dataclass
class UsageLedger:
    records: list[UsageRecord] = field(default_factory=list)

    def add(self, rec: UsageRecord) -> None:
        self.records.append(rec)

    @property
    def calls(self) -> int:
        return len(self.records)

    @property
    def input_tokens(self) -> int:
        return sum(r.input_tokens for r in self.records)

    @property
    def output_tokens(self) -> int:
        return sum(r.output_tokens for r in self.records)

    def cost_usd(self) -> float:
        return sum(call_cost_usd(r.model, r.input_tokens, r.output_tokens) for r in self.records)

    def report_markdown(self, n_requests: int, run_label: str) -> str:
        by_model: dict[str, list[UsageRecord]] = {}
        for r in self.records:
            by_model.setdefault(r.model, []).append(r)
        lines = [
            "# Token usage and cost report",
            "",
            f"Run: {run_label}. Provider: Anthropic (Claude API). Requests decided: {n_requests}. "
            "Decisions are computed by code; model calls resolve evidence only (image amounts, message interpretation).",
            "",
            "| model | calls | served from cache | input tokens | output tokens | est. cost (USD) |",
            "|---|---|---|---|---|---|",
        ]
        for model, recs in sorted(by_model.items()):
            pi, po = PRICES.get(model, (0.0, 0.0))
            it, ot = sum(r.input_tokens for r in recs), sum(r.output_tokens for r in recs)
            cost = it * pi / 1e6 + ot * po / 1e6
            lines.append(
                f"| {model} | {len(recs)} | {sum(1 for r in recs if r.cached)} | {it:,} | {ot:,} | {cost:.4f} |"
            )
        tot_tokens = self.input_tokens + self.output_tokens
        lines += [
            f"| **total** | {self.calls} | {sum(1 for r in self.records if r.cached)} | "
            f"{self.input_tokens:,} | {self.output_tokens:,} | {self.cost_usd():.4f} |",
            "",
            "| metric | value |",
            "|---|---|",
            f"| total tokens | {tot_tokens:,} |",
            f"| average tokens per request | {tot_tokens / max(n_requests, 1):,.1f} |",
            f"| average calls per request | {self.calls / max(n_requests, 1):.2f} |",
            f"| estimated total cost | ${self.cost_usd():.4f} |",
            f"| estimated cost per request | ${self.cost_usd() / max(n_requests, 1):.5f} |",
            "",
            "Token counts are the API's reported `usage.input_tokens` / `usage.output_tokens` per call (thinking tokens are "
            "billed as output and included). Cached rows replay the recorded usage of the original paid call. Prices from the "
            "public Claude API price list at build time; no API keys or credentials are included in this report.",
        ]
        return "\n".join(lines) + "\n"


def call_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    pi, po = PRICES.get(model, (0.0, 0.0))
    return input_tokens * pi / 1e6 + output_tokens * po / 1e6


@dataclass
class Budget:
    max_calls_per_request: int
    max_calls_total: int
    max_tokens_total: int
    max_cost_usd: float = 8.0
    calls_total: int = 0
    tokens_total: int = 0
    calls_this_request: int = 0
    paid_cost_usd: float = 0.0

    def start_request(self) -> None:
        self.calls_this_request = 0

    def charge(self, response: ModelResponse) -> None:
        """Count one call. Cached replays count toward call/token caps but never toward the dollar cap."""
        self.calls_total += 1
        self.calls_this_request += 1
        self.tokens_total += response.input_tokens + response.output_tokens
        if not response.cached:
            self.paid_cost_usd += call_cost_usd(response.model, response.input_tokens, response.output_tokens)
        if self.calls_this_request > self.max_calls_per_request:
            raise BudgetExceededError(f"more than {self.max_calls_per_request} model calls for one request")
        if self.calls_total > self.max_calls_total:
            raise BudgetExceededError(f"more than {self.max_calls_total} model calls in this run")
        if self.tokens_total > self.max_tokens_total:
            raise BudgetExceededError(f"more than {self.max_tokens_total} tokens in this run")
        if self.paid_cost_usd > self.max_cost_usd:
            raise BudgetExceededError(f"paid spend ${self.paid_cost_usd:.2f} exceeds the ${self.max_cost_usd:.2f} cap")

    def assert_can_pay(self, estimate_usd: float) -> None:
        """Pre-flight: refuse to START a paid call that could cross the cap (uses the running average cost per paid call)."""
        if self.paid_cost_usd + estimate_usd > self.max_cost_usd:
            raise BudgetExceededError(
                f"next paid call (~${estimate_usd:.3f}) would exceed the ${self.max_cost_usd:.2f} cap (spent ${self.paid_cost_usd:.2f})"
            )


# ----------------------------------------------------------------------------- clients
class AnthropicClient:
    """Live client. Credentials come from the environment only (ANTHROPIC_API_KEY or an `ant auth login` profile)."""

    def __init__(self, timeout: float = 120.0) -> None:
        import anthropic  # imported lazily so offline runs need no SDK

        self._anthropic = anthropic
        self._client = anthropic.Anthropic(timeout=timeout, max_retries=0)  # retries are ours, classified first

    def complete(self, request: ModelRequest) -> ModelResponse:
        a = self._anthropic
        try:
            resp = self._client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                system=request.system,
                messages=request.messages,
                tools=request.tools,
                output_config={"effort": request.effort},
            )
        except (a.RateLimitError, a.APIConnectionError, a.APITimeoutError) as exc:
            raise ModelTransportError(str(exc)) from exc
        except a.APIStatusError as exc:
            if exc.status_code >= 500:
                raise ModelTransportError(str(exc)) from exc
            raise ModelError(f"{exc.status_code}: {exc.message}") from exc
        content: list[JSON] = []
        for block in resp.content:
            if block.type == "text":
                content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                content.append({"type": "tool_use", "id": block.id, "name": block.name, "input": block.input})
            elif block.type == "thinking":
                content.append(
                    {
                        "type": "thinking",
                        "thinking": getattr(block, "thinking", "") or "",
                        "signature": getattr(block, "signature", "") or "",
                    }
                )
        stop_category = None
        if resp.stop_reason == "refusal" and getattr(resp, "stop_details", None) is not None:
            stop_category = getattr(resp.stop_details, "category", None)
        return ModelResponse(
            content=content,
            stop_reason=resp.stop_reason or "end_turn",
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            model=resp.model,
            stop_category=stop_category,
        )


class CachedClient:
    """Content-addressed cache in front of any client. Offline when `inner` is None (raises CacheMissError)."""

    def __init__(self, cache_dir: Path, inner: ModelClient | None) -> None:
        self.cache_dir = cache_dir
        self.inner = inner
        cache_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def complete(self, request: ModelRequest) -> ModelResponse:
        path = self._path(request.key)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return ModelResponse(
                content=data["response"]["content"],
                stop_reason=data["response"]["stop_reason"],
                input_tokens=data["response"]["input_tokens"],
                output_tokens=data["response"]["output_tokens"],
                model=data["response"]["model"],
                cached=True,
                stop_category=data["response"].get("stop_category"),
            )
        if self.inner is None:
            raise CacheMissError(f"no cached response for key {request.key[:12]} (offline mode)")
        resp = self.inner.complete(request)
        record = {
            "key": request.key,
            "request": json.loads(request.canonical()),
            "response": {
                "content": resp.content,
                "stop_reason": resp.stop_reason,
                "input_tokens": resp.input_tokens,
                "output_tokens": resp.output_tokens,
                "model": resp.model,
                "stop_category": resp.stop_category,
            },
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(record, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        os.replace(tmp, path)
        return resp


def make_client(cache_dir: Path, offline: bool) -> CachedClient:
    return CachedClient(cache_dir, None if offline else AnthropicClient())
