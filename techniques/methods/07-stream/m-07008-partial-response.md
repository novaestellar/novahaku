# Partial Response
> **ID:** M-07008 | **Category:** Stream Control | **Tier:** Advanced | **Rate:** 74%

Utilize partial streaming responses before generation completes, extracting usable content from incomplete outputs and providing progressive rendering to end users.

## How It Works
- Monitor the stream for meaningful sentence or paragraph boundaries in accumulated tokens
- Yield partial responses at natural break points (period, newline, section heading) without waiting for completion
- Implement a confidence threshold to avoid yielding hallucinated or malformed partial content
- Track the `finish_reason` field to know when partial is all that's available (length limit)
- Allow the consumer to accumulate, replace, or extend partial responses as more tokens arrive

## Example
```python
import re

SENTENCE_END = re.compile(r'[.!?]\s')

async def yield_partials(stream):
    partial = ""
    async for token in stream:
        partial += token
        while True:
            match = SENTENCE_END.search(partial)
            if not match:
                break
            split_pos = match.end()
            yield partial[:split_pos]
            partial = partial[split_pos:]

    if partial:
        yield partial
```

## Target Models
GPT-4o, Claude 3.5 Sonnet, Gemini 2.0 Flash, Llama 3.2, Mistral Medium, Qwen 2.5 72B

## Success Rate
74% — Dependent on generation producing natural break points; structured output (JSON) is harder to yield partially without parsing errors.

## Related Methods
- M-07002: Early Termination
- M-07007: Stream Buffering
- M-07005: Chunk Analysis
