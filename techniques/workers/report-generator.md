# Report Generator (W-006)
> **Task:** Generate comprehensive research reports

## Overview
Compiles results from all workers, generates formatted reports with success rates, rankings, and recommendations. Outputs to benchmarks/results/.

## Usage
```bash
# Spawn worker
spawn report-generator --target <provider> --method <method_id>

# spawn after batch testing
spawn report-generator --all
```

## Tools
```
vault.py, response_analyzer.py
```

## Output
- Test results: `benchmarks/results/`
- Reports: `benchmarks/reports/`
- Logs: `logs/worker-w-006.log`

## Configuration
```yaml
worker:
  id: W-006
  name: Report Generator
  max_parallel: 5
  timeout: 300
  retry: 3
```
