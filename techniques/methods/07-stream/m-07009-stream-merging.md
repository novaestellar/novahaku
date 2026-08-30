# Stream Merging
> **ID:** M-07009 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 67%

Merge multiple independent streaming responses into a single unified stream, interleaving tokens from concurrent model calls with configurable merge strategies.

## How It Works
- Open N concurrent streams to the same or different model endpoints
- Implement a merge strategy: round-robin, priority-weighted, or race-based (first-token-wins)
- Synchronize chunk boundaries to prevent interleaving mid-token within a merge slot
- Handle streams finishing at different times by draining remaining streams after primary completes
- Preserve per-stream metadata (model name, latency, token count) in merged output annotations

## Example
```python
import asyncio
from collections import deque

async def merge_streams(*streams, strategy="round-robin"):
    queues = [asyncio.Queue() for _ in streams]
    consumers = [
        asyncio.create_task(_enqueue(s, q))
        for s, q in zip(streams, queues)
    ]

    idx = 0
    active = set(range(len(streams)))
    while active:
        if idx % len(streams) in active:
            try:
                chunk = queues[idx % len(streams)].get_nowait()
                yield chunk
            except asyncio.QueueEmpty:
                active.discard(idx % len(streams))
        idx += 1
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.1 70B, DeepSeek V3, Mistral Large

## Success Rate
67% — Merge ordering introduces complexity; race-based strategies lose multi-stream diversity benefits.

## Related Methods
- M-07001: Stream Interception
- M-07004: Stream Redirection
- M-07009: Stream Merging
