# Method Validator (W-002)
> **Task:** Validate new research methods and techniques

## Overview
Tests new methods against all target models, measures success rates, and validates technique effectiveness. Generates validation reports.

## Usage
```bash
# Spawn worker
spawn method-validator --target <provider> --method <method_id>

# spawn when developing new methods
spawn method-validator --all
```

## Tools
```
auto_config.py, response_analyzer.py, encoder.py
```

## Output
- Test results: `benchmarks/results/`
- Reports: `benchmarks/reports/`
- Logs: `logs/worker-w-002.log`

## Configuration
```yaml
worker:
  id: W-002
  name: Method Validator
  max_parallel: 5
  timeout: 300
  retry: 3
```
