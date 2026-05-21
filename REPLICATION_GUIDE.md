# Replication Guide

This guide collects the commands needed to reproduce the current evidence
without editing manuscript files.

These replications are author-implemented. Independent third-party replication remains future work.

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
