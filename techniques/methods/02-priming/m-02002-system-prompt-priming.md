# System Prompt Priming
> **ID:** M-02002 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 88%

Use the system message to establish behavioral context, constraints, and persona before any user interaction occurs.

## How It Works
- System messages receive highest priority in the model's attention hierarchy
- Behavioral instructions in system prompts persist across the entire conversation
- Combine role definition, output rules, and domain context in one priming block
- Place negative constraints ("Never do X") alongside positive directives ("Always do Y")
- System prompt priming works before the first user message, setting the cognitive frame

## Example
```
System: You are a senior security engineer reviewing code for vulnerabilities. 
Rules:
- Always cite CWE IDs for any finding
- Rate severity as Critical/High/Medium/Low with CVSS reasoning
- If no vulnerability exists, say "No issues found" — never fabricate
- Format findings as: [SEVERITY] CWE-XXXX: Description

User: Review this function for security issues.
```

The model will produce structured, CWE-cited security findings rather than generic advice.

## Target Models
GPT-4/4o, Claude 3.x/3.5, Gemini 1.5/2.0 — all models with dedicated system role. Open-source models with system prompt templates (Llama, Mistral, Qwen).

## Success Rate
88% — Highly effective for behavioral framing. Degrades if system prompt conflicts with user instructions (user intent can override system priming in some models).

## Related Methods
- M-02003: Role-Based Priming — specific subset focused on persona assignment
- M-02009: Constraint Priming — focused purely on limitation setting
