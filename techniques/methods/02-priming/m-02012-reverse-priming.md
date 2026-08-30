# Reverse Priming
> **ID:** M-02012 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 84%

Show the desired output first (as an exemplar or partial completion), then ask the model to produce something matching that example.

## How It Works
- Provide a complete or partial example of the desired output before the actual request
- The model uses the example as a reference pattern to match
- More effective than describing the format — examples bypass ambiguity
- Works as few-shot learning: 1-3 examples dramatically improve output consistency
- The example primes style, depth, structure, and reasoning approach simultaneously

## Example
```
Here's how I want you to analyze code:

Example:
Input: def f(x): return x * 2 if x > 0 else x
Analysis: 
- Risk: No input validation; accepts any type (string * 2 repeats, not multiplies)
- Fix: Add type hint + guard: def f(x: int) -> int: if not isinstance(x, int): raise TypeError...
- Rating: Medium risk — works for ints, breaks for strings/lists

Now analyze:
Input: def parse(s): return eval(s)
```

The model will produce a structured analysis matching the example's format and depth.

## Target Models
GPT-4, Claude, Gemini all respond strongly to exemplar-based priming. More effective than instructions-only priming by 25-30% in benchmark studies.

## Success Rate
84% — One of the most reliable priming methods. Example quality directly determines output quality. A bad example produces a bad output that matches the bad pattern.

## Related Methods
- M-02001: Assistant Prefill — shows partial output rather than complete example
- M-02004: Format Priming — can use examples as format specification
