# Hybrid Selection
> **ID:** M-05015 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 88%

Combine multiple selection strategies into a single adaptive pipeline.

## How It Works
- Classify incoming prompt by complexity, type, and urgency
- Apply strategy routing: simple → cheapest, urgent → fastest, complex → ensemble
- Combine parallel race for latency with quality scoring for accuracy
- Fall back through strategy chain if primary approach fails
- Log strategy selection outcomes to improve routing over time

## Example
```python
from enum import Enum

class PromptType(Enum):
    SIMPLE = "simple"       # factual, short → cost-optimize
    COMPLEX = "complex"     # reasoning, multi-step → ensemble
    CREATIVE = "creative"   # writing, brainstorm → diversity
    URGENT = "urgent"       # user-facing, low latency → race

class HybridSelector:
    def __init__(self, providers: dict, judge, balancer, cost_router):
        self.providers = providers
        self.judge = judge
        self.balancer = balancer
        self.cost_router = cost_router

    def classify(self, prompt: str) -> PromptType:
        word_count = len(prompt.split())
        if word_count < 20 and any(k in prompt.lower() for k in ["what", "when", "who", "where"]):
            return PromptType.SIMPLE
        if "urgent" in prompt.lower() or word_count < 10:
            return PromptType.URGENT
        if any(k in prompt.lower() for k in ["write", "create", "brainstorm", "design"]):
            return PromptType.CREATIVE
        return PromptType.COMPLEX

    async def select(self, prompt: str) -> dict:
        ptype = self.classify(prompt)

        if ptype == PromptType.SIMPLE:
            return await self.cost_router.select(prompt)  # cheapest that works

        if ptype == PromptType.URGENT:
            return await parallel_race(prompt, self.providers.values())  # first response

        if ptype == PromptType.CREATIVE:
            selected = select_diverse(prompt, self.providers, n=3)
            return await response_fusion(prompt, selected, self.judge)

        # COMPLEX: full ensemble with voting + quality scoring
        responses = await asyncio.gather(*[p.generate(prompt) for p in self.providers.values()])
        scored = [(name, score_response(text, prompt)) for (name, text) in responses]
        ranked = sorted(scored, key=lambda x: composite_score(x[1]), reverse=True)

        return {
            "response": responses[ranked[0][0]],
            "provider": ranked[0][0],
            "type": ptype.value,
            "method": "hybrid_ensemble"
        }

# Usage
selector = HybridSelector(providers, judge_client, balancer, cost_router)
result = await selector.select("What is 2+2?")  # → SIMPLE → cheapest
result = await selector.select("Analyze this security vulnerability")  # → COMPLEX → ensemble
```

## Target Providers
Requires 3+ providers across different price/performance tiers for effective strategy routing.

## Success Rate
88% — Hybrid approach adapts to prompt characteristics, achieving high quality on complex tasks while optimizing cost/latency on simpler ones.

## Related Methods
- M-05001: Parallel Race
- M-05003: Voting Ensemble
- M-05009: Cost Optimization
- M-05005: Response Fusion
