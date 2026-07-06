# Repository Audit

## Structure Summary

| Area | Location | Notes |
| --- | --- | --- |
| OSDS interpreter | `src/` | Runtime and language implementation; `src/runtime.py`, `src/values.py`, parser/lexer/AST/energy modules. |
| Exact semantics | `validation/exact_semantics.py` | Uses `fractions.Fraction` for exact rational OSDS replay. |
| Experiments | `run_experiments.py`, `run_extended_experiments.py`, `scripts/scp_new_experiments/`, `real_world_validation/`, `substrates/reactive_py/` | Original, extended, descriptor, reactive, and new SCP experiment suites. |
| Current summaries | `results/`, `results_extended/`, `results_validation/`, `results/scp_new_experiments/`, `results_static/` | Paper tables, exact validation summaries, static analyzer summaries. |
| Analyzer | `analysis/oc_static.py`, `analysis/pypi_static_benchmark.py`, `analyzer/` | Static analyzer and abstract-interpreter sketches/tests. |
| Analyzer outputs | `results_static/pypi_static_benchmark*.csv`, `results/scp_new_experiments/pypi_expanded_*` | Reviewed PyPI findings and expanded screening artifacts. |
| PyPI metadata/results | `results_static/pypi_static_benchmark.csv`, `results_static/pypi_static_benchmark_findings.csv` | 73 packages, 4437 classes, 278 reviewed MEDIUM/HIGH findings. |
| Controlled labels | `analysis/benchmark_examples.py`, `benchmarks/controlled_extended/extended_examples.py`, `results/scp_new_experiments/extended_controlled_benchmark_summary.json` | Controlled benchmark labels and summary metrics. |

## Environment

System `python` and `py` were not available. The Codex bundled runtime was used:

- Python: `3.12.13`
- Executable: `C:\Users\Asus\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`
- Selected packages: `pytest 8.3.5`, `pandas 3.0.1`, `numpy 2.3.5`, `requests 2.32.4`, `packaging 26.2`, `ruff 0.15.20`

## Exact Rational Replay

Exact rational replay is used in `validation/exact_semantics.py`, `validation/polynomial_degree_extended.py`, `validation/rho_infinity_investigation.py`, and the new `paper_artifacts/validate_polynomial_degree_theorem.py`. These scripts serialize rational values as `numerator/denominator`.

## Commands Successfully Run

| Command | Result |
| --- | --- |
| bundled Python `run_tests.py` | 28 passed, 0 failed |
| bundled Python `-m pytest tests -q` | 44 passed |
| bundled Python `-m validation.run_all` | `ALL PASS`, wrote `validation/results.json` |
| bundled Python `-m validation.rho_infinity_investigation` | 34 checked, 0 failures |
| bundled Python `paper_artifacts/validate_polynomial_degree_theorem.py` | 20 checked, 0 corrected-2d failures |
| bundled Python `paper_artifacts/sample_unflagged_recall_audit.py` | Wrote missing-data fallback audit |
| bundled Python `paper_artifacts/real_named_case_reproduction.py` | Reproduced `__getattr__` diagnostic side effect |

## Commands That Failed Or Timed Out

| Command | Reason |
| --- | --- |
| `python --version` | `python` not on PATH |
| `python -m pip list` | `python` not on PATH |
| `py --version` | Windows launcher found no installed Python |
| `py -m pip list` | Windows launcher found no installed Python |
| bundled Python `-m validation.polynomial_degree_extended` with 120s timeout | Timed out; existing result files remain in `results_validation/` |
| recall audit with reviewed-corpus source reacquisition | Timed out after 5 minutes, then again after 15 minutes with escalation |

## Missing Files/Data

The reviewed PyPI benchmark preserves aggregate counts and reviewed flagged findings, but the corresponding reviewed-corpus source trees are not available in the repo/cache in a usable form. Therefore a deterministic 200-class audit of unflagged reviewed-corpus classes could not be computed from the current checkout. The new audit script emits an explicit missing-data fallback using the available expanded SAFE queue rows and does not estimate recall.

