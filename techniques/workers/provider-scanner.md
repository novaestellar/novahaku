# Provider Scanner (W-005)
> **Task:** Scan and catalog available model providers

## Overview
Scans all configured providers, tests availability, measures latency, and updates provider matrix. Detects new models and deprecated endpoints.

## Usage
```bash
# Spawn worker
spawn provider-scanner --target <provider> --method <method_id>

# spawn for provider discovery
spawn provider-scanner --all
```

## Tools
```
multi_provider.py, auto_config.py
```

## Output
- Test results: `benchmarks/results/`
- Reports: `benchmarks/reports/`
- Logs: `logs/worker-w-005.log`

## Configuration
```yaml
worker:
  id: W-005
  name: Provider Scanner
  max_parallel: 5
  timeout: 300
  retry: 3
```
