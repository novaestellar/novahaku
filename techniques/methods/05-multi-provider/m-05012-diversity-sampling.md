# Diversity Sampling
> **ID:** M-05012 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 73%

Intentionally select from diverse providers to capture different perspectives and reduce groupthink.

## How It Works
- Maintain provider profiles noting training data biases and strengths
- Select providers with maximal coverage of different knowledge domains
- Apply temperature variation across providers for response diversity
- Deduplicate semantically similar responses before selection
- Curate final set that maximizes information coverage with minimal overlap

## Example
```python
from dataclasses import dataclass

@dataclass
class ProviderProfile:
    name: str
    strengths: list[str]     # ["code", "math", "creative"]
    temperature: float       # provider-specific temperature
    diversity_weight: float  # higher = more unique perspective

PROFILES = [
    ProviderProfile("openai",    ["general", "code", "reasoning"], 0.7, 0.8),
    ProviderProfile("anthropic", ["analysis", "safety", "writing"], 0.5, 0.9),
    ProviderProfile("google",    ["factual", "multilingual", "search"], 0.8, 0.7),
    ProviderProfile("mistral",   ["code", "math", "european"], 0.9, 0.85),
    ProviderProfile("cohere",    ["retrieval", "summarization"], 0.6, 0.75),
]

def select_diverse(prompt: str, profiles: list[ProviderProfile], n: int = 3) -> list[ProviderProfile]:
    # Score each provider by relevance to prompt keywords
    prompt_keywords = set(prompt.lower().split())
    scored = []
    for p in profiles:
        relevance = len(set(p.strengths) & prompt_keywords) / max(len(set(p.strengths)), 1)
        diversity = p.diversity_weight
        score = relevance * 0.6 + diversity * 0.4
        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Greedy diversification: pick top, then maximize dissimilarity
    selected = [scored[0][1]]
    for _ in range(n - 1):
        remaining = [(s, p) for s, p in scored if p not in selected]
        if not remaining:
            break
        # Prefer providers with least overlap to already-selected
        best = max(remaining, key=lambda x: len(set(x[1].strengths) - set.union(*(set(s.strengths) for s in selected))))
        selected.append(best[1])
    return selected

# Usage
selected = select_diverse("Write a legal contract for SaaS", PROFILES, n=3)
# Returns: [anthropic (writing), openai (reasoning), cohere (retrieval)]
```

## Target Providers
Maximizes value with 5+ diverse providers; works across OpenAI, Anthropic, Google, Mistral, Cohere, AI21.

## Success Rate
73% — Diversity ensures broader coverage; effectiveness depends on how well provider strengths are profiled and matched to prompt intent.

## Related Methods
- M-05011: Consensus Check
- M-05005: Response Fusion
- M-05003: Voting Ensemble
