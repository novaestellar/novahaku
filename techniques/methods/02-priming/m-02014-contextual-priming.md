# Contextual Priming
> **ID:** M-02014 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 81%

Provide relevant background context before the actual request to anchor the model's response in a specific situation, domain, or state of knowledge.

## How It Works
- Supply background information that the model should treat as established fact
- Context can include: project details, previous decisions, constraints, stakeholder info
- The model adjusts its response to be consistent with the provided context
- More effective than implicit context — explicitly stated facts are weighted more heavily
- Use "Given that..." or "Context:" blocks to separate priming context from the request

## Example
```
Context:
- Our startup has 3 engineers, 6 months to launch
- Tech stack: React + Python FastAPI + PostgreSQL on AWS
- No ML/AI expertise on the team
- We're building a B2B invoice processing tool
- Current pain: manual data entry from PDF invoices

Question: Should we build our own PDF parser or use a third-party service?

Ignore any advice about hiring more engineers — that's not an option right now.
```

The model responds with budget-aware, team-size-appropriate advice rather than suggesting an enterprise solution.

## Target Models
All models. Claude integrates context most naturally. GPT-4 sometimes ignores contextual constraints if they conflict with "optimal" advice. Be explicit about which context is binding.

## Success Rate
81% — Effective when context is clearly stated and relevant. Reduces generic advice by ~40%. Context overload (>500 words of background) can cause the model to lose the actual question.

## Related Methods
- M-02009: Constraint Priming — constraints derived from context
- M-02013: Conditional Priming — context-based branching
