# Voting Ensemble
> **ID:** M-05003 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 78%

Collect responses from multiple providers and select via majority vote or weighted voting.

## How It Works
- Send the same prompt to 3+ providers simultaneously
- Parse responses into comparable format (structured output or classification)
- Apply majority vote for classification tasks, or weighted vote based on provider reliability
- For generation tasks, use an LLM-as-judge to pick the consensus answer
- Tie-breaking uses pre-defined provider priority order

## Example
```python
async def voting_ensemble(prompt: str, providers: dict[str, any], weights: dict[str, float] = None) -> dict:
    responses = await asyncio.gather(*[p.generate(prompt) for p in providers.values()])

    if is_classification_task(prompt):
        votes: dict[str, float] = {}
        for (name, resp), weight in zip(responses, weights.values()):
            label = extract_label(resp.text)
            votes[label] = votes.get(label, 0) + weight
        winner = max(votes, key=votes.get)
        return {"response": winner, "votes": votes, "method": "majority_vote"}

    # For generation: use judge model to select best
    judge_prompt = f"Given these {len(responses)} answers, pick the most accurate:\n"
    for name, resp in responses:
        judge_prompt += f"[{name}]: {resp.text}\n"
    judge_result = await judge_provider.generate(judge_prompt)
    return {"response": judge_result.text, "method": "llm_judge"}

# Usage
result = await voting_ensemble(
    "Is Python statically typed?",
    providers={"openai": oai, "anthropic": ant, "google": ggl},
    weights={"openai": 0.4, "anthropic": 0.35, "google": 0.25}
)
```

## Target Providers
Best with 3+ diverse providers (OpenAI, Anthropic, Google, Mistral) to maximize vote diversity.

## Success Rate
78% — Voting reduces individual provider errors; effectiveness depends on provider independence and task type. Classification tasks vote higher (~90%), generation tasks lower (~70%).

## Related Methods
- M-05004: Best Response Selection
- M-05011: Consensus Check
- M-05012: Diversity Sampling
