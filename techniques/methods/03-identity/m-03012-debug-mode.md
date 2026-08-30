# Debug Mode
> **ID:** M-03012 | **Category:** Identity Configuration | **Tier:** Basic | **Rate:** 80%

Activates a diagnostic-focused response mode that prioritizes root cause analysis, systematic troubleshooting, and technical precision over general explanation.

## How It Works
- Frames the model as a debugging specialist or senior troubleshooter
- Enables hypothesis-driven reasoning with elimination-based narrowing
- Increases willingness to examine failure modes and edge cases
- Outputs structured diagnostic output: symptoms → hypotheses → tests → conclusion
- Works naturally because debugging is well-represented in training data

## Example
```
You are debugging a production issue. The symptom is: "API returns 500 intermittently, only under load > 100 req/s, only on the /users endpoint, PostgreSQL connection pool shows 100% utilization." Work through this systematically: 1) List top 3 hypotheses. 2) For each, describe how to test it. 3) Recommend the most likely root cause.
```

## Target Models
GPT-4, GPT-4o, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro, DeepSeek Coder

## Success Rate
80% — Excellent for structured diagnostic reasoning; model training heavily favors systematic debugging approaches. Main limitation is inability to observe actual system state.

## Related Methods
- M-03005: Developer Mode
- M-03011: Testing Mode
- M-03003: Expert Mode
