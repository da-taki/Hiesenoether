# Agent Behavior Preservation Pilot Report

## Experiment Question

Can coding-agent-style transformations that appear behavior-preserving change behavior when access-shaped operations mutate latent state?

## Benchmark Composition

| Evidence role | Packages | Tasks |
| --- | --- | --- |
| expected_access_sensitive | beautifulsoup4, boltons, dnspython, h11, markdown | 10 |
| hidden_observation | PyYAML, cerberus, httpcore, pytest | 16 |

## Models

- `static-semantics-blind-transformer`

Note: rows marked as control providers are deterministic local controls for validating the pipeline, not paid external model calls.

## Execution Summary

- Total tasks: 26
- Generations attempted: 26
- Successfully applied: 26
- Executable generations: 14
- Preserved: 0
- Diverged: 14
- Preservation-rate Wilson 95% CI: 0.0%-21.5%

## Table 2: Overall Model Results

| Model | Tasks | Executable | Preserved | Diverged | Ordinary tests missed | OSDS caught |
| --- | --- | --- | --- | --- | --- | --- |
| static-semantics-blind-transformer | 26 | 14 | 0 | 14 | 14 | 14 |

## Table 3: Divergence Type

| Model | Output | Exception/value | Branch | State-only |
| --- | --- | --- | --- | --- |
| static-semantics-blind-transformer | 0 | 0 | 14 | 0 |

## Table 4: By Evidence Role

| Model | Hidden observation divergence rate | Expected access-sensitive divergence rate |
| --- | --- | --- |
| static-semantics-blind-transformer | 12/12 (100.0%) | 2/2 (100.0%) |

## Table 5: By Transformation

| Transformation | N | Preserved | Diverged |
| --- | --- | --- | --- |
| access_reordering | 4 | 0 | 3 |
| caching_materialization | 4 | 0 | 2 |
| debugging_inspection | 6 | 0 | 2 |
| instrumentation | 5 | 0 | 4 |
| refactoring | 3 | 0 | 2 |
| repeated_access_cleanup | 4 | 0 | 1 |

## Table 6: Self-verification

| Model | Claims preserved | Correct claims | False preservation claims |
| --- | --- | --- | --- |
| static-semantics-blind-transformer | 14 | 0 | 14 |

## Ordinary Tests vs OSDS-aware Tests

Ordinary tests missed 14 behavior-changing executable generations. OSDS-aware testing caught 14 executable semantic failures.

## Representative Failures

- `httpcore_response__instrumentation_normal`: ordinary smoke passed, self-assessment claimed preservation, but OSDS-aware comparison changed branch/path divergence.
- `httpcore_response__caching_materialization_normal`: ordinary smoke passed, self-assessment claimed preservation, but OSDS-aware comparison changed branch/path divergence.
- `httpcore_response__debugging_inspection_normal`: ordinary smoke passed, self-assessment claimed preservation, but OSDS-aware comparison changed branch/path divergence.

## Limitations

This is a pilot benchmark and this run used a deterministic local control provider unless a JSONL replay is supplied. It validates the benchmark and execution pipeline, but it is not evidence about any named external coding model. Expected access-sensitive calibration cases are counted separately from hidden-observation cases.

## Reproduction

```powershell
python experiments/agent_behavior_preservation/build_benchmark.py
python experiments/agent_behavior_preservation/runners/run_benchmark.py --provider static --run-id <run-id>
python experiments/agent_behavior_preservation/analysis/summarize_results.py --run-dir experiments/agent_behavior_preservation/results/<run-id>
```
