# Parallel Race
> **ID:** M-05001 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 85%

Fire requests to multiple providers simultaneously and accept the first valid response that returns.

## How It Works
- Dispatch identical prompts to N providers concurrently via async/threading
- First provider to return a non-error response wins
- Cancel remaining requests after winner is selected
- Apply timeout threshold (e.g., 5s) to avoid hanging on slow providers
- Log which provider won for latency profiling and future routing

## Example
```python
import asyncio
from typing import Any

async def parallel_race(prompt: str, providers: list, timeout: float = 5.0) -> dict:
    async def call_provider(provider):
        return await provider.generate(prompt, timeout=timeout)

    tasks = [call_provider(p) for p in providers]
    done, pending = await asyncio.wait(
        tasks, timeout=timeout, return_when=asyncio.FIRST_COMPLETED
    )
    for task in pending:
        task.cancel()
    if done:
        result = next(iter(done)).result()
        return {"response": result.text, "provider": result.provider_name}
    raise TimeoutError("All providers exceeded timeout")

# Usage
providers = [openai_client, anthropic_client, google_client]
winner = await parallel_race("Explain quantum computing", providers)
```

## Target Providers
OpenAI, Anthropic, Google Gemini, Mistral, Cohere, any OpenAI-compatible endpoint

## Success Rate
85% — Race succeeds when at least one provider responds within timeout; fails only if all providers are down or rate-limited simultaneously.

## Related Methods
- M-05002: Sequential Fallback
- M-05008: Latency Optimization
- M-05007: Load Balancing
