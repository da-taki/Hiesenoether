# Real-World Revision Repository Audit

## Paths Discovered

| Item | Path | Status |
| --- | --- | --- |
| 278 reviewed flagged findings | `results_static/pypi_static_benchmark_findings.csv` | available |
| 203 likely PyPI matches | rows with `manual_review=likely true positive` in `results_static/pypi_static_benchmark_findings.csv` | available |
| 73-package corpus summary | `results_static/pypi_static_benchmark.csv` | available |
| analyzer implementation | `analysis/oc_static.py` | available |
| PyPI benchmark runner | `analysis/pypi_static_benchmark.py` | available |
| original temp source cache | `%TEMP%/hiesenoether_pypi_static_benchmark/sources` | package directories present, reviewed package trees mostly unusable skeletons |
| rebuilt stable snapshot | `paper_artifacts/scp_realworld_revision/source_snapshot/` | 73/73 exact versions reacquired |

## Source Availability

The original temp cache contained directories for reviewed packages such as `attrs`, `click`, and `cachetools`, but those exact reviewed trees had zero `.py` files. Package download was blocked in the sandbox (`WinError 10013`) and succeeded after escalation. The stable rebuilt snapshot reacquired exact wheel/source archives for all 73 reviewed packages.

Snapshot manifest:

`paper_artifacts/scp_realworld_revision/source_snapshot_manifest.csv`

Snapshot status:

| source_status | packages |
| --- | ---: |
| reacquired_exact | 73 |

The rebuilt snapshot has 4383 analyzable classes. The original published summary reports 4437 classes, so recall-v2 is a rebuilt-snapshot audit rather than a byte-for-byte replay of the original corpus scan.

## Preserved Metadata

The reviewed findings preserve package, version, file path, class name, starting line, analyzer label, mechanisms, short reason, manual review label, and manual review note. Full line ranges were not preserved in the reviewed findings, but line ranges are recovered from AST for rebuilt snapshot classes where source is available.

## Commands Tried

Successful:

- bundled Python `paper_artifacts/scp_realworld_revision/build_source_snapshot.py --download --timeout 45`
- bundled Python `paper_artifacts/scp_realworld_revision/mine_real_case_candidates.py`
- bundled Python `paper_artifacts/scp_realworld_revision/run_real_case_harnesses.py`
- bundled Python `paper_artifacts/scp_realworld_revision/sample_unflagged_recall_audit_v2.py`
- bundled Python `paper_artifacts/scp_realworld_revision/adjacent_swap_extrema_analysis.py`
- bundled Python `run_tests.py`
- bundled Python `-m pytest tests -q`

Failed or constrained:

- `python --version`: `python` not on PATH.
- `py --version`: launcher found no installed Python.
- sandboxed `pip download cachetools==7.1.3`: failed with `WinError 10013`.
- web search for a verifiable Duktape GH-303 source: no usable result returned.

## Environment

Python executable:

`C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

Python version:

`Python 3.12.13`

Selected package versions:

- `httpcore 1.0.9`
- `pytest 8.3.5`
- `requests 2.32.4`
- `packaging 26.2`
- `numpy 2.3.5`
- `pandas 3.0.1`

## Internet/Package Download

Direct package download is not available inside the sandbox. Exact-version PyPI downloads are available when the command is run with approved escalation.

