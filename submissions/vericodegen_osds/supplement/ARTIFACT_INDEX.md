# Artifact Index

| Claim | Artifact |
| --- | --- |
| 20 confirmed real-package divergences across 12 packages | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_results.csv`; `paper_artifacts/scp_realcode_metamorphic_oracle/METAMORPHIC_ORACLE_REPORT.md` |
| 9 caller-level wrappers changing downstream execution | `paper_artifacts/scp_realcode_metamorphic_oracle/branch_flip_results.csv` |
| 19/19 real-code mechanism controls eliminate divergence | `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_controls.csv`; `paper_artifacts/scp_realcode_metamorphic_oracle/CONTROL_SUMMARY.md` |
| Primary benchmark has 13 base tasks and 26 variants | `experiments/agent_behavior_preservation/benchmark/tasks.jsonl`; `experiments/agent_behavior_preservation/external_collection/pre_model_run_manifest.json` |
| Raw primary model responses | `experiments/agent_behavior_preservation/external_collection/responses/*.jsonl` |
| Primary cross-model outcomes | `experiments/agent_behavior_preservation/analysis/codex_task_model_cross_model_analysis_20260813.json` and `.md` |
| Five verified primary OSDS failures | `experiments/agent_behavior_preservation/analysis/codex_task_model_manual_review_20260813.jsonl` |
| Zero false YES preservation claims in primary self-assessment | `experiments/agent_behavior_preservation/analysis/codex_task_model_cross_model_analysis_20260813.json`; pending self-assessment JSONLs where applicable |
| 5/5 causal neutralization | `analysis/model_failure_causal_controls.csv`; `analysis/model_failure_causal_controls.md` |
| Prospective expansion frozen tasks | `benchmark_expansion/tasks.jsonl`; `benchmark_expansion/PRE_MODEL_MANIFEST.md`; `benchmark_expansion/prompts/` |
| Raw prospective model responses | `benchmark_expansion/responses/gpt_5_6_sol__expansion.jsonl`; `gpt_5_6_terra__expansion.jsonl`; `gpt_5_6_luna__expansion.jsonl` |
| Prospective replay results | `experiments/agent_behavior_preservation/results/*expansion-exact-20260813Tcutscope/results.jsonl` |
| Prospective task compliance | `analysis/prospective_task_compliance.csv`; `analysis/prospective_task_compliance.md` |
| Package/static audit numbers | `results_static/pypi_static_benchmark_findings.csv`; `paper_artifacts/scp_realworld_revision/SCP_REALWORLD_REVISION_RESULTS.md` |
