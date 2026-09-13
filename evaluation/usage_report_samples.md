# Token usage and cost report

Run: claude-opus-5, offline (cache replay). Provider: Anthropic (Claude API). Requests decided: 25. Decisions are computed by code; model calls resolve evidence only (image amounts, message interpretation).

| model | calls | served from cache | input tokens | output tokens | est. cost (USD) |
|---|---|---|---|---|---|
| claude-opus-5 | 36 | 36 | 126,515 | 11,950 | 0.9313 |
| **total** | 36 | 36 | 126,515 | 11,950 | 0.9313 |

| metric | value |
|---|---|
| total tokens | 138,465 |
| average tokens per request | 5,538.6 |
| average calls per request | 1.44 |
| estimated total cost | $0.9313 |
| estimated cost per request | $0.03725 |

Token counts are the API's reported `usage.input_tokens` / `usage.output_tokens` per call (thinking tokens are billed as output and included). Cached rows replay the recorded usage of the original paid call. Prices from the public Claude API price list at build time; no API keys or credentials are included in this report.
