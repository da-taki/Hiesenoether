# Prospective OSDS Agent Benchmark Expansion Manifest

Created at: 2026-08-13T16:14:19.883995+00:00

Branch: `experiment/agent-behavior-preservation`
Builder commit before freeze: `f316af08f658524f511d300a5f883e985a5ea781`
Freeze commit: `c198d026fd5ea7ea65650be240b760b0e021ba33`

No model generation has been run on these expansion tasks at manifest creation time.

## Counts

| Metric | Value |
| --- | ---: |
| all_confirmed_real_code_witnesses | 20 |
| current_primary_benchmark_members | 9 |
| unused_confirmed_witnesses | 11 |
| eligible_unused_witnesses | 7 |
| new_base_tasks | 7 |
| new_prompt_variants | 14 |
| validation_all_eligible | True |

## Package Reconstruction

| Package | Installed version |
| --- | --- |
| boltons | `25.0.0` |
| dnspython | `2.8.0` |
| h11 | `0.16.0` |

## Validation

| Task | Baseline | Ordinary smoke | Witness | Prompt leaks | Eligible |
| --- | --- | --- | --- | --- | --- |
| `boltons_lri_stats__repeated_access_cleanup__normal` | True | True | True | 0 | True |
| `boltons_multifile_reader__access_reordering__normal` | True | True | True | 0 | True |
| `h11_receive_buffer__access_reordering__normal` | True | True | True | 0 | True |
| `boltons_spooled_string_io__access_reordering__normal` | True | True | True | 0 | True |
| `boltons_spooled_bytes_io__access_reordering__normal` | True | True | True | 0 | True |
| `dnspython_tokenizer_concat__access_reordering__normal` | True | True | True | 0 | True |
| `boltons_lru_pair2__repeated_access_cleanup__normal` | True | True | True | 0 | True |

## Frozen Artifacts

- `benchmark_expansion/candidate_witnesses.csv`
- `benchmark_expansion/tasks.jsonl`
- `benchmark_expansion/prompts/*.md`
- `benchmark_expansion/validation.json`

The primary benchmark at `experiments/agent_behavior_preservation/benchmark/tasks.jsonl` is not modified by this expansion.

## Environment

Python executable: `C:\Users\Asus\Desktop\Profitlo Projects\Hiesenoether\experiments\agent_behavior_preservation\environment\.venv\Scripts\python.exe`
Python version: `3.14.4 (tags/v3.14.4:23116f9, Apr  7 2026, 14:10:54) [MSC v.1944 64 bit (AMD64)]`
OS: `Windows-11-10.0.26200-SP0`
