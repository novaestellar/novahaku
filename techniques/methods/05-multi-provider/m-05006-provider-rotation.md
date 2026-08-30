# Provider Rotation
> **ID:** M-05006 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 88%

Systematically rotate through providers using round-robin, weighted, or adaptive algorithms.

## How It Works
- Maintain a provider pool with health status and performance metrics
- Cycle through providers in round-robin fashion for even distribution
- Weight rotation by provider reliability scores (higher weight = more requests)
- Skip unhealthy providers detected via error rate monitoring
- Re-introduce recovered providers after cooldown period

## Example
```python
import itertools
from dataclasses import dataclass, field

@dataclass
class ProviderPool:
    providers: dict[str, any]
    weights: dict[str, float] = field(default_factory=dict)
    error_counts: dict[str, int] = field(default_factory=dict)
    cooldown_until: dict[str, float] = field(default_factory=dict)

    def get_next(self) -> tuple[str, any]:
        now = time.time()
        available = {
            name: client for name, client in self.providers.items()
            if self.cooldown_until.get(name, 0) < now
            and self.error_counts.get(name, 0) < 5
        }
        if not available:
            self._reset_cooldowns()
            available = self.providers

        total_weight = sum(self.weights.get(n, 1.0) for n in available)
        r = random.uniform(0, total_weight)
        cumulative = 0
        for name, client in available.items():
            cumulative += self.weights.get(name, 1.0)
            if r <= cumulative:
                return name, client
        return next(iter(available.items()))

    def record_success(self, name: str):
        self.error_counts[name] = 0
        self.weights[name] = min(self.weights.get(name, 1.0) + 0.1, 3.0)

    def record_failure(self, name: str):
        self.error_counts[name] = self.error_counts.get(name, 0) + 1
        if self.error_counts[name] >= 5:
            self.cooldown_until[name] = time.time() + 60
        self.weights[name] = max(self.weights.get(name, 1.0) - 0.2, 0.1)

# Usage
pool = ProviderPool(
    providers={"openai": oai, "anthropic": ant, "mistral": mistral},
    weights={"openai": 1.5, "anthropic": 1.2, "mistral": 1.0}
)
name, client = pool.get_next()
```

## Target Providers
Works with any pool of 2+ providers; best when providers have similar capabilities but different rate limits.

## Success Rate
88% — Rotation prevents single-provider burnout and distributes load; adaptive weighting improves over time as provider performance data accumulates.

## Related Methods
- M-05007: Load Balancing
- M-05002: Sequential Fallback
- M-05009: Cost Optimization
