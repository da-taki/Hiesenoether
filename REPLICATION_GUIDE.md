# Replication Guide

This guide collects the commands needed to reproduce the current evidence
without editing artifact files.

These replications are repository-local. Independent third-party replication remains future work.

## Environment

- Python 3.11 or newer is recommended.
- Run commands from the repository root.
- The PyPI-scale static analyzer benchmark requires network access the first
  time it downloads package archives. Other commands are local.

## Interpreter Experiments

Run the original interpreter experiment suite:

```powershell
py run_experiments.py
```

Expected output: regenerated experiment CSVs under `results/` and a textual
summary of findings.

For extended experiment sweeps:

```powershell
py run_extended_experiments.py
```

Expected output: extended CSVs under `results_extended/`.

## Descriptor Substrate Results

Run the Python descriptor validation suite:

```powershell
py -m real_world_validation.run_validation
```

Expected output: descriptor, cache-invalidation, and Python-substrate summaries
under `real_world_validation/results/summary/`.

## Reactive Substrate Results

Run the reactive substrate validation:

```powershell
py -m substrates.reactive_py.run_validation
```

Expected output: raw and summary CSVs under
`substrates/reactive_py/results/`.

## Theorem Validation

Run the full validation suite:

```powershell
py -m validation.run_all
```

Expected output includes `ALL PASS` and updates `validation/results.json`.

Run the extended polynomial-degree evidence:

```powershell
py -m validation.polynomial_degree_extended
```

Expected output:

- `results_validation/polynomial_degree_extended.csv`
- `results_validation/polynomial_degree_extended_summary.md`

Run the rho-infinity investigation:

```powershell
py -m validation.rho_infinity_investigation
```

Expected output:

- `results_validation/rho_infinity_investigation.csv`
- `results_validation/rho_infinity_investigation_summary.md`

## Static Analyzer Benchmarks

Run the toy benchmark:

```powershell
py -m analysis.oc_static_benchmark
```

Expected output: JSON metrics for the curated toy cases.

Run the PyPI benchmark:

```powershell
py -m analysis.pypi_static_benchmark
```

Expected output:

- `results_static/pypi_static_benchmark.csv`
- `results_static/pypi_static_benchmark_findings.csv`
- `results_static/pypi_static_benchmark_summary.md`

This command may take several minutes on a cold cache because it downloads and
extracts PyPI source or wheel archives.


## Real-Code Metamorphic Oracle

The stored real-code oracle numbers are in `paper_artifacts/realcode_metamorphic_oracle/metamorphic_results.json` and `.csv`: 60 selected candidates, 39 constructed harnesses, and 20 confirmed divergences across 12 packages. The same directory also contains per-candidate traces, branch-flip outputs, and control summaries.

To rerun the oracle for the stored result, first rebuild or provide the exact-version source snapshot at `paper_artifacts/realworld_package_study/source_snapshot/` from `paper_artifacts/realworld_package_study/corpus_manifest.csv` and `source_snapshot_manifest.csv`. The pinned package set used by the candidate pool is: httpcore 1.0.9, PyYAML 6.0.3, pytest 8.3.5, rich 15.0.0, markdown 3.10.2, more-itertools 11.0.2, pygments 2.20.0, docutils 0.22.4, soupsieve 2.8.3, beautifulsoup4 4.14.3, boltons 25.0.0, cerberus 1.3.8, dnspython 2.8.0, h11 0.16.0, click-option-group 0.5.9, anyio 4.13.0, tomlkit 0.15.0, marshmallow 4.3.0, and mistune 3.2.1.

```powershell
py paper_artifacts/realcode_metamorphic_oracle/run_metamorphic_oracle.py
```

A reduced local environment without the source snapshot may construct only candidates whose packages are already installed. Those reduced runs are useful setup diagnostics, but they do not reproduce the stored 39-constructed / 20-confirmed evidence. Do not overwrite the committed oracle result files with reduced-environment outputs.

## One-Command Runner

For local, non-network validation commands:

```powershell
py scripts/run_replication_suite.py
```

To include the network-dependent PyPI benchmark:

```powershell
py scripts/run_replication_suite.py --include-pypi
```

## Hardware And Time Expectations

On a typical laptop, `validation.run_all` can take around two minutes because
it includes exact permutation checks. The PyPI static benchmark is usually
faster on a warm cache and slower on first run due to downloads. The extended
polynomial and rho scripts are intended to run in seconds to minutes.

## Interpreting Failures

- Network failures in the PyPI benchmark usually indicate package download
  issues rather than analyzer logic failures.
- Exact validation failures should be treated as evidence regressions and
  investigated before updating claims.
- The extended polynomial script intentionally reports that the checked data do
  not support an unqualified `d+2` degree claim beyond the narrow historical
  cases.
