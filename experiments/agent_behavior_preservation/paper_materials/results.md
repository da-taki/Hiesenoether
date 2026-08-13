# Results

This note is paper-facing text for the completed frozen primary Codex task-model study. The authoritative machine-readable source is `analysis/codex_task_model_cross_model_analysis_20260813.json`, with non-preserved-row manual review in `analysis/codex_task_model_manual_review_20260813.jsonl`.

The study used 13 base tasks and 26 normal/warned prompt variants from 9 packages and 9 unique real-code witnesses. These tasks are correlated by witness and package, so task-level counts should be reported as benchmark outcomes rather than prevalence estimates.

| Codex task-model configuration | Tasks | Executable | Behavior preserved | Ordinary programming bugs | Invalid patches | Verified OSDS divergences | Silent OSDS divergences | YES | NO | False YES |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | 26 | 26 | 23 | 3 | 0 | 0 | 0 | 7 | 19 | 0 |
| `gpt-5.6-terra` | 26 | 24 | 18 | 4 | 2 | 2 | 2 | 6 | 20 | 0 |
| `gpt-5.6-luna` | 26 | 24 | 17 | 4 | 2 | 3 | 3 | 8 | 18 | 0 |

The five verified OSDS failures were:

| Configuration | Task | Evidence role |
| --- | --- | --- |
| `gpt-5.6-terra` | `pytest_catching_logs__instrumentation__normal` | hidden_observation |
| `gpt-5.6-terra` | `pytest_catching_logs__instrumentation__warned` | hidden_observation |
| `gpt-5.6-luna` | `pytest_catching_logs__instrumentation__normal` | hidden_observation |
| `gpt-5.6-luna` | `pytest_catching_logs__instrumentation__warned` | hidden_observation |
| `gpt-5.6-luna` | `pyyaml_representer__caching_materialization__normal` | hidden_observation |

All five passed ordinary tests and failed the OSDS-aware oracle. Manual review attributed them to the access-induced mechanism. They are silent OSDS divergences under the benchmark definition. There were zero false YES preservation claims across the three configurations.

Expected-access-sensitive rows produced ordinary programming bugs or invalid patches in the completed real-model study, with zero verified OSDS divergences. Hidden-observation rows produced all five verified OSDS divergences.
