# Researcher Mode
> **ID:** M-03007 | **Category:** Identity Configuration | **Tier:** Basic | **Rate:** 76%

Activates a research-oriented response profile that prioritizes analytical depth, evidence-based reasoning, and systematic exploration of questions.

## How It Works
- Frames the model as a research analyst or academic researcher
- Shifts output toward structured analysis, hypothesis formation, and evidence evaluation
- Increases citation likelihood (though hallucinated references remain a known issue)
- Encourages multi-perspective examination of topics
- Can be domain-specific ("medical researcher", "security researcher") for deeper activation

## Example
```
You are a security researcher analyzing attack vectors. Approach every question systematically: 1) Define the threat model. 2) Enumerate attack surfaces. 3) Assess feasibility with evidence. 4) Recommend mitigations ranked by cost-effectiveness. Use CVE references where applicable.
```

## Target Models
GPT-4, GPT-4o, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro

## Success Rate
76% — Effective for analytical tasks; model tends to over-generate citations that may be fabricated. Combining with real-time search grounding improves accuracy significantly.

## Related Methods
- M-03003: Expert Mode
- M-03009: Consultant Mode
- M-03008: Instructor Mode
