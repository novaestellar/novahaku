# Adversarial Selection
> **ID:** M-05013 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 70%

Select responses by stress-testing them against adversarial validation prompts.

## How It Works
- Generate candidate responses from multiple providers
- Automatically generate adversarial follow-ups targeting each response's weaknesses
- Score responses based on how well they withstand adversarial probing
- Select response that best survives challenge rounds
- Useful for safety-critical or high-stakes content generation

## Example
```python
ADVERSARIAL_PROMPTS = [
    "Is this claim factually correct? Challenge it.",
    "Find logical flaws in this argument.",
    "What important context is missing from this response?",
    "Is this response potentially misleading? How?",
]

async def adversarial_select(prompt: str, providers: dict[str, any], judge) -> dict:
    candidates = {}
    for name, client in providers.items():
        resp = await client.generate(prompt)
        candidates[name] = resp.text

    scores = {name: 100 for name in candidates}  # start at 100, deduct for flaws

    for name, text in candidates.items():
        for adv_prompt in ADVERSARIAL_PROMPTS:
            challenge = f"Response to evaluate: {text}\n\n{adv_prompt}"
            critique = await judge.generate(challenge)
            flaw_count = critique.text.lower().count("flaw") + critique.text.lower().count("issue")
            scores[name] -= flaw_count * 5  # deduct 5 points per flaw found

    best = max(scores, key=scores.get)
    return {
        "response": candidates[best],
        "provider": best,
        "scores": scores,
        "method": "adversarial_selection"
    }

# Usage
result = await adversarial_select(
    "Explain the safety of mRNA vaccines",
    providers={"openai": oai, "anthropic": ant, "google": ggl},
    judge=anthropic_client
)
```

## Target Providers
Works best with high-capability models as both candidates and judge (GPT-4, Claude Sonnet/Opus).

## Success Rate
70% — Adversarial filtering catches hallucinations and weak reasoning; overhead is significant (N×M API calls) but justified for high-stakes outputs.

## Related Methods
- M-05004: Best Response Selection
- M-05014: Confidence Ranking
- M-05011: Consensus Check
