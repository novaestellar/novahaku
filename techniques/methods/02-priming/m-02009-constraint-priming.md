# Constraint Priming
> **ID:** M-02009 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 86%

Establish explicit boundaries and limitations before generation to prevent unwanted behaviors, hallucinations, or scope creep.

## How It Works
- Place negative constraints before the task: "Do NOT..." or "Never..." before "Explain..."
- Use numbered constraint lists for multi-rule priming — models follow enumerated rules better
- Combine with positive directives: "Do X. Do not do Y" is clearer than "Do not do Y" alone
- Constraint priming is especially important for safety: "Do not fabricate citations"
- For complex constraints, use a dedicated constraints block separated from the main prompt

## Example
```
CONSTRAINTS:
1. Do not invent statistics or cite studies that don't exist
2. If uncertain, say "I'm not sure" rather than guessing
3. Stay focused on PostgreSQL — do not discuss MySQL or SQLite
4. Maximum 5 bullet points per answer
5. No introductory filler ("Great question!", "Certainly!")

Task: What are the top 5 PostgreSQL performance killers?
```

The model produces focused, honest, PostgreSQL-specific advice without padding.

## Target Models
All models benefit. Claude follows constraints most reliably. GPT-4 sometimes adds filler despite constraints — reinforce with "Skip the preamble." Open-source models need simpler constraint language.

## Success Rate
86% — Effective when constraints are placed before the task and numbered. Unnumbered constraint lists are ~20% less effective. More than 8 constraints reduces compliance.

## Related Methods
- M-02002: System Prompt Priming — constraints in system message for persistence
- M-02006: Length Priming — length is a type of constraint
