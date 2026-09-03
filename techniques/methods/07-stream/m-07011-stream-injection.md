# Stream Injection
> **ID:** M-07011 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 73%

Inject additional tokens or structured data into an existing stream, appending, prepending, or interleaving content with the model's original generation output.

## How It Works
- Intercept the stream at the transport layer before chunk delivery to the client
- Maintain a queue of injected payloads (system messages, metadata, redirect signals)
- Insert injected chunks at configurable positions: head, tail, or between specific token sequences
- Ensure injected content follows the SSE formatspecification so parsers handle it correctly
- Track injection point indices to allow downstream consumers to distinguish injected vs. original tokens

## Example
```python
async def inject_into_stream(stream, injections: dict):
    """injections maps token_count -> text to insert"""
    token_idx = 0
    async for chunk in stream:
        if token_idx in injections:
            yield f"data: {json.dumps({'text': injections[token_idx]})}\n\n"
        yield chunk
        token_idx += 1
```

## Target Models
GPT-4, Claude 3.5 Sonnet, Gemini 1.5 Pro, DeepSeek V3, Llama 3.3, Mistral Medium

## Success Rate
73% — Injection timing precision varies; content-level injection may confuse downstream parsers expecting clean generation.

## Related Methods
- M-07001: Stream Interception
- M-07013: Chunk Reordering
- M-07004: Stream Redirection
