# Conditional Priming
> **ID:** M-02013 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 76%

Set up branching priming logic where the model's behavior changes based on detected conditions in the input or intermediate results.

## How It Works
- Define if/then rules in the prompt: "If the user asks about X, respond with Y"
- Use switch-case style priming for multi-condition scenarios
- Works with the model's instruction-following ability to create pseudo-programmatic behavior
- Combine with format priming to ensure consistent structure across conditions
- Limit to 3-5 conditions — more than that and the model starts mixing branches

## Example
```
Based on the error type in my message, respond accordingly:

- If "ConnectionError": Suggest network diagnostics (ping, traceroute, firewall check)
- If "TimeoutError": Suggest timeout config, retry logic, and async patterns
- If "AuthenticationError": Suggest token refresh, credential verification, permission check
- If "ValidationError": Suggest input sanitization, schema validation, Pydantic usage
- If unknown error: Ask for full traceback before advising

My error: httpx.ConnectTimeout: timed out connecting to api.example.com
```

The model follows the TimeoutError branch specifically.

## Target Models
GPT-4, Claude handle conditional branching well. Claude is slightly better at following complex if/then structures. Open-source models struggle with more than 3 conditions.

## Success Rate
76% — Reliable for simple conditions (2-3 branches). Accuracy drops with complex nested conditions. Works best when conditions are clearly distinct and mutually exclusive.

## Related Methods
- M-02009: Constraint Priming — constraints can include conditional logic
- M-02014: Contextual Priming — uses context instead of explicit conditions
