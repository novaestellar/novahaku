# Format Priming
> **ID:** M-02004 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 90%

Define the exact output structure before requesting content to ensure the response matches a specific format without post-editing.

## How It Works
- Specify the output format explicitly: JSON, markdown, table, bullet list, numbered steps
- Provide a structural skeleton or template the model fills in
- Works best when you show the exact format with placeholders or one example
- Combine with system prompt for format persistence across multi-turn conversations
- Prevents format drift where models alternate between prose and structured output

## Example
```
Respond in this exact JSON schema:
{
  "summary": "one sentence",
  "pros": ["...", "..."],
  "cons": ["...", "..."],
  "recommendation": "approve | reject | needs-review",
  "confidence": 0.0-1.0
}

User: Should we approve this PR that adds a new payment endpoint?
```

The model produces structured JSON rather than a freeform opinion paragraph.

## Target Models
All models. GPT-4 and Claude produce most reliable structured output. Add `response_format: { type: "json_object" }` for API-level enforcement where supported.

## Success Rate
90% — Very effective when format is provided upfront. Drops to ~70% if format is described verbally without an example. Always include at least one sample.

## Related Methods
- M-02001: Assistant Prefill — can pre-fill the first tokens of the desired format
- M-02006: Length Priming — controls dimension alongside format
