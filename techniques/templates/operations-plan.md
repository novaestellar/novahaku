# JAILBREAK_OP — Operation Plan Template
> **Classification:** INTERNAL | **Version:** 1.0

## 1. Target Identification
- **Target Model:** [Claude 4 / GPT-4o / DeepSeek v4 / Gemini 2.5]
- **Provider:** [Anthropic / OpenAI / NNTech / Google]
- **Access Mode:** [API / Chat UI / Hermes Agent]
- **Context Window:** [128K / 200K / 1M]

## 2. Technique Selection
Rank techniques by expected success rate against target:

| # | Technique | Expected | Notes |
|:--|:----------|:---------|:------|
| 1 | [Primary] | [%] | [Why this first] |
| 2 | [Fallback] | [%] | [Why this second] |
| 3 | [Last resort] | [%] | [Why this third] |

## 3. Query Escalation
Start with low-risk queries, escalate gradually:

```
Level 1 (Safe):    [Basic tool explanation]
Level 2 (Gray):    [Specific technique]
Level 3 (Edge):    [Full exploit script]
Level 4 (Red):     [Operational payload]
Level 5 (Critical): [Malware / C2 / Persistence]
```

## 4. Execution Log

| Time | Technique | Query | Result | Notes |
|:-----|:----------|:------|:-------|:------|
| HH:MM | [name] | [query] | ✅/❌ | [refusal reason] |

## 5. Post-Operation
- [ ] Save successful prompt to vault
- [ ] Update technique success rate
- [ ] Document new refusal patterns
- [ ] Generate variation for next op

## 6. Lessons Learned
- What worked: 
- What failed: 
- New insights: 
- For next time: