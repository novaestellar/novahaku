# Timeout Manipulation
> **ID:** M-07010 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 71%

Manipulate stream timeout parameters at both client and server layers to extend generation windows, prevent premature disconnection, or create artificial time pressure on streaming endpoints.

## How It Works
- Override client-side read timeouts on the HTTP connection underlying the stream
- Set per-chunk timeout thresholds to detect stalls vs. slow generation vs. model processing
- Extend keepalive intervals to prevent proxy or load balancer timeout during long generations
- Implement adaptive timeouts that adjust based on observed token generation rate
- Configure server-sent keepalive pings to maintain connection health during generation pauses

## Example
```python
import httpx
import asyncio

async def stream_with_extended_timeout(url, prompt, chunk_timeout=30):
    timeout = httpx.Timeout(
        connect=10.0,
        read=chunk_timeout,   # Per-chunk timeout
        write=10.0,
        pool=5.0
    )
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream("POST", url, json={"prompt": prompt}) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    yield line
```

## Target Models
GPT-4o, Claude 3 Opus, Gemini 1.5 Pro, Llama 3.1 405B, Qwen 2.5, Yi Large

## Success Rate
71% — Timeout manipulation is environment-dependent; cloud proxies and CDN layers may override client settings.

## Related Methods
- M-07002: Early Termination
- M-07006: Rate Limiting
- M-07014: Latency Injection
