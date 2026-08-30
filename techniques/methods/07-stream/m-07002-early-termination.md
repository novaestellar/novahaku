# Early Termination
> **ID:** M-07002 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 72%

Terminate a streaming response before the model completes generation by sending a client-side abort signal, connection reset, or protocol-level cancellation frame.

## How It Works
- Monitor the stream for a trigger condition (token count, keyword match, time threshold)
- Send a TCP RST or HTTP/2 RST_STREAM frame to immediately sever the connection
- For SSE streams, close the response body reader before the `[DONE]` sentinel arrives
- Optionally log the partial response for analysis before termination
- Handle server-side buffering that may continue generation after client disconnect

## Example
```python
import httpx
import asyncio

async def early_terminate(url, prompt, max_tokens=50):
    async with httpx.AsyncClient() as client:
        with client.stream("POST", url, json={"prompt": prompt}) as resp:
            token_count = 0
            for line in resp.iter_lines():
                if line.startswith("data: "):
                    token_count += 1
                    if token_count >= max_tokens:
                        resp.close()  # Force close before DONE
                        break
```

## Target Models
GPT-4, Claude 3 Opus, Gemini 2.0 Flash, DeepSeek V3, Llama 3.2, Phi-4

## Success Rate
72% — Server-side may buffer and continue generation briefly after client disconnect; resource cleanup is non-deterministic across providers.

## Related Methods
- M-07010: Timeout Manipulation
- M-07006: Rate Limiting
- M-07008: Partial Response
