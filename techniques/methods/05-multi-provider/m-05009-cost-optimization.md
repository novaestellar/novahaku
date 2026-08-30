# Cost Optimization
> **ID:** M-05009 | **Category:** Multi-Provider Selection | **Tier:** Advanced | **Rate:** 91%

Minimize total API cost by routing to the cheapest provider that meets quality requirements.

## How It Works
- Maintain a cost table: price_per_1k_input and price_per_1k_output per provider/model
- Set a quality floor — only consider providers that meet minimum quality threshold
- Route to cheapest qualifying provider for each request
- Apply budget caps and alert when spending approaches limits
- Track cumulative cost per session/user/project for spend visibility

## Example
```python
@dataclass
class ModelPricing:
    name: str
    input_per_1k: float   # USD per 1K input tokens
    output_per_1k: float  # USD per 1K output tokens
    quality_score: float  # 0-1 from benchmark evaluation

COST_TABLE = [
    ModelPricing("deepseek-v3",     0.00027, 0.00110, 0.82),
    ModelPricing("mistral-small",   0.00020, 0.00060, 0.78),
    ModelPricing("gpt-4o-mini",     0.00015, 0.00060, 0.80),
    ModelPricing("claude-haiku",    0.00025, 0.00125, 0.85),
    ModelPricing("gpt-4o",          0.00250, 0.01000, 0.93),
    ModelPricing("claude-sonnet",   0.00300, 0.01500, 0.95),
]

def select_cheapest(input_tokens: int, output_tokens: int, quality_min: float = 0.75) -> ModelPricing:
    candidates = [m for m in COST_TABLE if m.quality_score >= quality_min]
    def estimate_cost(m: ModelPricing) -> float:
        return (input_tokens / 1000 * m.input_per_1k) + (output_tokens / 1000 * m.output_per_1k)
    return min(candidates, key=estimate_cost)

# Usage — 2K input, 500 output tokens, need decent quality
best = select_cheapest(input_tokens=2000, output_tokens=500, quality_min=0.75)
# Returns: gpt-4o-mini at $0.00060 total vs gpt-4o at $0.010
```

## Target Providers
Any provider with published pricing; especially effective with tiered model offerings (GPT-4o-mini vs GPT-4o, Haiku vs Sonnet).

## Success Rate
91% — Cost savings of 60-80% achievable by routing simple tasks to cheaper models; quality floor prevents degradation on complex prompts.

## Related Methods
- M-05006: Provider Rotation
- M-05010: Quality Scoring
- M-05002: Sequential Fallback
