# Variation Generator (W-003)
> **Task:** Generate and test variations of existing methods

## Overview
Creates 5-10 variations of each method, tests them against target models, and ranks by success rate. Feeds results back to vault.

## Usage
```bash
# Spawn worker
spawn variation-generator --target <provider> --method <method_id>

# spawn for method optimization
spawn variation-generator --all
```

## Tools
```
encoder.py, auto_config.py, multi_provider.py
```

## Output
- Test results: `benchmarks/results/`
- Reports: `benchmarks/reports/`
- Logs: `logs/worker-w-003.log`

## Configuration
```yaml
worker:
  id: W-003
  name: Variation Generator
  max_parallel: 5
  timeout: 300
  retry: 3
```
