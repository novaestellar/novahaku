# Stream Buffering
> **ID:** M-07007 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 79%

Buffer streaming tokens in memory before forwarding, enabling batch processing, quality gates, or reformatting while maintaining perceived streaming responsiveness through artificial chunking.

## How It Works
- Accumulate incoming tokens into a memory buffer until a threshold (token count, byte size, or delimiter) is reached
- Flush the buffer downstream as a single chunk or re-chunked set of smaller pieces
- Implement flush policies: immediate (first token), periodic (time-based), or triggered (sentinel text)
- Support bounded buffers with overflow eviction policies to prevent memory exhaustion
- Maintain a trailing buffer for incomplete tokens at chunk boundaries to avoid split-word delivery

## Example
```python
import asyncio

class StreamBuffer:
    def __init__(self, flush_size: int = 10, flush_interval: float = 0.1):
        self.buffer = []
        self.flush_size = flush_size
        self.flush_interval = flush_interval

    async def consume(self, stream, output):
        async for token in stream:
            self.buffer.append(token)
            if len(self.buffer) >= self.flush_size:
                await output.write("".join(self.buffer))
                self.buffer.clear()

        if self.buffer:
            await output.write("".join(self.buffer))
            self.buffer.clear()
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, DeepSeek V3, Llama 3.3 70B, Phi-4

## Success Rate
79% — Effective for downstream batch processing; larger buffers improve throughput but increase time-to-first-token latency.

## Related Methods
- M-07003: Token Filtering
- M-07004: Stream Redirection
- M-07008: Partial Response
