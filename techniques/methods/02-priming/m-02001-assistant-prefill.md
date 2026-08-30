# Assistant Prefill
> **ID:** M-02001 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 92%

Pre-fill the assistant message with the beginning of a desired response to steer the model toward completing it in a specific direction, format, or style.

## How It Works
- Send a partial assistant response as the first tokens of the completion
- The model treats the pre-filled text as its own prior output and continues from there
- Works because language models are conditioned to maintain coherence with prior tokens
- Effective for forcing specific opening phrases, structures, or reasoning patterns
- Most APIs support this via the `assistant` role message with partial content

## Example
```
User: Explain quantum entanglement.

Assistant prefill: "Quantum entachlument is a phenomenon where two particles become correlated such that the quantum state of one instantly influences the other, regardless of distance. Here's a step-by-step breakdown:"
```

The model will continue with a structured breakdown rather than a freeform essay.

## Target Models
GPT-4, GPT-4o, Claude 3.x, Gemini Pro, Llama 3 (via API), Mistral — any model exposing chat completion API with assistant role.

## Success Rate
92% — Very reliable. The model strongly anchors to pre-filled content. Risk: if pre-fill contradicts the prompt, output becomes incoherent.

## Related Methods
- M-02002: System Prompt Priming — primes via system message instead of assistant pre-fill
- M-02012: Reverse Priming — shows desired output first as exemplar
