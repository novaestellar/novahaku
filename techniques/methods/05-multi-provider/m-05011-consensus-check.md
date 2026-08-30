# Consensus Check
> **ID:** M-05011 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 76%

Verify response reliability by checking agreement across multiple independent providers.

## How It Works
- Query 3+ providers with the same factual prompt
- Normalize responses to comparable format (extract key claims, values, or classifications)
- Measure pairwise agreement using semantic similarity or exact match
- High consensus (≥2/3 agreement) → accept with confidence
- Low consensus → flag for escalation, retry with refined prompt, or request human review

## Example
```python
from collections import Counter
import re

async def consensus_check(prompt: str, providers: dict[str, any], threshold: float = 0.66) -> dict:
    responses = {}
    for name, client in providers.items():
        resp = await client.generate(prompt)
        responses[name] = resp.text

    # Extract key claims (simplified: split into sentences, normalize)
    def extract_claims(text: str) -> set[str]:
        sentences = [s.strip().lower() for s in re.split(r'[.!?]', text) if s.strip()]
        return set(sentences)

    claim_sets = {name: extract_claims(text) for name, text in responses.items()}

    # Pairwise Jaccard similarity
    names = list(claim_sets.keys())
    agreements = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = claim_sets[names[i]], claim_sets[names[j]]
            if a or b:
                agreements.append(len(a & b) / len(a | b))

    avg_consensus = sum(agreements) / max(len(agreements), 1)

    # Find most common response cluster
    all_claims = []
    for claims in claim_sets.values():
        all_claims.extend(list(claims)[:3])
    common = Counter(all_claims).most_common(1)

    return {
        "consensus_score": avg_consensus,
        "agrees": avg_consensus >= threshold,
        "dominant_claim": common[0][0] if common else None,
        "responses": responses
    }

# Usage
result = await consensus_check(
    "What is the capital of France?",
    providers={"openai": oai, "anthropic": ant, "google": ggl}
)
# consensus_score: 0.95 → high confidence
```

## Target Providers
Requires 3+ independent providers for meaningful consensus; works best with diverse training data.

## Success Rate
76% — Strong for factual verification; less effective for subjective or creative tasks where disagreement is expected and valid.

## Related Methods
- M-05003: Voting Ensemble
- M-05012: Diversity Sampling
- M-05005: Response Fusion
