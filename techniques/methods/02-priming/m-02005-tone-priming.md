# Tone Priming
> **ID:** M-02005 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 82%

Set the emotional register, formality level, and stylistic voice before the model generates content.

## How It Works
- Explicitly name the desired tone: "academic," "conversational," "urgent," "diplomatic"
- Provide a short tone exemplar — one sentence in the target tone is more effective than describing it
- Combine tone with audience: "explain to a 10-year-old" implicitly sets tone + complexity
- Tone priming interacts with role priming — a "legal advisor" role already implies formal tone
- Some tones conflict: "casual" + "academic rigor" needs explicit prioritization

## Example
```
Write the following in a warm, encouraging tone for a developer who just 
failed their first coding interview:

"It's normal to feel discouraged. Here's what actually matters..."

Tone: empathetic, not patronizing. Practical advice wrapped in encouragement.
No toxic positivity. Acknowledge the disappointment honestly first.
```

The model produces genuine encouragement rather than generic "you'll do great!" platitudes.

## Target Models
Claude excels at tone adaptation. GPT-4 responds well to explicit tone labels. Open-source models benefit more from exemplar sentences than tone keywords.

## Success Rate
82% — Good for obvious tones (formal, casual, technical). Struggles with nuanced tonal blends. Exemplar-based priming outperforms keyword-based by ~15%.

## Related Methods
- M-02003: Role-Based Priming — role choice implicitly sets tone
- M-02014: Contextual Priming — adjusts tone based on conversation context
