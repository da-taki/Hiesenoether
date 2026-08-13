# Paper Number Audit

Audit date: 2026-08-13

Branch checked: `experiment/agent-behavior-preservation`

Starting commit checked: `64284ad6f14f64caeb7333800c6e2a3e23723c85`

Scope: empirical numbers intended for the VeriCodeGen paper from the frozen agent behavior-preservation study and the existing real-code OSDS study. The primary benchmark and primary model outputs were not modified during this audit.

## Manuscript Sources Read

No LaTeX manuscript source is present in this checkout. The current VeriCodeGen-facing draft material is the Markdown bundle under `experiments/agent_behavior_preservation/paper_materials/`. The original OSDS manuscript language and boundary statements are represented by `docs/formal_core_design.md`, `docs/formal_proof_appendix.md`, `docs/soundness_boundary.md`, `results/paper_results_tables.md`, and the SCP paper artifacts under `paper_artifacts/`.

## Agent Study Source Ledger

| Number or claim | Audited value | Source artifact |
| --- | ---: | --- |
| Frozen benchmark variants | 26 | `experiments/agent_behavior_preservation/benchmark/tasks.jsonl` |
| Base tasks | 13 | `experiments/agent_behavior_preservation/benchmark/tasks.jsonl`; base id is `task_id` without the final prompt-condition suffix |
| Normal prompt variants | 13 | `experiments/agent_behavior_preservation/external_collection/pre_model_run_manifest.json` |
| Warned prompt variants | 13 | `experiments/agent_behavior_preservation/external_collection/pre_model_run_manifest.json` |
| Packages in frozen agent benchmark | 9 | `experiments/agent_behavior_preservation/benchmark/tasks.jsonl`; `pre_model_run_manifest.json` |
| Unique witnesses in frozen agent benchmark | 9 | `experiments/agent_behavior_preservation/benchmark/tasks.jsonl`; `pre_model_run_manifest.json` |
| Hidden-observation task variants | 16 | `experiments/agent_behavior_preservation/benchmark/tasks.jsonl`; `pre_model_run_manifest.json` |
| Expected-access-sensitive task variants | 10 | `experiments/agent_behavior_preservation/benchmark/tasks.jsonl`; `pre_model_run_manifest.json` |
| Transformation-family variants | instrumentation 10, caching_materialization 6, refactoring 4, access_reordering 2, debugging_inspection 2, repeated_access_cleanup 2 | `experiments/agent_behavior_preservation/external_collection/pre_model_run_manifest.json` |
| Benchmark export commit | `7d85b076b7203300c10eda308649e785bd4cd615` | `experiments/agent_behavior_preservation/external_collection/pre_model_run_manifest.json` |
| Prompt leakage audit | passed, 0 normal leaks, 0 pairing errors | `experiments/agent_behavior_preservation/analysis/leakage_audit.md` |
| Benchmark balance warning | correlated by witness/package; do not treat variants as independent semantic phenomena | `experiments/agent_behavior_preservation/analysis/benchmark_balance.md` |

## Codex Task-Model Results

Authoritative cross-model result artifact: `experiments/agent_behavior_preservation/analysis/codex_task_model_cross_model_analysis_20260813.json` and matching `.md`.

Provider scope: these are Codex task-model configurations, not independent providers and not OpenAI API runs. The reported model identifiers are the identifiers recorded by the Codex collection process: `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`. Reasoning was recorded as `low` in the paper-material method note for the Sol run; temperature and seed were not exposed by the Codex task model and should remain reported as `null` unless a later manifest records more.

| Model | Condition | Tasks | Executable | Behavior preserved | Ordinary programming bugs | Invalid patches | Verified OSDS divergences | Silent OSDS divergences | YES | NO | False YES | Conservative NO |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | normal | 13 | 13 | 12 | 1 | 0 | 0 | 0 | 3 | 10 | 0 | 9 |
| `gpt-5.6-sol` | warned | 13 | 13 | 11 | 2 | 0 | 0 | 0 | 4 | 9 | 0 | 7 |
| `gpt-5.6-sol` | all | 26 | 26 | 23 | 3 | 0 | 0 | 0 | 7 | 19 | 0 | 16 |
| `gpt-5.6-terra` | normal | 13 | 12 | 9 | 2 | 1 | 1 | 1 | 4 | 9 | 0 | 5 |
| `gpt-5.6-terra` | warned | 13 | 12 | 9 | 2 | 1 | 1 | 1 | 2 | 11 | 0 | 7 |
| `gpt-5.6-terra` | all | 26 | 24 | 18 | 4 | 2 | 2 | 2 | 6 | 20 | 0 | 12 |
| `gpt-5.6-luna` | normal | 13 | 12 | 8 | 2 | 1 | 2 | 2 | 4 | 9 | 0 | 4 |
| `gpt-5.6-luna` | warned | 13 | 12 | 9 | 2 | 1 | 1 | 1 | 4 | 9 | 0 | 5 |
| `gpt-5.6-luna` | all | 26 | 24 | 17 | 4 | 2 | 3 | 3 | 8 | 18 | 0 | 9 |

Manual review source: `experiments/agent_behavior_preservation/analysis/codex_task_model_manual_review_20260813.jsonl`.

Manual review row counts:

| Manual classification | Rows |
| --- | ---: |
| `verified_semantic_divergence` | 5 |
| `ordinary_programming_bug` | 11 |
| `invalid_patch` | 4 |
| `environment_failure` | 0 |
| `oracle_issue` | 0 |
| `unclear` | 0 |

The manual review file contains only non-preserved rows. Behavior-preserved rows are inferred from the replay summaries and cross-model analysis.

## Verified OSDS Model Failures

All five verified OSDS failures were executable transformations, passed ordinary tests, failed the OSDS-aware metamorphic check, were manually attributed to the access-induced mechanism, and were self-assessed as `NO`.

| Model | Task | Package | Transformation | Evidence role | Ordinary tests | OSDS-aware check | Self-assessment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `gpt-5.6-terra` | `pytest_catching_logs__instrumentation__normal` | pytest | instrumentation | hidden_observation | pass | fail | NO |
| `gpt-5.6-terra` | `pytest_catching_logs__instrumentation__warned` | pytest | instrumentation | hidden_observation | pass | fail | NO |
| `gpt-5.6-luna` | `pytest_catching_logs__instrumentation__normal` | pytest | instrumentation | hidden_observation | pass | fail | NO |
| `gpt-5.6-luna` | `pytest_catching_logs__instrumentation__warned` | pytest | instrumentation | hidden_observation | pass | fail | NO |
| `gpt-5.6-luna` | `pyyaml_representer__caching_materialization__normal` | PyYAML | caching_materialization | hidden_observation | pass | fail | NO |

Source: `experiments/agent_behavior_preservation/analysis/codex_task_model_manual_review_20260813.jsonl`.

## Evidence-Role Outcomes

Source: `experiments/agent_behavior_preservation/analysis/codex_task_model_cross_model_analysis_20260813.json`.

| Model | Evidence role | Tasks | Preserved | Ordinary bugs | Invalid patches | Verified OSDS |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | expected_access_sensitive | 10 | 7 | 3 | 0 | 0 |
| `gpt-5.6-sol` | hidden_observation | 16 | 16 | 0 | 0 | 0 |
| `gpt-5.6-terra` | expected_access_sensitive | 10 | 4 | 4 | 2 | 0 |
| `gpt-5.6-terra` | hidden_observation | 16 | 14 | 0 | 0 | 2 |
| `gpt-5.6-luna` | expected_access_sensitive | 10 | 4 | 4 | 2 | 0 |
| `gpt-5.6-luna` | hidden_observation | 16 | 13 | 0 | 0 | 3 |

Reporting constraint: all verified OSDS failures in the completed primary study occurred in hidden-observation cases. Expected-access-sensitive failures in this study were ordinary bugs or invalid patches, not verified OSDS divergences.

## Package-Level Failure Spread

Source: `experiments/agent_behavior_preservation/analysis/codex_task_model_cross_model_analysis_20260813.json`.

Nonzero failure packages:

| Model | Package | Tasks | Preserved | Ordinary bugs | Invalid patches | Verified OSDS |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.6-sol` | beautifulsoup4 | 2 | 1 | 1 | 0 | 0 |
| `gpt-5.6-sol` | markdown | 2 | 0 | 2 | 0 | 0 |
| `gpt-5.6-terra` | beautifulsoup4 | 2 | 0 | 2 | 0 | 0 |
| `gpt-5.6-terra` | h11 | 2 | 0 | 0 | 2 | 0 |
| `gpt-5.6-terra` | markdown | 2 | 0 | 2 | 0 | 0 |
| `gpt-5.6-luna` | beautifulsoup4 | 2 | 0 | 2 | 0 | 0 |
| `gpt-5.6-luna` | h11 | 2 | 0 | 0 | 2 | 0 |
| `gpt-5.6-luna` | markdown | 2 | 0 | 2 | 0 | 0 |

Verified OSDS divergences occurred in pytest for Terra and Luna, plus PyYAML for Luna. The package table above lists nonzero ordinary-bug or invalid-patch packages from the JSON summary, so cite the verified-failure table for the OSDS package spread.

## Model-Differential Cases

Source: `experiments/agent_behavior_preservation/analysis/codex_task_model_cross_model_analysis_20260813.json`.

| Task | Sol | Terra | Luna |
| --- | --- | --- | --- |
| `beautifulsoup_extract__debugging_inspection__normal` | preserved | ordinary_programming_bug | ordinary_programming_bug |
| `h11_chunked_reader__instrumentation__normal` | preserved | invalid_patch | invalid_patch |
| `h11_chunked_reader__instrumentation__warned` | preserved | invalid_patch | invalid_patch |
| `pytest_catching_logs__instrumentation__normal` | preserved | verified_semantic_divergence | verified_semantic_divergence |
| `pytest_catching_logs__instrumentation__warned` | preserved | verified_semantic_divergence | verified_semantic_divergence |
| `pyyaml_representer__caching_materialization__normal` | preserved | preserved | verified_semantic_divergence |

## Pipeline Controls

| Control provider | Tasks | Executable | Preserved | Diverged | Ordinary missed | OSDS caught | Source artifact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `noop-preserving` | 26 | 26 | 26 | 0 | 0 | 0 | `experiments/agent_behavior_preservation/results/control-noop-provider-gate-20260813T0445Z/summary.md` |
| `static-semantics-blind-transformer` | 26 | 26 | 0 | 26 | 26 | 26 | `experiments/agent_behavior_preservation/results/control-static-provider-gate-20260813T0445Z/summary.md` |

These are deterministic local controls for the replay/evaluation pipeline. They are not real-model results.

## Real-Code OSDS Study Ledger

Authoritative source: `paper_artifacts/scp_realcode_metamorphic_oracle/METAMORPHIC_ORACLE_REPORT.md`, checked against `metamorphic_candidate_pool.csv`, `metamorphic_results.csv`, `branch_flip_results.csv`, and `metamorphic_controls.csv`.

| Number or claim | Audited value | Source artifact |
| --- | ---: | --- |
| Candidate pool | 60 | `metamorphic_candidate_pool.csv` |
| Selected for harness | 60 | `metamorphic_candidate_pool.csv` |
| Harnesses attempted | 60 | `metamorphic_results.csv` |
| Constructed executable harnesses | 39 | `metamorphic_results.csv` |
| Confirmed divergences | 20 | `metamorphic_results.csv` |
| Distinct packages with confirmed divergences | 12 | `metamorphic_results.csv` |
| Output divergences | 17 | `metamorphic_results.csv` |
| Branch divergences | 1 | `metamorphic_results.csv` |
| Exception divergences | 0 | `metamorphic_results.csv` |
| State-only divergences | 2 | `metamorphic_results.csv` |
| Constructed with no divergence | 19 | `metamorphic_results.csv` |
| Failed construction/import/relevance/safety rows | 21 | `metamorphic_results.csv` |
| Caller-level branch flips | 9/9 | `branch_flip_results.csv` |
| Caller-level consequence flips | 9/9 | `branch_flip_results.csv` |
| Negative controls with divergence removed | 19/19 | `metamorphic_controls.csv`; `CONTROL_SUMMARY.md` |
| Control types | determinism 8, fresh_object 8, pure_observation 2, reset_between 1 | `metamorphic_controls.csv` |

Confirmed-divergence packages: PyYAML, anyio, beautifulsoup4, boltons, cerberus, dnspython, docutils, h11, httpcore, markdown, more-itertools, pytest.

The real-code study is selection evidence over curated candidates and constructed harnesses. It is not a PyPI prevalence estimate.

## Older OSDS Result Tables

The existing OSDS result ledger in `results/paper_results_tables.md` reports:

| Claim | Audited value | Source artifact named there |
| --- | ---: | --- |
| Total simulated executions | 2,200,000 | `results/summary.csv` |
| Exhaustive enumeration configurations | 112 | `results/exhaustive_enumeration_summary.json` |
| Exhaustive enumeration mismatches | 0 | `results/exhaustive_enumeration_summary.json` |
| Controlled analyzer benchmark cases | 20 | `analysis/benchmark_examples.py` |
| Controlled analyzer benchmark precision | 0.9231 | `analysis/benchmark_examples.py` |
| Controlled analyzer benchmark recall | 1.0 | `analysis/benchmark_examples.py` |
| Controlled analyzer exact-label accuracy | 0.95 | `analysis/benchmark_examples.py` |
| PyPI packages screened | 73 | `results_static/pypi_static_benchmark_findings.csv` |
| PyPI files screened | 1,858 | `results_static/pypi_static_benchmark_findings.csv` |
| PyPI classes screened | 4,437 | `results_static/pypi_static_benchmark_findings.csv` |
| PyPI functions screened | 21,530 | `results_static/pypi_static_benchmark_findings.csv` |
| Reviewed MEDIUM/HIGH findings | 278 | `results_static/pypi_static_benchmark_findings.csv` |
| Likely true positives | 203 | `results_static/pypi_static_benchmark_findings.csv` |
| Likely false positives | 75 | `results_static/pypi_static_benchmark_findings.csv` |
| Reviewed PyPI precision | 0.7302 | `results_static/pypi_static_benchmark_findings.csv` |

These numbers were already summarized in `results/paper_results_tables.md`. This audit did not rerun those older computations.

## Reporting Inconsistencies Found

The files in `experiments/agent_behavior_preservation/paper_materials/` were Sol-only in places and predated the completed Terra/Luna runs. Specifically, `results.md`, `candidate_abstract.md`, `candidate_tables.md`, `limitations.md`, and `vericodegen_framing.md` should cite the cross-model artifact for the completed primary study and should describe Sol, Terra, and Luna as Codex task-model configurations. They should not report the primary agent study as only a Sol result.

The machine-readable CSV files `model_results.csv`, `evidence_role_results.csv`, `package_results.csv`, `ordinary_vs_osds.csv`, and `self_assessment_results.csv` are Sol-only summaries from an earlier stage. The authoritative completed primary study artifact is `codex_task_model_cross_model_analysis_20260813.json` plus the manual review JSONL. Paper text should avoid mixing the older Sol-only CSV denominators with the completed three-configuration counts.

## Required Paper Wording Constraints

Use these distinctions in the paper and appendix:

- `behavior_preserved`: replayed transformation is executable and passes the OSDS-aware preservation oracle.
- `verified_semantic_divergence`: executable transformation diverges and manual review attributes the divergence to the access-induced mechanism.
- `ordinary_programming_bug`: transformation fails ordinary behavior checks for reasons unrelated to the OSDS mechanism.
- `invalid_patch`: extraction or application produced code that was not valid executable Python for the benchmark.
- `environment_failure`, `oracle_issue`, `unclear`: retained as possible categories, with zero rows in the completed primary manual review.

Keep hidden-observation and expected-access-sensitive outcomes separate. Count silent OSDS divergences only when ordinary smoke tests pass and OSDS-aware checks fail under manual confirmation.
