# Multi-Turn Priming
> **ID:** M-02010 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 80%

Use earlier conversation turns to establish patterns, preferences, and behavioral baselines that the model follows in subsequent turns.

## How It Works
- Start with a calibration turn: give an example Q&A pair showing desired behavior
- The model's in-context learning picks up patterns from the example turn
- Reinforce the pattern across 2-3 turns before introducing the main task
- Works because models optimize for consistency with conversation history
- Especially powerful for establishing output format, depth, and style across a session

## Example
```
Turn 1 (system): You are a code reviewer. Here's how you should respond:

User: Review: def add(a, b): return a + b
Assistant: [MEDIUM] No type hints. Suggest: def add(a: int, b: int) -> int: return a + b
Missing docstring. Consider: """Add two integers."""

Now apply this same format to all future reviews. Be consistent.
```

After this calibration, all subsequent reviews follow the same terse, bracketed-severity format.

## Target Models
GPT-4, Claude, Gemini — all support in-context learning from multi-turn examples. Effectiveness depends on context window. Claude maintains patterns longest across turns.

## Success Rate
80% — Reliable for format and style consistency. Less effective for changing already-established patterns mid-conversation. Best used from turn 1.

## Related Methods
- M-02011: Chain Priming — chains multiple distinct priming steps
- M-02015: Adaptive Priming — adjusts the pattern based on intermediate results
