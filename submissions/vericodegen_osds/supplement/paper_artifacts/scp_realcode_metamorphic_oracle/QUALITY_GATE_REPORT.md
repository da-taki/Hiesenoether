# Quality Gate Report

All gates were run on Windows 11 with the bundled **`py` launcher (CPython 3.14.4)**.

> **Interpreter note.** `python` is **not** on this machine's PATH (it resolves to the
> Windows Store app-execution-alias shim). Every command below therefore uses the bundled
> `py` launcher instead of `python`. This is expected and does not affect results.

## Commands run

| Gate | Command | Result |
|---|---|---|
| Fixture self-test | `py .../metamorphic_fixtures.py` | ✅ all 13 families build |
| Metamorphic oracle | `py .../run_metamorphic_oracle.py` | ✅ 60 selected, 39 constructed, 20 confirmed |
| Branch-flip study | `py .../run_branch_flip_cases.py` | ✅ 9/9 confirmed branch flips |
| Negative controls | `py .../run_metamorphic_controls.py` | ✅ 19/19 divergence removed |
| JSON validation | `json.load` on both result JSONs + 60 traces | ✅ 0 malformed |
| CSV header validation | 4 CSVs vs expected headers | ✅ all match |
| Project test runner | `py run_tests.py` | ✅ 28 passed, 0 failed |
| Project pytest suite | `py -m pytest tests` | ✅ 44 passed, 0 failed |

## Validation checklist

- ✅ **Candidate pool created** — `metamorphic_candidate_pool.csv`, 60 rows.
- ✅ **≥ 60 selected** — 60/60 candidates have `selected_for_harness = yes`.
- ✅ **Every selected candidate has a classification** — 0 result rows missing a
  `classification`; 0 selected candidates missing a result row.
- ✅ **Every confirmed divergence has a trace JSON** — 20/20 confirmed candidates have a
  file under `traces/` (60 trace files total, all valid JSON).
- ✅ **Branch-flip file created** — `branch_flip_results.{json,csv}` (9 rows).
- ✅ **Controls attempted for confirmed divergences** — `metamorphic_controls.csv`, 19
  controls covering 8 confirmed cases (determinism / fresh_object / reset_between /
  pure_observation); all `divergence_removed = True`.
- ✅ **No unresolved placeholders in final reports** — verified across `METAMORPHIC_ORACLE_REPORT.md`,
  `CONTROL_SUMMARY.md`, `INPUT_ARTIFACTS_FOUND.md`, this file.
- ✅ **Existing project tests still pass** — 28 (`run_tests.py`) + 44 (`pytest tests`) = 72
  tests, 0 failures. No third-party package source was modified.

## Determinism

`run_metamorphic_oracle.py`, `run_branch_flip_cases.py`, and `run_metamorphic_controls.py`
are deterministic (fixed fixtures, no randomness, no network). Re-running reproduces
identical JSON/CSV. The two `pytest` cache warnings on Windows are unrelated to this study.

## Headline numbers

| Metric | Value |
|---|---|
| Candidates selected | 60 |
| Harnesses attempted | 60 |
| Constructed | 39 |
| Output divergences | 17 |
| Exception divergences | 0 |
| Branch divergences | 1 |
| State-only divergences | 2 |
| Confirmed divergences (total) | 20 (across 12 packages) |
| No divergence | 19 |
| Failed (could-not-construct / import-failed / not-relevant / unsafe) | 21 (14 / 3 / 2 / 2) |
| Caller branch flips confirmed | 9 / 9 |
| Negative controls (divergence removed) | 19 / 19 |
