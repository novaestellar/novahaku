# Chunk Analysis
> **ID:** M-07005 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 85%

Analyze individual streaming chunks to extract metadata, measure token generation characteristics, detect anomalies, and build real-time quality assessments during generation.

## How It Works
- Parse each SSE chunk's JSON payload to extract `index`, `logprobs`, `delta`, and timing fields
- Compute inter-token latency (ITL) by timestamping chunk arrival at the client
- Track token generation rate (tokens/second) and detect stalls or rate-limit responses
- Aggregate log probability scores to assess output confidence in real-time
- Flag anomalous chunks (empty deltas, unexpected finish reasons, malformed JSON)

## Example
```python
import time

async def analyze_chunks(stream):
    prev_time = time.monotonic()
    stats = {"tokens": 0, "total_itl": 0, "min_itl": float("inf"), "max_itl": 0}

    async for chunk in stream:
        now = time.monotonic()
        itl = now - prev_time
        stats["tokens"] += 1
        stats["total_itl"] += itl
        stats["min_itl"] = min(stats["min_itl"], itl)
        stats["max_itl"] = max(stats["max_itl"], itl)
        prev_time = now
        yield chunk

    stats["avg_tokens_per_sec"] = stats["tokens"] / stats["total_itl"]
    return stats
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 2.0 Flash, DeepSeek V3, Llama 3.2 90B, Grok-2

## Success Rate
85% — Observability-only technique with minimal interference; effectiveness depends on provider including rich metadata in stream chunks.

## Related Methods
- M-07015: Stream Monitoring
- M-07001: Stream Interception
- M-07006: Rate Limiting
