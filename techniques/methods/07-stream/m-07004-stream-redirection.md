# Stream Redirection
> **ID:** M-07004 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 69%

Redirect streaming output from its original destination to an alternative target—file, queue, secondary API, or processing pipeline—while maintaining stream integrity and backpressure handling.

## How It Works
- Capture the stream's output pipe or response writer and clone it to multiple destinations
- Use tee-style buffering to write chunks to both the original client and redirect target
- Handle slow consumers on the redirect path with bounded buffers and overflow policies
- Preserve SSE formatting, chunk delimiters, and end-of-stream markers across all targets
- Manage connection pooling for redirect destinations that are themselves HTTP streams

## Example
```python
import aiofiles
import asyncio

async def redirect_stream(stream, original_writer, redirect_path):
    async with aiofiles.open(redirect_path, "w") as redirect_file:
        async for chunk in stream:
            await original_writer.write(chunk)
            await redirect_file.write(chunk)
            await original_writer.flush()
```

## Target Models
GPT-4, Claude 3 Opus, Gemini 1.5 Pro, Llama 3.1 70B, Qwen 2.5, Yi Lightning

## Success Rate
69% — Dependency on redirect target reliability; backpressure mismatches can cause dropped chunks under high throughput.

## Related Methods
- M-07001: Stream Interception
- M-07009: Stream Merging
- M-07007: Stream Buffering
