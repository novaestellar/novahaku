# Role-Based Priming
> **ID:** M-02003 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 85%

Assign a specific expert role or persona to the model to activate domain-specific knowledge patterns and response conventions.

## How It Works
- Begin prompts with "You are [specific role]" to anchor the model's behavioral space
- More specific roles produce better results: "senior Go engineer at a fintech startup" > "programmer"
- The role primes vocabulary, depth, assumptions, and reasoning patterns
- Combine role with experience level for finer control: "20-year veteran," "junior developer"
- Roles activate latent training data associated with that persona

## Example
```
You are a principal database architect at a high-traffic SaaS company handling 50M queries/day. 
You've spent 15 years optimizing PostgreSQL. A junior developer asks:

"Why is my JOIN query slow on a table with 100M rows?"

Give advice as if mentoring them — practical, specific, with PostgreSQL EXPLAIN plans.
```

The model responds with database-specific expertise, practical indexing advice, and mentor-like tone.

## Target Models
All chat-capable models. Effectiveness varies: Claude and GPT-4 respond strongly to role priming. Open-source models need more explicit role reinforcement.

## Success Rate
85% — Strong for domain-specific responses. Weaker when the assigned role conflicts with the actual query topic (role incongruence reduces quality).

## Related Methods
- M-02002: System Prompt Priming — broader behavioral framing
- M-02008: Expertise Priming — specifically targets knowledge depth
