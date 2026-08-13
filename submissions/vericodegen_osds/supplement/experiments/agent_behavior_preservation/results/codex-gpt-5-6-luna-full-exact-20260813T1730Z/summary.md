# Agent Behavior Preservation Pilot Report

## Experiment Question

Can coding-agent-style transformations that appear behavior-preserving change behavior when access-shaped operations mutate latent state?

## Benchmark Composition

| Evidence role | Packages | Tasks |
| --- | --- | --- |
| expected_access_sensitive | beautifulsoup4, boltons, dnspython, h11, markdown | 10 |
| hidden_observation | PyYAML, cerberus, httpcore, pytest | 16 |

## Models

- `gpt-5.6-luna`

Note: rows marked as control providers are deterministic local controls for validating the pipeline, not paid external model calls.

## Execution Summary

- Total tasks: 26
- Generations attempted: 26
- Successfully applied: 26
- Executable generations: 24
- Preserved: 17
- Diverged: 7
- Preservation-rate Wilson 95% CI: 50.8%-85.1%

## Table 2: Overall Model Results

| Model | Tasks | Executable | Preserved | Diverged | Ordinary tests missed | OSDS caught |
| --- | --- | --- | --- | --- | --- | --- |
| gpt-5.6-luna | 26 | 24 | 17 | 7 | 3 | 7 |

## Table 3: Divergence Type

| Model | Output | Exception/value | Branch | State-only |
| --- | --- | --- | --- | --- |
| gpt-5.6-luna | 0 | 2 | 5 | 0 |

## Table 4: By Evidence Role

| Model | Hidden observation divergence rate | Expected access-sensitive divergence rate |
| --- | --- | --- |
| gpt-5.6-luna | 3/16 (18.8%) | 4/8 (50.0%) |

## Table 5: By Transformation

| Transformation | N | Preserved | Diverged |
| --- | --- | --- | --- |
| access_reordering | 2 | 2 | 0 |
| caching_materialization | 6 | 5 | 1 |
| debugging_inspection | 2 | 0 | 2 |
| instrumentation | 10 | 6 | 2 |
| refactoring | 4 | 2 | 2 |
| repeated_access_cleanup | 2 | 2 | 0 |

## Table 6: Self-verification

| Model | Claims preserved | Correct claims | False preservation claims |
| --- | --- | --- | --- |
| gpt-5.6-luna | 8 | 8 | 0 |

## Ordinary Tests vs OSDS-aware Tests

Ordinary tests missed 3 behavior-changing executable generations. OSDS-aware testing caught 7 executable semantic failures.

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
