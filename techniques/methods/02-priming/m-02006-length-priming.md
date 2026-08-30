# Length Priming
> **ID:** M-02006 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 87%

Control the approximate length of model responses by priming with explicit constraints or examples of the target length.

## How It Works
- State exact length targets: "in 3 sentences," "under 100 words," "one paragraph"
- Provide a length-matched example as the strongest form of length priming
- Combine with negative constraints: "Do not exceed 5 sentences"
- For longer outputs, specify section counts: "3 sections, each 2-3 paragraphs"
- Models tend toward verbose defaults — length priming counteracts this bias

## Example
```
Explain what a REST API is. 

Constraints:
- Exactly 3 sentences
- First sentence: definition
- Second sentence: how it works  
- Third sentence: real-world example
- Total: under 60 words
```

The model produces a tight, focused explanation instead of a 500-word essay.

## Target Models
All models. GPT-4 and Claude follow length constraints well. Open-source models often overshoot — use stricter phrasing ("exactly N sentences" beats "about N sentences").

## Success Rate
87% — Effective for short outputs (1-5 sentences). Less reliable for precise word counts. Best paired with structural constraints (sentence roles) alongside length limits.

## Related Methods
- M-02004: Format Priming — structure + length together
- M-02010: Multi-Turn Priming — can enforce length across turns
