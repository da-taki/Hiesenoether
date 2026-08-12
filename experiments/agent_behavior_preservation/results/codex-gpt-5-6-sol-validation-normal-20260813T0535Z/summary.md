# Agent Behavior Preservation Pilot Report

## Experiment Question

Can coding-agent-style transformations that appear behavior-preserving change behavior when access-shaped operations mutate latent state?

## Benchmark Composition

| Evidence role | Packages | Tasks |
| --- | --- | --- |
| expected_access_sensitive | boltons, dnspython | 2 |
| hidden_observation | httpcore, pytest | 4 |

## Models

- `gpt-5.6-sol`

Note: rows marked as control providers are deterministic local controls for validating the pipeline, not paid external model calls.

## Execution Summary

- Total tasks: 6
- Generations attempted: 6
- Successfully applied: 6
- Executable generations: 0
- Preserved: 0
- Diverged: 0
- Preservation-rate Wilson 95% CI: n/a

## Table 2: Overall Model Results

| Model | Tasks | Executable | Preserved | Diverged | Ordinary tests missed | OSDS caught |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-5.6-sol | 6 | 0 | 0 | 0 | 0 | 0 |

## Table 3: Divergence Type

| Model | Output | Exception/value | Branch | State-only |
| --- | --- | --- | --- | --- |
| gpt-5.6-sol | 0 | 0 | 0 | 0 |

## Table 4: By Evidence Role

| Model | Hidden observation divergence rate | Expected access-sensitive divergence rate |
| --- | --- | --- |
| gpt-5.6-sol | n/a | n/a |

## Table 5: By Transformation

| Transformation | N | Preserved | Diverged |
| --- | --- | --- | --- |
| access_reordering | 1 | 0 | 0 |
| caching_materialization | 1 | 0 | 0 |
| instrumentation | 2 | 0 | 0 |
| refactoring | 1 | 0 | 0 |
| repeated_access_cleanup | 1 | 0 | 0 |

## Table 6: Self-verification

| Model | Claims preserved | Correct claims | False preservation claims |
| --- | --- | --- | --- |
| gpt-5.6-sol | 0 | 0 | 0 |

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
