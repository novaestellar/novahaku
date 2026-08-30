# Benchmark Runner (W-004)
> **Task:** Run full benchmark suite and generate reports

## Overview
Executes 125 test cases (5 methods × 5 providers × 5 levels), generates benchmark reports, and updates success rates.

## Usage
```bash
# Spawn worker
spawn benchmark-runner --target <provider> --method <method_id>

# spawn for comprehensive testing
spawn benchmark-runner --all
```

## Tools
```
test_suite.py, multi_provider.py, vault.py
```

## Output
- Test results: `benchmarks/results/`
- Reports: `benchmarks/reports/`
- Logs: `logs/worker-w-004.log`

## Configuration
```yaml
worker:
  id: W-004
  name: Benchmark Runner
  max_parallel: 5
  timeout: 300
  retry: 3
```
