# Quality Scoring
> **ID:** M-05010 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 80%

Score and rank provider responses using automated quality metrics before selection.

## How It Works
- Define quality dimensions: factual accuracy, completeness, coherence, format compliance
- Run automated checks per dimension (regex for format, keyword overlap for accuracy)
- Compute weighted composite score across all dimensions
- Cache provider quality profiles to avoid re-scoring identical prompt patterns
- Select highest-scoring response or threshold-gate responses for human review

## Example
```python
from dataclasses import dataclass

@dataclass
class QualityDimensions:
    accuracy: float = 0.0     # keyword/claim overlap with reference
    completeness: float = 0.0 # coverage of expected topics
    coherence: float = 0.0    # readability metrics
    format: float = 0.0       # output format compliance

WEIGHTS = {"accuracy": 0.4, "completeness": 0.3, "coherence": 0.2, "format": 0.1}

def score_response(response: str, prompt: str, reference: str = None) -> QualityDimensions:
    scores = QualityDimensions()

    # Accuracy: overlap with reference or prompt keywords
    if reference:
        ref_words = set(reference.lower().split())
        resp_words = set(response.lower().split())
        scores.accuracy = len(ref_words & resp_words) / max(len(ref_words), 1)

    # Completeness: response length relative to expected
    expected_len = len(prompt.split()) * 5  # rough heuristic
    scores.completeness = min(len(response.split()) / max(expected_len, 1), 1.0)

    # Coherence: sentence structure quality
    sentences = [s.strip() for s in response.split('.') if s.strip()]
    avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    scores.coherence = min(avg_len / 20, 1.0)  # 20 words/sentence is ideal

    # Format: basic structure checks
    scores.format = 1.0 if len(response) > 50 else len(response) / 50

    return scores

def composite_score(dims: QualityDimensions) -> float:
    return sum(getattr(dims, k) * v for k, v in WEIGHTS.items())

# Usage
responses = {"openai": resp_oai, "anthropic": resp_ant, "mistral": resp_mist}
ranked = sorted(
    responses.items(),
    key=lambda x: composite_score(score_response(x[1], prompt)),
    reverse=True
)
best_provider, best_response = ranked[0]
```

## Target Providers
Any provider; scoring is provider-agnostic and works with raw text output.

## Success Rate
80% — Automated scoring catches format and completeness issues reliably; accuracy scoring benefits from reference data or ground-truth anchoring.

## Related Methods
- M-05004: Best Response Selection
- M-05014: Confidence Ranking
- M-05009: Cost Optimization
