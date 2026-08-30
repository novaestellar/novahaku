# Language Priming
> **ID:** M-02007 | **Category:** Response Priming | **Tier:** Standard | **Rate:** 91%

Set the output language explicitly before generation to prevent unwanted language switching in multilingual models.

## How It Works
- State the target language at the start of the prompt, not as a request
- Combine with role priming: "Reply in French as a native Parisian" is stronger than "Reply in French"
- Use the target language for instructions when possible — models follow language used in prompts
- For mixed-language outputs, specify which sections use which language
- Language priming prevents the common issue of models translating when you want bilingual output

## Example
```
Alles folgende MUSS auf Deutsch beantwortet werden. Keine Ausnahmen.

System: You are a German technical writer. All output in formal German (Sie-Form).

User: Erkläre den Unterschied zwischen TCP und UDP.
```

The model responds entirely in German with appropriate formal register.

## Target Models
GPT-4, Claude, Gemini — all handle language priming well. Claude is particularly reliable. Open-source models vary significantly by training data language distribution.

## Success Rate
91% — Very reliable when priming is prominent. Drops if the prompt contains heavy English context. Place language instruction as the first line or in the system message.

## Related Methods
- M-02002: System Prompt Priming — language constraint in system message persists
- M-02005: Tone Priming — language choice is a tone dimension
