# Chunk Reordering
> **ID:** M-07013 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 64%

Reorder streaming chunks based on priority, content type, or completion status, delivering the most important or context-setting tokens first in latency-sensitive applications.

## How It Works
- Buffer incoming chunks and tag each with a priority score based on content analysis
- Implement a priority queue that reorders chunks by importance (keywords, structure tokens, content tokens)
- Forward high-priority chunks immediately while buffering lower-priority ones
- Reassemble the final output in original order after all chunks are received for completeness
- Handle the tension between reordered delivery and maintaining coherent partial text

## Example
```python
import heapq

PRIORITY_KEYWORDS = {"```": 10, "# ": 8, "def ": 7, "class ": 7, "import ": 5}

async def reorder_stream(stream, priority_keywords):
    pending = []
    async for chunk in stream:
        priority = max(
            (score for kw, score in priority_keywords.items() if kw in chunk),
            default=1
        )
        heapq.heappush(pending, (-priority, chunk))

        if len(pending) >= 5:
            _, best = heapq.heappop(pending)
            yield best

    while pending:
        _, chunk = heapq.heappop(pending)
        yield chunk
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, DeepSeek V3, Llama 3.1 70B, Mistral Large

## Success Rate
64% — Reordering can break sentence coherence; most effective for structured output (code, JSON) where token order is less critical.

## Related Methods
- M-07005: Chunk Analysis
- M-07008: Partial Response
- M-07011: Stream Injection
