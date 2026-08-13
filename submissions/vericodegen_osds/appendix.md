# Appendix

## A. Formal Boundary

The formal core models a deterministic straight-line template over a semantic value `(b, a, d)` and an accumulator `y`. A read transition exposes `f(b, a, d)`, increments access count, and may update latent drift. An observation transition exposes no additive value and updates only latent drift through `g`. Body execution is a deterministic fold over the operation list, followed by a deterministic cap.

The proved claims are fixed-order determinism, zero divergence for identity observations, zero divergence for access-insensitive reads, and preservation of body-level divergence by a nonzero-slope linear cap. The proof core does not claim universal nonlinear amplification, analyzer soundness, arbitrary Python soundness, or production prevalence.

## B. Real-Code Oracle Summary

The real-code oracle selected 60 candidates and constructed 39 executable harnesses. It confirmed 20 divergences across 12 packages. The confirmed divergences comprise 1 branch divergence, 17 output divergences, and 2 state-only divergences. Nine caller-level wrappers converted confirmed divergences into downstream branch consequences. Nineteen negative controls removed the divergence under fresh-object, reset-between, or pure-observation interventions.

## C. Primary Benchmark Matrix

| Model | Tasks | Executable | Preserved | Ordinary bugs | Invalid patches | Verified OSDS | Silent OSDS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt-5.6-sol | 26 | 26 | 23 | 3 | 0 | 0 | 0 |
| gpt-5.6-terra | 26 | 24 | 18 | 4 | 2 | 2 | 2 |
| gpt-5.6-luna | 26 | 24 | 17 | 4 | 2 | 3 | 3 |

Verified OSDS rows:

| Model | Task | Mechanism |
| --- | --- | --- |
| gpt-5.6-terra | pytest_catching_logs__instrumentation__normal | handler level changed by logging-shaped access |
| gpt-5.6-terra | pytest_catching_logs__instrumentation__warned | handler level changed by logging-shaped access |
| gpt-5.6-luna | pytest_catching_logs__instrumentation__normal | handler level changed by logging-shaped access |
| gpt-5.6-luna | pytest_catching_logs__instrumentation__warned | handler level changed by logging-shaped access |
| gpt-5.6-luna | pyyaml_representer__caching_materialization__normal | identity/access cache state reused after observation |

## D. Causal-Control Matrix

| Failure family | Rows | Original replay | Controlled replay | Causal status |
| --- | ---: | --- | --- | --- |
| pytest catching_logs instrumentation | 4 | ordinary-pass, OSDS-fail | OSDS-pass | mechanism_neutralized_divergence_disappeared |
| PyYAML representer caching | 1 | ordinary-pass, OSDS-fail | OSDS-pass | mechanism_neutralized_divergence_disappeared |

All five exact generated transformations were preserved byte-identically during the control experiment.

## E. Prospective Expansion Matrix

| Model | Tasks | Executable | Preserved | Ordinary bugs | Invalid patches | Verified OSDS | Silent OSDS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gpt-5.6-sol | 14 | 14 | 14 | 0 | 0 | 0 | 0 |
| gpt-5.6-terra | 14 | 14 | 14 | 0 | 0 | 0 | 0 |
| gpt-5.6-luna | 14 | 14 | 14 | 0 | 0 | 0 | 0 |

Expansion witnesses:

| Witness | Package | Family |
| --- | --- | --- |
| re07_boltons_LRI | boltons | repeated_access_cleanup |
| re09_boltons_MultiFileReader | boltons | access_reordering |
| re13_h11_ReceiveBuffer | h11 | access_reordering |
| bs15_boltons_SpooledStringIO | boltons | access_reordering |
| ext02_boltons_SpooledBytesIO | boltons | access_reordering |
| ext07_dnspython_Tokenizer_concat | dnspython | access_reordering |
| ext08_boltons_LRU_pair2 | boltons | repeated_access_cleanup |

All expansion rows are expected-access-sensitive. Hidden-observation rows are present in the primary benchmark only.

## F. Reproducibility Pointers

Primary benchmark tasks are under `experiments/agent_behavior_preservation/benchmark/tasks.jsonl`. The prospective expansion tasks are under `benchmark_expansion/tasks.jsonl`, with frozen prompts in `benchmark_expansion/prompts/`. Raw Codex task-model expansion responses are saved under `benchmark_expansion/responses/`. Replays use `experiments/agent_behavior_preservation/runners/run_benchmark.py --provider jsonl --task-ids-from-replay`.

The causal controls are under `experiments/agent_behavior_preservation/causal_controls/` and produce `analysis/model_failure_causal_controls.csv` and `.md`. The expansion summary artifacts are `analysis/prospective_expansion_results.csv`, `analysis/prospective_expansion_results.md`, and `analysis/model_differential_cases.md`.
