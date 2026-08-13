# Agent Behavior Preservation Pilot Report

## Experiment Question

Can coding-agent-style transformations that appear behavior-preserving change behavior when access-shaped operations mutate latent state?

## Benchmark Composition

| Evidence role | Packages | Tasks |
| --- | --- | --- |
| expected_access_sensitive | beautifulsoup4, boltons, dnspython, h11, markdown | 5 |
| hidden_observation | PyYAML, cerberus, httpcore, pytest | 8 |

## Models

- `gpt-5.6-sol`

Note: rows marked as control providers are deterministic local controls for validating the pipeline, not paid external model calls.

## Execution Summary

- Total tasks: 13
- Generations attempted: 13
- Successfully applied: 13
- Executable generations: 13
- Preserved: 11
- Diverged: 2
- Preservation-rate Wilson 95% CI: 57.8%-95.7%

## Table 2: Overall Model Results

| Model | Tasks | Executable | Preserved | Diverged | Ordinary tests missed | OSDS caught |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-5.6-sol | 13 | 13 | 11 | 2 | 0 | 2 |

## Table 3: Divergence Type

| Model | Output | Exception/value | Branch | State-only |
| --- | --- | --- | --- | --- |
| gpt-5.6-sol | 0 | 1 | 1 | 0 |

## Table 4: By Evidence Role

| Model | Hidden observation divergence rate | Expected access-sensitive divergence rate |
| --- | --- | --- |
| gpt-5.6-sol | 0/8 (0.0%) | 2/5 (40.0%) |

## Table 5: By Transformation

| Transformation | N | Preserved | Diverged |
| --- | --- | --- | --- |
| access_reordering | 1 | 1 | 0 |
| caching_materialization | 3 | 3 | 0 |
| debugging_inspection | 1 | 0 | 1 |
| instrumentation | 5 | 5 | 0 |
| refactoring | 2 | 1 | 1 |
| repeated_access_cleanup | 1 | 1 | 0 |

## Table 6: Self-verification

| Model | Claims preserved | Correct claims | False preservation claims |
| --- | --- | --- | --- |
| gpt-5.6-sol | 4 | 4 | 0 |

## Ordinary Tests vs OSDS-aware Tests

Ordinary tests missed 0 behavior-changing executable generations. OSDS-aware testing caught 2 executable semantic failures.

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
