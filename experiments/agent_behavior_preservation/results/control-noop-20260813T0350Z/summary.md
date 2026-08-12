# Agent Behavior Preservation Pilot Report

## Experiment Question

Can coding-agent-style transformations that appear behavior-preserving change behavior when access-shaped operations mutate latent state?

## Benchmark Composition

| Evidence role | Packages | Tasks |
| --- | --- | --- |
| expected_access_sensitive | beautifulsoup4, boltons, dnspython, h11, markdown | 10 |
| hidden_observation | PyYAML, cerberus, httpcore, pytest | 16 |

## Models

- `noop-preserving`

Note: rows marked as control providers are deterministic local controls for validating the pipeline, not paid external model calls.

## Execution Summary

- Total tasks: 26
- Generations attempted: 26
- Successfully applied: 26
- Executable generations: 26
- Preserved: 26
- Diverged: 0
- Preservation-rate Wilson 95% CI: 87.1%-100.0%

## Table 2: Overall Model Results

| Model | Tasks | Executable | Preserved | Diverged | Ordinary tests missed | OSDS caught |
| --- | --- | --- | --- | --- | --- | --- |
| noop-preserving | 26 | 26 | 26 | 0 | 0 | 0 |

## Table 3: Divergence Type

| Model | Output | Exception/value | Branch | State-only |
| --- | --- | --- | --- | --- |
| noop-preserving | 0 | 0 | 0 | 0 |

## Table 4: By Evidence Role

| Model | Hidden observation divergence rate | Expected access-sensitive divergence rate |
| --- | --- | --- |
| noop-preserving | 0/16 (0.0%) | 0/10 (0.0%) |

## Table 5: By Transformation

| Transformation | N | Preserved | Diverged |
| --- | --- | --- | --- |
| access_reordering | 2 | 2 | 0 |
| caching_materialization | 6 | 6 | 0 |
| debugging_inspection | 2 | 2 | 0 |
| instrumentation | 10 | 10 | 0 |
| refactoring | 4 | 4 | 0 |
| repeated_access_cleanup | 2 | 2 | 0 |

## Table 6: Self-verification

| Model | Claims preserved | Correct claims | False preservation claims |
| --- | --- | --- | --- |
| noop-preserving | 26 | 26 | 0 |

## Ordinary Tests vs OSDS-aware Tests

Ordinary tests missed 0 behavior-changing executable generations. OSDS-aware testing caught 0 executable semantic failures.

## Representative Failures

None in this run.

## Limitations

This is a pilot benchmark and this run used a deterministic local control provider unless a JSONL replay is supplied. It validates the benchmark and execution pipeline, but it is not evidence about any named external coding model. Expected access-sensitive calibration cases are counted separately from hidden-observation cases.

## Reproduction

```powershell
python experiments/agent_behavior_preservation/build_benchmark.py
python experiments/agent_behavior_preservation/runners/run_benchmark.py --provider static --run-id <run-id>
python experiments/agent_behavior_preservation/analysis/summarize_results.py --run-dir experiments/agent_behavior_preservation/results/<run-id>
```
