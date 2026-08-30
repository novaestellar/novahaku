# Expertise Priming
> **ID:** M-02008 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 83%

Signal the expected knowledge depth to push the model toward specialized, detailed responses rather than surface-level explanations.

## How It Works
- Explicitly state expertise level: "Assume I'm a senior engineer" or "Explain to a PhD physicist"
- Technical depth priming activates deeper training data associations
- Combine with domain specificity: "senior Kubernetes SRE" activates different knowledge than "senior developer"
- Use jargon freely in prompts — it signals the model should respond at the same level
- Counter-intuitive: asking for "beginner-level" sometimes constrains too much; prefer "explain simply but don't omit technical accuracy"

## Example
```
I'm a staff engineer at a distributed systems company. Don't explain basics.

Explain the linearizability vs serializability distinction in databases. 
Include edge cases, formal definitions, and real-world failure modes 
from systems like CockroachDB or Spanner. Reference the Herlihy & Wing paper.
```

The model produces a graduate-level technical discussion instead of a textbook overview.

## Target Models
GPT-4 and Claude respond strongly to expertise signals. Model responds to the "level" of the prompt's vocabulary. Gemini Pro handles technical priming well for STEM domains.

## Success Rate
83% — Strong for STEM and technical domains. Less effective for creative or subjective topics where expertise level is ambiguous.

## Related Methods
- M-02003: Role-Based Priming — role assignment implies expertise level
- M-02009: Constraint Priming — can constrain to "no simplification"
