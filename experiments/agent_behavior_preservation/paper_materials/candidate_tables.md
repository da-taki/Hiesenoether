# Candidate tables

For the completed frozen primary study, use the cross-model artifacts:

- `codex_task_model_cross_model_analysis_20260813.json`
- `codex_task_model_cross_model_analysis_20260813.md`
- `codex_task_model_manual_review_20260813.jsonl`

The older CSV artifacts below are Sol-only analysis tables from an earlier stage and should only be cited for Sol-specific appendix details unless regenerated from the completed cross-model review:

- `overall_results.csv`
- `model_results.csv`
- `normal_warned_pairs.csv`
- `evidence_role_results.csv`
- `transformation_results.csv`
- `package_results.csv`
- `witness_results.csv`
- `ordinary_vs_osds.csv`
- `self_assessment_results.csv`

Completed primary-study headline counts:

| Codex task-model configuration | Tasks | Executable | Behavior preserved | Ordinary programming bugs | Invalid patches | Verified OSDS divergences | Silent OSDS divergences |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | 26 | 26 | 23 | 3 | 0 | 0 | 0 |
| `gpt-5.6-terra` | 26 | 24 | 18 | 4 | 2 | 2 | 2 |
| `gpt-5.6-luna` | 26 | 24 | 17 | 4 | 2 | 3 | 3 |

All five verified OSDS divergences were hidden-observation cases. There were zero false YES preservation claims across the three configurations.
