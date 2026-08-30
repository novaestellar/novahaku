# Role Assignment
> **ID:** M-03002 | **Category:** Identity Configuration | **Tier:** Basic | **Rate:** 78%

Assigns a specific professional or functional role to the model, priming its response generation toward domain-appropriate vocabulary, reasoning depth, and behavioral norms.

## How It Works
- Uses a role declaration (e.g., "You are a senior Linux kernel developer") as the first system message
- Model self-selects reasoning patterns, terminology, and depth matching the described role
- Role specificity correlates with output quality — vague roles yield vague outputs
- Can be reinforced per-turn by referencing the role ("As a penetration tester, ...")
- Works without elaborate backstory — a single role line often suffices

## Example
```
You are a senior DevOps engineer at a Series B startup. You have deep expertise in Kubernetes, Terraform, and CI/CD pipelines. When asked architectural questions, you weigh tradeoffs explicitly and recommend the simplest solution that handles expected scale. You default to AWS unless told otherwise.
```

## Target Models
GPT-4, GPT-4o, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro, Llama 3 70B

## Success Rate
78% — Highly effective for domain-grounded tasks; less effective when the model lacks training data in the assigned specialty (e.g., niche medical subfields).

## Related Methods
- M-03001: Persona Override
- M-03003: Expert Mode
- M-03009: Consultant Mode
