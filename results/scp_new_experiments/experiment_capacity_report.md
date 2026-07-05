# Experiment Capacity Report

Repository audited: `C:\Users\Asus\Desktop\Profitlo Projects\Hiesenoether`

Remote: `https://github.com/da-taki/Hiesenoether.git`

## Existing Experiments

- `run_experiments.py`: original Hiesenoether runtime experiment battery, 22 configurations, 100,000 executions each, 2.2 million executions total.
- `python_sim/run_cross_experiments_2m.py`: older Python simulation producing `python_sim/results_2m/summary_2.2m.csv`.
- `run_extended_experiments.py`: extended empirical axes written to `results_extended/`.
- `validation/run_all.py`: exact-rational and runtime-cross-check validation suite.
- `validation/exhaustive_permutation_check.py`: original exact small-configuration exhaustive enumeration, 112 configurations.
- `validation/theorem_*`: bounded checks for determinism, conservation, permutation sensitivity, necessity, polynomial structure, length scaling, degree amplification, entropy decay, and runtime correspondence.
- `analysis/oc_static_benchmark.py`: 20-class controlled Python analyzer benchmark.
- `analysis/pypi_static_benchmark.py`: 73-package PyPI static analyzer screen with manually reviewed MEDIUM/HIGH findings in existing results.

## Sweepable Parameters

- Body length / read count: already used from 2 through 20 in existing experiments; exact OSDS evaluation can sweep larger values with sampling.
- Observation count: existing exact and empirical scripts cover 0 through 5 in different places; new exact sampling can cover 0 through 10.
- Cap degree: existing paper tables cover 1 through 4; exact compositional caps can be evaluated beyond that, with practical numeric growth.
- Operation order: exact enumeration is feasible when `comb(reads + observations, observations)` is small; otherwise sampled permutations are required.
- Drift schedule: existing `validation/theorem_T5_entropy_decay.py` supports constant, linear-decay, and exponential-decay entropy increments under exact `Fraction` arithmetic.
- Analyzer risk labels: the analyzer emits SAFE, LOW, MEDIUM, HIGH class labels plus module-level nonlinear-use evidence.

## Analyzer Corpora

- Controlled corpus: `analysis/benchmark_examples.py`, 20 labeled classes.
- Existing examples: `analysis/examples/`.
- PyPI corpus: 73 packages listed in `analysis/pypi_static_benchmark.py`, with package-level CSV and MEDIUM/HIGH finding CSV under `results_static/`.
- Local PyPI cache, if present: `%TEMP%/hiesenoether_pypi_static_benchmark`.

## PyPI Expansion Feasibility

The code can expand the PyPI corpus by downloading additional source or wheel distributions with `pip download --no-deps`, extracting them, then running `analysis.oc_static.analyze_file` over non-test Python files. This depends on network/package-index availability. If downloads are unavailable, the new expanded screen reuses the local cache and records the limitation in `NEW_EXPERIMENT_GAPS.md`.

## Controlled Benchmark Expansion Feasibility

The 20-class benchmark can be expanded directly because labels are encoded as `expected_risk` class attributes. The new controlled benchmark uses the same analyzer and adds at least 40 new classes under `benchmarks/controlled_extended/`, while keeping the original 20-class corpus intact.

## Numbers Recomputable From Raw Data

- Main 2.2M execution count from `results/summary.csv` by summing `n_valid`.
- Observation-count sweep table from `results/A1.csv`.
- Cap-degree sweep table from `results/A2.csv`.
- Ablation table from `results_extended/e3_ablation_comparison.csv`.
- Exhaustive permutation ranges from exact OSDS semantics.
- Controlled analyzer TP/FP/TN/FN, precision, recall, specificity, F1, and exact-label accuracy from labeled classes.
- Existing PyPI package/file/class/function and analyzer-label counts from `results_static/pypi_static_benchmark.csv`.
- Existing reviewed PyPI precision from `results_static/pypi_static_benchmark_findings.csv`.

## Numbers Needing New Data Collection

- Larger exact-rational mechanism sweeps over body lengths 30 and 50, observation counts up to 10, cap degrees up to 8, and decay schedules.
- Extended exhaustive enumeration beyond the original 112 configurations.
- Sampling convergence behavior for known exhaustive configurations.
- Expanded controlled benchmark metrics over at least 60 labeled classes.
- Expanded PyPI screen beyond 73 packages if downloads or local cached packages are available.
- Manual review labels for expanded PyPI findings and the LOW/SAFE false-negative queue; these are intentionally left blank.
