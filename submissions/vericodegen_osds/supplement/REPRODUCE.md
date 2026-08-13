# Reproducing the OSDS VeriCodeGen Results

Run these commands from the extracted supplement root. The supplement is anonymized and uses only relative paths.

Model generation is not reproduced here. The raw Codex task-model responses are frozen and included as JSONL files, so replay uses those existing outputs and does not contact proprietary models or require credentials.

## 1. Environment Check

```powershell
py -c "import sys; print(sys.version)"
py -c "import pytest, yaml, h11, httpcore; print('core replay dependencies ok')"
```

For the full real-code oracle beyond the quick check, install the optional packages named in `paper_artifacts/scp_realcode_metamorphic_oracle/METAMORPHIC_ORACLE_REPORT.md` at the recorded versions. The frozen CSV and JSON outputs are included for review even when optional packages are absent.

## 2. Baseline Validation

```powershell
$RID = Get-Date -Format yyyyMMddHHmmss
py experiments/agent_behavior_preservation/runners/run_benchmark.py --provider noop --task-id pytest_catching_logs__instrumentation__normal --run-id "reproduce-baseline-noop-$RID" --timeout-s 8
```

Expected output: one task is replayed, no baseline failures are reported, and a result directory is created under `experiments/agent_behavior_preservation/results/`.

## 3. Frozen Primary Replay

```powershell
$RID = Get-Date -Format yyyyMMddHHmmss
py experiments/agent_behavior_preservation/runners/run_benchmark.py --provider jsonl --replay-path experiments/agent_behavior_preservation/external_collection/responses/gpt-5.6-terra__full_exact.jsonl --task-id pytest_catching_logs__instrumentation__normal --run-id "reproduce-primary-terra-$RID" --timeout-s 8
```

Expected output: one frozen Terra primary response is extracted and executed from the included JSONL. The resulting row preserves the raw response and writes `results.jsonl` plus `candidates/pytest_catching_logs__instrumentation__normal/candidate.py` under the new run directory.

## 4. Prospective Expansion Replay

```powershell
$RID = Get-Date -Format yyyyMMddHHmmss
py experiments/agent_behavior_preservation/runners/run_benchmark.py --tasks benchmark_expansion/tasks.jsonl --provider jsonl --replay-path benchmark_expansion/responses/gpt_5_6_luna__expansion.jsonl --task-id h11_receive_buffer__access_reordering__normal --run-id "reproduce-prospective-luna-$RID" --timeout-s 8
```

Expected output: one frozen Luna prospective response is extracted and executed from the included expansion JSONL, with a new result directory under `experiments/agent_behavior_preservation/results/`.

## 5. Five-Case Causal Controls

```powershell
py experiments/agent_behavior_preservation/causal_controls/run_model_failure_causal_controls.py --no-write
```

Expected output: `records` is 5 and `causal_status_counts` reports 5 `mechanism_neutralized_divergence_disappeared` records. This command reads the included frozen primary `candidate.py` files and result JSONLs.

## 6. Real-Code Metamorphic Evidence

```powershell
py paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py
```

Expected output: fixture-family construction status is printed. The already frozen real-code evidence tables are `paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_results.csv`, `branch_flip_results.csv`, and `metamorphic_controls.csv`.

## 7. Key Analysis Tables

```powershell
py scripts/summarize_replay_counts.py
```

Expected output: primary replay row counts, prospective task-compliance counts, and five-case causal-control counts are printed from the included frozen artifacts.

## Expected Reported Counts

- Primary causal controls: 5/5 original model OSDS failures reproduce and 5/5 disappear under mechanism-neutralizing controls.
- Prospective expansion: 42 outputs, 23 task-compliant transformations, 19 unchanged outputs, 0 other noncompliant outputs, 23/23 task-compliant transformations OSDS-preserving, and 0/42 verified prospective OSDS divergences.
- Real-code oracle: 20 confirmed real-package divergences across 12 packages, 9 caller-level effects, and 19/19 real-code mechanism controls removing the targeted divergence.
