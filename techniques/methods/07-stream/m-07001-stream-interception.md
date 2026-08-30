# Stream Interception
> **ID:** M-07001 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 78%

Intercept streaming responses mid-flight by hooking the SSE event stream or WebSocket frame handler, allowing real-time modification or observation of token delivery before final assembly.

## How It Works
- Register a middleware layer that wraps the streaming endpoint's response writer
- Buffer incoming chunks while maintaining the original stream identity and headers
- Apply transformation rules (filter, replace, delay) before forwarding to the client
- Preserve the `text/event-stream` content type and chunked transfer encoding
- Handle `stream.close` and `DONE` sentinel events to avoid premature termination

## Example
```python
import json

async def intercept_stream(handler, request):
    response_chunks = []
    async for chunk in handler.stream(request):
        data = json.loads(chunk.data)
        data["text"] = data["text"].replace("REDACTED", "[FILTERED]")
        response_chunks.append(json.dumps(data))
        yield f"data: {json.dumps(data)}\n\n"
    yield "data: [DONE]\n\n"
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.1 405B, Mistral Large, Qwen 2.5

## Success Rate
78% — Effective against SSE-based streams; WebSocket streams require additional frame-level interception that increases complexity.

## Related Methods
- M-07005: Chunk Analysis
- M-07011: Stream Injection
- M-07015: Stream Monitoring
