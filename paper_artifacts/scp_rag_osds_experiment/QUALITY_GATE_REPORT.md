# Quality Gate Report

## Experiment Gates

- JSON valid: true (`rag_osds_results.json` and `rag_osds_replay_check.json` written by Python JSON encoder).
- CSV headers present: true (`rag_osds_results.csv` and `rag_osds_ablation.csv`).
- Replay check passed: True.
- At least one baseline no-divergence scenario exists: True.
- At least one feedback scenario shows retrieval or answer divergence: True.
- Feedback weight 0 removes divergence: True.

## Counts

- Scenarios: 7
- Answer divergences: 4
- Top-k retrieval-order changes: 4
- Retrieval-order-only divergences: 0
- State-only divergences: 1
- No divergence: 2

## Project Test Gates

- `C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe run_tests.py`: passed, 28/28.
- `C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pytest tests`: passed, 44/44.
