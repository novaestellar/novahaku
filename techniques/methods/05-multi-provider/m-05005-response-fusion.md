# Response Fusion
> **ID:** M-05005 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 75%

Merge complementary information from multiple provider responses into a single superior answer.

## How It Works
- Query multiple providers with the same prompt
- Identify unique strengths in each response (different perspectives, facts, code examples)
- Use a fusion model to synthesize a combined response that includes best elements
- Deduplicate overlapping content and resolve contradictions
- Preserve attribution markers for traceability

## Example
```python
async def response_fusion(prompt: str, providers: dict[str, any], fusion_model) -> dict:
    responses = {}
    for name, client in providers.items():
        resp = await client.generate(prompt)
        responses[name] = resp.text

    fusion_prompt = f"""You are a synthesis engine. Merge the following {len(responses)} responses into ONE superior answer.

RULES:
1. Keep unique facts from each response — do not discard information
2. When sources conflict, prefer the more specific/detailed claim
3. Maintain coherent structure — group by topic, not by source
4. Preserve code examples from the most complete implementation

"""
    for name, text in responses.items():
        fusion_prompt += f"=== SOURCE: {name} ===\n{text}\n\n"

    fusion_prompt += "=== SYNTHESIZED OUTPUT ==="
    fused = await fusion_model.generate(fusion_prompt)

    return {"response": fused.text, "sources": list(responses.keys()), "method": "fusion"}

# Usage
result = await response_fusion(
    "Compare React Server Components vs traditional SSR",
    providers={"openai": oai, "anthropic": ant, "google": ggl},
    fusion_model=claude_client
)
```

## Target Providers
Most effective with 3+ providers with different training data (OpenAI, Anthropic, Google, Mistral, Cohere).

## Success Rate
75% — Fusion creates richer answers than any single provider; quality depends on the fusion model's ability to reconcile conflicting information.

## Related Methods
- M-05004: Best Response Selection
- M-05012: Diversity Sampling
- M-05003: Voting Ensemble
