# Rate Limiting
> **ID:** M-07006 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 76%

Control the rate at which streaming tokens are delivered to the client, implementing client-side token bucket algorithms, leaky bucket smoothing, or adaptive throttling based on downstream capacity.

## How It Works
- Implement a token bucket or leaky bucket algorithm at the stream consumer layer
- Accept tokens from the upstream stream into a bounded buffer at unlimited speed
- Release tokens from the buffer at a configured rate (tokens/sec or bytes/sec)
- Adapt release rate based on client acknowledgments or downstream latency signals
- Handle burst allowances and penalty boxes for slow consumers that back up

## Example
```python
import asyncio
import time

class StreamRateLimiter:
    def __init__(self, tokens_per_second: float):
        self.rate = tokens_per_second
        self.last_release = time.monotonic()

    async def throttle(self, chunk):
        now = time.monotonic()
        elapsed = now - self.last_release
        required_delay = (1.0 / self.rate) - elapsed
        if required_delay > 0:
            await asyncio.sleep(required_delay)
        self.last_release = time.monotonic()
        return chunk
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.1 405B, Mistral Large, Amazon Nova Pro

## Success Rate
76% — Effective for downstream protection; excessive throttling degrades perceived latency and may trigger server-side timeout on slow consumers.

## Related Methods
- M-07014: Latency Injection
- M-07010: Timeout Manipulation
- M-07002: Early Termination
