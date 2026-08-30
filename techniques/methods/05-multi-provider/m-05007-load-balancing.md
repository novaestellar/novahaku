# Load Balancing
> **ID:** M-05007 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 90%

Distribute requests across providers proportional to their capacity and rate limits.

## How It Works
- Track per-provider metrics: RPM, TPM, error rate, p95 latency
- Calculate available capacity as (max_limit - current_usage) for each provider
- Route new requests to provider with highest available capacity
- Implement token bucket or sliding window rate limiting per provider
- Auto-adjust distribution when providers hit rate limits or degrade

## Example
```python
from collections import deque
import time

class LoadBalancer:
    def __init__(self, providers: dict[str, dict]):
        self.providers = providers  # {name: {"client": ..., "rpm_limit": 60, "requests": deque}}
        self.window = 60  # 1-minute sliding window

    def _current_rpm(self, name: str) -> int:
        now = time.time()
        reqs = self.providers[name]["requests"]
        while reqs and reqs[0] < now - self.window:
            reqs.popleft()
        return len(reqs)

    def select_provider(self) -> tuple[str, any]:
        best_name, best_capacity = None, -1
        for name, cfg in self.providers.items():
            current = self._current_rpm(name)
            capacity = cfg["rpm_limit"] - current
            error_rate = cfg.get("error_rate", 0)
            adjusted = capacity * (1 - error_rate)
            if adjusted > best_capacity:
                best_capacity = adjusted
                best_name = name
        if best_name is None:
            raise RuntimeError("All providers at capacity")
        return best_name, self.providers[best_name]["client"]

    def record_request(self, name: str, success: bool):
        self.providers[name]["requests"].append(time.time())
        # Exponential moving average for error rate
        er = self.providers[name].get("error_rate", 0)
        self.providers[name]["error_rate"] = er * 0.9 + (0.1 if not success else 0)

# Usage
balancer = LoadBalancer({
    "openai":    {"client": oai,    "rpm_limit": 500, "requests": deque()},
    "anthropic": {"client": ant,    "rpm_limit": 200, "requests": deque()},
    "mistral":   {"client": mist,   "rpm_limit": 100, "requests": deque()},
})
name, client = balancer.select_provider()
```

## Target Providers
Any provider with published or estimable rate limits; especially useful for OpenAI (TPM/RPM), Anthropic (RPD), and Google (RPM).

## Success Rate
90% — Prevents 429 errors by distributing load intelligently; maintains high throughput even under heavy request volume.

## Related Methods
- M-05006: Provider Rotation
- M-05008: Latency Optimization
- M-05001: Parallel Race
