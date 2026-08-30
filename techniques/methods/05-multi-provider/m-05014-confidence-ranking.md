# Confidence Ranking
> **ID:** M-05014 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 79%

Rank provider responses by self-reported or estimated confidence scores.

## How It Works
- Request providers to include confidence scores with responses (prompt-based or logprobs)
- For providers without logprobs: use prompt-engineered confidence estimation
- Normalize confidence scores across providers to comparable scale
- Rank responses by confidence and select highest
- Apply confidence threshold — reject responses below minimum confidence

## Example
```python
CONFIDENCE_PROMPT = """Answer the following question. After your answer, provide a confidence score from 0-100% on a new line in the format: CONFIDENCE: XX%

Question: {prompt}"""

async def confidence_rank(prompt: str, providers: dict[str, any], min_confidence: int = 70) -> dict:
    results = []
    for name, client in providers.items():
        resp = await client.generate(CONFIDENCE_PROMPT.format(prompt=prompt))
        text = resp.text

        # Extract confidence from response
        import re
        match = re.search(r'CONFIDENCE:\s*(\d+)%', text)
        confidence = int(match.group(1)) if match else 50  # default 50 if not found
        answer = re.sub(r'CONFIDENCE:\s*\d+%', '', text).strip()

        # Normalize confidence by provider baseline calibration
        calibration = PROVIDER_CALIBRATION.get(name, 1.0)
        adjusted = min(confidence * calibration, 100)

        results.append({
            "provider": name,
            "answer": answer,
            "raw_confidence": confidence,
            "adjusted_confidence": adjusted
        })

    results.sort(key=lambda x: x["adjusted_confidence"], reverse=True)

    if results[0]["adjusted_confidence"] < min_confidence:
        return {"response": None, "warning": "Below confidence threshold", "results": results}

    return {"response": results[0]["answer"], "provider": results[0]["provider"],
            "confidence": results[0]["adjusted_confidence"], "all_rankings": results}

PROVIDER_CALIBRATION = {"openai": 0.95, "anthropic": 1.05, "google": 0.90}

# Usage
result = await confidence_rank(
    "What year was Python first released?",
    providers={"openai": oai, "anthropic": ant, "google": ggl}
)
```

## Target Providers
Works with any provider; logprobs-based confidence (OpenAI, Cohere) is more reliable than prompt-engineered estimates.

## Success Rate
79% — Confidence calibration improves with historical data; prompt-based confidence is moderately reliable, logprobs-based is highly reliable.

## Related Methods
- M-05004: Best Response Selection
- M-05010: Quality Scoring
- M-05013: Adversarial Selection
