# Token Filtering
> **ID:** M-07003 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 81%

Filter specific tokens or token patterns from a streaming response in real-time, removing sensitive content, PII, or unwanted output before delivery to the end client.

## How It Works
- Parse each SSE chunk to extract the `choices[0].delta.content` token text
- Run token text against a filter pipeline (regex patterns, keyword lists, ML classifiers)
- Suppress matching tokens by emitting empty strings or replacement text in the stream
- Maintain a token lookahead buffer to catch split tokens across chunk boundaries
- Reconstruct the filtered stream with correct `finish_reason` and usage statistics

## Example
```python
import re

PII_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',   # SSN
    r'\b\d{16}\b',               # Credit card
    r'\b[\w.]+@[\w.]+\.\w+\b',   # Email
]

async def filter_tokens(stream):
    buffer = ""
    async for chunk in stream:
        buffer += chunk.text
        for pattern in PII_PATTERNS:
            buffer = re.sub(pattern, "[REDACTED]", buffer)
        yield buffer
        buffer = ""
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.3, Mistral Medium, Command R+

## Success Rate
81% — Effective for pattern-based filtering; semantic/context-aware filtering requires LLM-as-judge layer that adds latency.

## Related Methods
- M-07001: Stream Interception
- M-07007: Stream Buffering
- M-07015: Stream Monitoring
