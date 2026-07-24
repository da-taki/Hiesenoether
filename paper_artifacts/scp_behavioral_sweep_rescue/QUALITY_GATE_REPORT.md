# Quality Gate Report

## Commands Run

- `python run_tests.py`
- `python -m pytest`
- `python -m pytest tests`
- `python paper_artifacts\scp_realworld_revision\run_real_case_harnesses.py`
- `python paper_artifacts\scp_behavioral_sweep_rescue\run_rescue_harnesses.py`

## Results

- Existing core tests: passed, 28/28.
- Repository-wide pytest: not feasible as a quality gate without excluding source snapshots. Collection entered rebuilt third-party package tests under `paper_artifacts/scp_realworld_revision/source_snapshot/` and failed before running project tests because vendored package tests require dependencies/import layouts not present in this workspace.
- Project-scoped pytest: passed, 44/44 with `python -m pytest tests`.
- Previous real-case runner: passed, confirmed=4 total=4.
- Rescue harness runner: passed, 15/15 harnesses executed and JSON was aggregated.

## Artifact Checks

- All rescue JSON outputs are valid and contain the required keys.
- `rescue_candidate_selection.csv` and `rescue_results.csv` have the requested headers.
- Every confirmed rescue case has a runnable harness path in `harnesses/`.
- No failed rescue case is missing a failure reason; this run had no import, construction, external-fixture, unsafe, or not-applicable failures.
- No unfinished-marker text remains in the final rescue markdown artifacts.

## Aggregate Rescue Check

| Rescue selected | Manual harnesses attempted | Branch/output confirmed | State-only confirmed | Structural only | Still could not construct | Import failed | External fixture | Not applicable |
| --------------: | -------------------------: | ----------------------: | -------------------: | --------------: | ------------------------: | ------------: | ---------------: | -------------: |
| 15 | 15 | 9 | 2 | 4 | 0 | 0 | 0 | 0 |
