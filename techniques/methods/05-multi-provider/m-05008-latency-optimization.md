# Latency Optimization
> **ID:** M-05008 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 86%

Route requests to providers and configurations that minimize end-to-end response latency.

## How It Works
- Maintain rolling p50/p95 latency stats per provider per region
- Prefer providers with lowest p95 latency for latency-sensitive requests
- Use streaming responses to reduce time-to-first-token (TTFT)
- Select smaller/faster models when response quality threshold is met
- Implement connection pooling and persistent sessions to reduce cold-start overhead

## Example
```python
import statistics
from collections import defaultdict

class LatencyRouter:
    def __init__(self):
        self.latencies: dict[str, list[float]] = defaultdict(list)
        self.max_samples = 100

    def record_latency(self, provider: str, ms: float):
        self.latencies[provider].append(ms)
        if len(self.latencies[provider]) > self.max_samples:
            self.latencies[provider].pop(0)

    def select_fastest(self, providers: dict, max_p95_ms: float = 3000) -> tuple[str, any]:
        candidates = []
        for name, client in providers.items():
            samples = self.latencies.get(name, [])
            if len(samples) < 5:
                candidates.append((name, client, 9999))  # unknown = low priority
                continue
            p95 = sorted(samples)[int(len(samples) * 0.95)]
            if p95 <= max_p95_ms:
                candidates.append((name, client, p95))
        if not candidates:
            # Fallback: pick any available
            name = next(iter(providers))
            return name, providers[name]
        candidates.sort(key=lambda x: x[2])
        return candidates[0][0], candidates[0][1]

# Usage
router = LatencyRouter()
# After collecting latency data from previous calls:
name, client = router.select_fastest(
    {"openai": oai, "mistral": mistral, "deepseek": ds},
    max_p95_ms=2000
)
```

## Target Providers
Most impactful with geographically distributed providers (OpenAI US/EU, Google global, Mistral EU).

## Success Rate
86% — Latency-aware routing reduces p95 response times by 30-50% compared to static routing; effectiveness depends on measurement sample size.

## Related Methods
- M-05001: Parallel Race
- M-05007: Load Balancing
- M-05009: Cost Optimization
