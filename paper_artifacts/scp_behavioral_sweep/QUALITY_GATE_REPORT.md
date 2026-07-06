# Quality Gate Report

## Commands Run

| Check | Command | Status | Notes |
| --- | --- | --- | --- |
| Core tests | bundled Python `run_tests.py` | passed | 28 passed, 0 failed |
| Pytest suite | bundled Python `-m pytest tests -q` | passed | 44 passed |
| Previous real-case runner | bundled Python `paper_artifacts/scp_realworld_revision/run_real_case_harnesses.py` | passed | 4 confirmed / 4 attempted |
| Behavioral sweep runner | bundled Python `paper_artifacts/scp_behavioral_sweep/run_behavioral_sweep.py` | passed | 50 selected, 50 harnesses attempted, 4 confirmed state-only, 4/4 controls passed |
| JSON validation | parsed all `paper_artifacts/scp_behavioral_sweep/**/*.json` | passed | 54 JSON files valid |
| CSV headers | checked all top-level sweep CSV files | passed | headers present |
| Placeholder scan | searched new sweep markdown files for placeholder markers | passed | no placeholder matches |

## Output Integrity

- Every selected candidate has a generated runnable harness under `harnesses/`.
- Every selected candidate has a JSON output under `outputs/`.
- Every confirmed case has a runnable harness and JSON output.
- Failed or skipped behavior attempts have explicit `classification` and `failure_reason` fields in `behavioral_sweep_results.csv`.
- Previous four controls are separated in `control_case_results.csv` and `control_outputs/`.

## Skipped Checks

No requested checks were skipped. The analyzer-specific pytest path is covered by the repository pytest suite available in this checkout.
