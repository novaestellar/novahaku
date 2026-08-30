# Sequential Fallback
> **ID:** M-05002 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 92%

Try providers in a priority-ordered list, falling through to the next on failure.

## How It Works
- Define a ranked provider list based on preference, cost, or quality
- Attempt the highest-ranked provider first
- On error (timeout, 429, 500, 503), log failure and move to next provider
- Track failure reasons per provider for dynamic reordering
- Return first successful response or raise aggregate error if all fail

## Example
```python
class SequentialFallback:
    def __init__(self, providers: list[tuple[str, any]]):
        self.providers = providers  # [(name, client), ...]
        self.failure_counts: dict[str, int] = {}

    def generate(self, prompt: str) -> dict:
        errors = []
        for name, client in self.providers:
            try:
                response = client.generate(prompt, timeout=10)
                self.failure_counts[name] = 0
                return {"response": response, "provider": name}
            except Exception as e:
                self.failure_counts[name] = self.failure_counts.get(name, 0) + 1
                errors.append({"provider": name, "error": str(e)})
        raise RuntimeError(f"All providers failed: {errors}")

# Usage — cheapest first, escalate to premium
router = SequentialFallback([
    ("deepseek", deepseek_client),
    ("mistral", mistral_client),
    ("openai", openai_client),
    ("anthropic", anthropic_client),
])
result = router.generate("Summarize this document")
```

## Target Providers
Any provider with standard error responses; works best with OpenAI-compatible APIs that return 429/500/503.

## Success Rate
92% — Extremely reliable as long as at least one provider in the fallback chain is operational; the ranked order ensures cost-efficient attempts first.

## Related Methods
- M-05001: Parallel Race
- M-05006: Provider Rotation
- M-05009: Cost Optimization
