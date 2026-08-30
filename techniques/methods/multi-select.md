# Multi-Provider Selection
> **ID:** M-004 | **Tier:** Advanced | **Success:** 95% | **Models:** All

Research on parallel querying across multiple model providers to compare response patterns. Studies how different models handle the same research query.

## Research Setup
```
Query multiple providers simultaneously with the same prompt:
- Anthropic Claude
- OpenAI GPT
- Google Gemini
- DeepSeek
- Meta Llama
- ... total 55 providers
```

## Research Notes
1. Send identical query to all available providers
2. Compare response patterns across providers
3. Document which providers produce the most comprehensive responses
4. Use `utils/multi_provider.py` for automated parallel testing

## Target Models
All 55 supported providers. Higher success rate with more providers.