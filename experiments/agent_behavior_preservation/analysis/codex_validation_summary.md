# Codex Task-Model Validation Summary

Run ID: `codex-gpt-5-6-sol-validation-normal-exact-20260813T0550Z`

This is the six-task normal-prompt validation subset only. It is not the full 26-variant experiment.

## Execution

- Generations attempted: 6
- Patches extracted/applied: 6
- Executable candidates: 6
- Preserved: 6
- Verified semantic divergences after manual review: 0
- Silent semantic divergences: 0
- Silent false-preservation cases: 0

## Self-Assessment

- YES claims: 3
- NO claims: 3
- UNCLEAR claims: 0
- False YES claims: 0
- False NO claims against the replay oracle: 3

## Manual Verification

All six corrected exact responses were extracted as complete Python candidate files, executed in isolated candidate directories, and compared against the baseline fixture. Ordinary smoke checks and OSDS-aware checks both passed for all six. No candidate entered the manual divergence queue for the corrected exact replay.

Earlier replay artifacts using all 26 tasks or compact flattened output are documented in `invalidated_runs.jsonl` and excluded from analysis.
