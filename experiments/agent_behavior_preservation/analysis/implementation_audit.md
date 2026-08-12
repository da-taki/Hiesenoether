# Implementation Audit

Audited from commit `5eafdc724fdd38aed3a9ff41dd06cd27db65679a` before extending the experiment.

## Reused Infrastructure

- Benchmark/task generation under `agent_bp/cases.py`.
- Schema validation under `agent_bp/schema.py`.
- Isolated candidate execution under `agent_bp/execution.py`.
- Local control providers and JSONL replay provider under `agent_bp/providers.py`.
- Existing real-code metamorphic oracle, branch wrappers, and controls under `paper_artifacts/scp_realcode_metamorphic_oracle/`.

## Weaknesses Found

1. Normal and warned prompts were not true pairs: different transformation families were sometimes used for normal versus warned tasks.
2. Task metadata did not include `witness_id`, `package_id`, or `pair_id`, preventing witness/package-aware analysis.
3. The active checkout lacked the source snapshot directory, and the global interpreter missed several exact package versions, causing 12/26 baseline failures.
4. Prompt generation did not remove stale generated prompt files when task IDs changed.
5. Baseline validation was only implicit in control runs, not recorded as a per-task eligibility table.
6. Provider discovery was not recorded in a machine-readable, no-secret format.
7. JSONL replay did not parse raw self-assessment text into YES/NO/UNCLEAR.

## Changes Made

- Rebuilt the 26-task benchmark as 13 paired base tasks, each with normal and warned variants.
- Added `witness_id`, `package_id`, and `pair_id` metadata.
- Reconstructed exact package versions in a repository-local venv and recorded exact-version status.
- Added benchmark balance, leakage, provider discovery, and baseline validation reports.
- Refreshed pipeline controls on 26/26 executable tasks.
- Added self-assessment parsing and tests for replay import.

## Remaining Boundary

No authenticated external coding-model provider was available. Real-model results are therefore not claimed in this phase.
