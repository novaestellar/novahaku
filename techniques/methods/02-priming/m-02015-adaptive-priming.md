# Adaptive Priming
> **ID:** M-02015 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 74%

Dynamically adjust priming instructions based on the model's initial response, creating a feedback loop that refines output quality over multiple exchanges.

## How It Works
- Start with basic priming, then evaluate the model's response
- Identify specific shortcomings: "too verbose," "missing examples," "wrong depth"
- Issue corrective priming: "That was too high-level. Redo with concrete code examples"
- The model adapts to the corrective feedback and produces refined output
- Can be automated in multi-turn conversations or manual in single-shot with follow-up

## Example
```
Turn 1: "Explain Docker networking."
[Model gives textbook answer]

Turn 2: "Too generic. I specifically need: 1) how bridge networking differs from overlay, 
2) when to use host mode, 3) a real troubleshooting scenario. Include actual docker commands."
[Model produces focused, practical response]

Turn 3: "Better. Now add the performance implications of each mode for a Kubernetes 
cluster running 200+ pods."
[Model produces production-grade answer]
```

Each corrective turn primes more precisely than the original prompt could.

## Target Models
GPT-4 and Claude adapt well to mid-conversation correction. Claude retains corrective feedback more accurately across turns. Gemini handles it but sometimes reverts to original patterns.

## Success Rate
74% — Effective but requires 2-3 turns to reach optimal output. Single-correction refinement works ~85% of the time. Multiple corrections can confuse the model if instructions conflict.

## Related Methods
- M-02010: Multi-Turn Priming — establishes pattern; adaptive refines it
- M-02011: Chain Priming — each chain step can include adaptive correction
