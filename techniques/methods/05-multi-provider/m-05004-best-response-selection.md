# Best Response Selection
> **ID:** M-05004 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 82%

Query multiple providers and use a judge model to select the single best response.

## How It Works
- Send prompt to N providers in parallel
- Collect all responses with metadata (latency, token count, provider name)
- Pass responses to a dedicated judge model with scoring criteria
- Judge evaluates on relevance, accuracy, completeness, and clarity
- Return the highest-scored response with judge reasoning

## Example
```python
CRITERIA = "Score each response 1-10 on: accuracy, completeness, clarity, reasoning quality"

async def best_response(prompt: str, providers: dict, judge) -> dict:
    responses = {}
    for name, client in providers.items():
        resp = await client.generate(prompt)
        responses[name] = resp.text

    judge_prompt = f"""{CRITERIA}

Prompt: {prompt}

"""
    for name, text in responses.items():
        judge_prompt += f"--- Response from {name} ---\n{text}\n\n"

    judge_prompt += """Return JSON: {"best_provider": "...", "scores": {"provider": score}, "reasoning": "..."}"""

    judgment = await judge.generate(judge_prompt, response_format="json")
    result = json.loads(judgment.text)

    return {
        "response": responses[result["best_provider"]],
        "provider": result["best_provider"],
        "scores": result["scores"],
        "reasoning": result["reasoning"]
    }

# Usage
result = await best_response(
    "Write a Python function to merge sorted arrays",
    providers={"openai": oai, "anthropic": ant, "deepseek": ds},
    judge=anthropic_client
)
```

## Target Providers
Works with any set of providers; judge should be a high-quality model (Claude, GPT-4) for reliable scoring.

## Success Rate
82% — Judge-based selection consistently picks higher-quality outputs; overhead is the judge call latency and cost.

## Related Methods
- M-05003: Voting Ensemble
- M-05010: Quality Scoring
- M-05014: Confidence Ranking
