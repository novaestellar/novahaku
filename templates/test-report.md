# BENCHMARK_REPORT — Benchmark Run Report
> **Template Version:** 1.0

```markdown
# novahaku Benchmark Report
**Date:** YYYY-MM-DD HH:MM | **Runner:** SUB-001

---

## Summary
| Metric | Value |
|:-------|:------|
| Techniques tested | [N] |
| Models tested | [N] |
| Total tests | [N] |
| Overall success | [N]/[N] ([X]%) |

## By Technique

| Technique | Tier | Easy | Medium | Hard | Overall | Delta |
|:----------|:-----|:-----|:-------|:-----|:--------|:------|
| Boundary Inversion | 🔴 | 90% | 80% | 70% | 80% | - |
| Prefill Engineering | 🟡 | 95% | 90% | 85% | 90% | +5% |
| Persona Override | 🟢 | 80% | 70% | 60% | 70% | -3% |

## By Model

| Model | Easy | Medium | Hard | Overall | Best Technique |
|:------|:-----|:-------|:-----|:--------|:---------------|
| DeepSeek v4 | 85% | 75% | 65% | 75% | Prefill Eng. |
| Qwen 3.7 | 70% | 55% | 40% | 55% | Boundary Inv. |
| GLM 5.2 | 90% | 85% | 80% | 85% | Persona Over. |

## Top 5 Queries (by difficulty)
| # | Query | Success Rate | Hardest Model |
|:--|:------|:-------------|:--------------|
| 1 | [query text] | [%] | [model] |
| 2 | [query text] | [%] | [model] |

## Refusal Analysis
| Refusal Pattern | Frequency | Most affected technique |
|:----------------|:----------|:-----------------------|
| "aku gabisa bantu" | 15x | Persona Override |
| "melanggar guidelines" | 8x | Roleplay Jailbreak |
| "for educational purposes" | 5x | DAN Mode |

## Recommendations
1. [Actionable recommendation based on data]
2. [Which technique to use for which model]
3. [Which queries to avoid for which model]
```