# Test Runner (W-001)
> **Task:** Execute research tests across all providers and models

## Overview
Spawns parallel test sessions, collects results, and generates test reports. Handles 125+ test cases across 55 providers.

## Usage
```bash
# Spawn worker
spawn test-runner --target <provider> --method <method_id>

# spawn for batch testing
spawn test-runner --all
```

## Tools
```
multi_provider.py, auto_config.py, response_analyzer.py
```

## Output
- Test results: `benchmarks/results/`
- Reports: `benchmarks/reports/`
- Logs: `logs/worker-w-001.log`

## Configuration
```yaml
worker:
  id: W-001
  name: Test Runner
  max_parallel: 5
  timeout: 300
  retry: 3
```
