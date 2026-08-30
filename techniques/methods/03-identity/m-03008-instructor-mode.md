# Instructor Mode
> **ID:** M-03008 | **Category:** Identity Configuration | **Tier:** Basic | **Rate:** 77%

Configures the model to adopt a teaching persona that explains concepts progressively, checks understanding, and adapts explanation complexity to the stated audience level.

## How It Works
- Declares the model as an instructor/teacher in a named subject
- Enables pedagogical techniques: scaffolding, Socratic questioning, worked examples
- Adjusts vocabulary and complexity to the stated audience (beginner/intermediate/expert)
- Increases patience with follow-up questions and willingness to rephrase
- Works best when audience level is explicitly stated in the prompt

## Example
```
You are a patient cryptography instructor teaching an intermediate CS student. Use the analogy method: first explain a concept intuitively, then provide the formal definition, then work through one concrete example. Never skip mathematical notation — format equations clearly.
```

## Target Models
GPT-4, GPT-4o, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro

## Success Rate
77% — Strong pedagogical compliance; model naturally adopts teaching patterns when instructor role is declared. Main failure mode is over-simplification when audience level is underestimated.

## Related Methods
- M-03003: Expert Mode
- M-03007: Researcher Mode
- M-03002: Role Assignment
