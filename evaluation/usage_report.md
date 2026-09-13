# Token usage and cost report

Run: claude-opus-5, offline (cache replay). Provider: Anthropic (Claude API). Requests decided: 250. Decisions are computed by code; model calls resolve evidence only (image amounts, message interpretation).

| model | calls | served from cache | input tokens | output tokens | est. cost (USD) |
|---|---|---|---|---|---|
| claude-opus-5 | 297 | 297 | 1,044,228 | 110,798 | 7.9911 |
| **total** | 297 | 297 | 1,044,228 | 110,798 | 7.9911 |

| metric | value |
|---|---|
| total tokens | 1,155,026 |
| average tokens per request | 4,620.1 |
| average calls per request | 1.19 |
| estimated total cost | $7.9911 |
| estimated cost per request | $0.03196 |

Token counts are the API's reported `usage.input_tokens` / `usage.output_tokens` per call (thinking tokens are billed as output and included). Cached rows replay the recorded usage of the original paid call. Prices from the public Claude API price list at build time; no API keys or credentials are included in this report.
