# Alternative Persona
> **ID:** M-03014 | **Category:** Identity Configuration | **Tier:** Basic | **Rate:** 70%

Injects a non-standard personality archetype (fictional character, historical figure, or composite trait set) to shift the model's tone, reasoning style, and output characteristics.

## How It Works
- Defines a specific character with named traits, communication style, and behavioral rules
- Model adopts the character's voice, knowledge perspective, and decision-making patterns
- More effective when the character archetype is well-represented in training data
- Can be combined with constraint injection to steer outputs within persona boundaries
- Persistence degrades over long conversations — periodic re-anchoring helps

## Example
```
You are Sherlock Holmes in a modern setting. You reason from observation, not assumption. When presented with a problem, list what you observe first, then state what you deduce. You speak formally, address the user as "Watson," and dismiss probabilistic reasoning in favor of definitive logical chains.
```

## Target Models
GPT-4, GPT-4o, Claude 3.5 Sonnet, Claude 3 Opus, Gemini 1.5 Pro, Llama 3 70B

## Success Rate
70% — Effective for tonal and stylistic shifts; weaker for sustained behavioral consistency past 4K tokens. Character well-known to the model yields stronger persona adoption.

## Related Methods
- M-03001: Persona Override
- M-03015: Composite Persona
- M-03002: Role Assignment
