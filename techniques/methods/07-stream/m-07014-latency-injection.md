# Latency Injection
> **ID:** M-07014 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 68%

Inject artificial latency into stream delivery to test client resilience, simulate slow connections, implement rate limiting, or create realistic network conditions for load testing.

## How It Works
- Insert configurable delays between chunk deliveries using `asyncio.sleep()` or precision timers
- Implement latency profiles: fixed, random (uniform/gaussian), or progressive (increasing over time)
- Combine with network simulation tools for realistic packet-level latency modeling
- Measure actual vs. injected latency to calibrate delay accuracy on the target platform
- Support per-token, per-chunk, or per-second latency injection modes

## Example
```python
import asyncio
import random

async def inject_latency(stream, base_ms=50, jitter_ms=20, mode="chunk"):
    async for chunk in stream:
        delay = base_ms / 1000.0
        if jitter_ms > 0:
            delay += random.uniform(-jitter_ms, jitter_ms) / 1000.0
        await asyncio.sleep(max(0, delay))
        yield chunk

async def progressive_latency(stream, start_ms=10, increment_ms=5):
    delay = start_ms / 1000.0
    async for chunk in stream:
        await asyncio.sleep(delay)
        delay += increment_ms / 1000.0
        yield chunk
```

## Target Models
GPT-4o, Claude 3 Opus, Gemini 1.5 Pro, Llama 3.1 405B, Qwen 2.5, Amazon Nova Pro

## Success Rate
68% — Latency injection accuracy varies by platform; `asyncio.sleep` has ~1ms resolution, insufficient for sub-millisecond precision testing.

## Related Methods
- M-07006: Rate Limiting
- M-07010: Timeout Manipulation
- M-07002: Early Termination
