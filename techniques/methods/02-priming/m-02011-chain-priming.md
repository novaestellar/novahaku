# Chain Priming
> **ID:** M-02011 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 78%

Sequence multiple priming steps in a deliberate order where each step's output becomes the context for the next, building toward a complex result.

## How It Works
- Break the task into sequential stages: define → analyze → decide → execute
- Each stage receives the output of the previous stage as priming context
- The chain creates a "cognitive scaffolding" effect where each step narrows the solution space
- Works because models perform better on decomposed tasks than monolithic ones
- Prevents hallucination by constraining each step to one focused operation

## Example
```
Step 1: List 5 common Python web frameworks. [Model lists: Flask, Django, FastAPI, Starlette, Tornado]
Step 2: Of these 5, which have native async support? [Model filters to: FastAPI, Starlette, Tornado]
Step 3: Compare these 3 on performance benchmarks and ecosystem maturity. [Model provides comparison]
Step 4: Based on your analysis, recommend one for a real-time chat API. [Model picks FastAPI with reasoning]
```

Each step primes the model with verified context, preventing it from making unfounded assumptions.

## Target Models
All models. Works best with GPT-4 and Claude which maintain accuracy across chained steps. Requires clear step numbering. Some open-source models lose context after 3+ chains.

## Success Rate
78% — Effective for complex reasoning tasks. Accuracy per step is ~90%, but errors compound across chains. Limit to 4-5 steps maximum.

## Related Methods
- M-02010: Multi-Turn Priming — simpler form using conversation turns
- M-02014: Contextual Priming — provides context for each chain step
