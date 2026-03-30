# Ordered Chaos — Python Runtime Validation

## What This Validates

This artifact demonstrates that **ordered chaos** — output divergence arising from
access-count-sensitive state, observation-induced perturbation, and nonlinear
composition — emerges in the **Python runtime itself**, not only in the Hiesenoether
language. It provides an independent substrate validation for the claims in
*"Ordered Chaos: Nonlinear Divergence from Observation in Deterministic Programs"*
(Section 7.4).

---

## Rerun Command
```bash
pip install -r real_world_validation/requirements.txt
python real_world_validation/run_validation.py
```

Quick smoke test (< 60 seconds):
```bash
python real_world_validation/run_validation.py --runs 1000
```

---

## Expected Outputs

| Path | Contents |
|---|---|
| `results/summary/descriptor_experiments.csv` | A1 and A3 analogue stats (std, range, cv) by config |
| `results/summary/sle_python_substrate.csv` | SLE, R², CI per nonlinearity degree |
| `results/summary/cache_invalidation_summary.csv` | Cache error % by intervening steps |
| `results/summary/all_experiments_merged.csv` | Merged table across all experiments |
| `results/figures/python_a1_observation.png` | Std and range vs observation count |
| `results/figures/python_sle_fit.png` | log(range) vs degree with fitted SLE line |
| `results/figures/python_cache_invalidation.png` | Cache error % vs drift steps |
| `results/figures/python_a3_length_scaling.png` | Std and marginal Δstd vs program length |
| `results/logs/findings_python.txt` | Plain-text findings in Hiesenoether findings.txt format |
| `results/logs/run.log` | Full timestamped run log |

Expected key metrics (full `NUM_RUNS=100000`):

| Metric | Expected value |
|---|---|
| Python SLE | ~2.78 – 2.80 |
| SLE R² | > 0.98 |
| Zero-observe std | 0.00 |
| Max cache error % (20 steps) | > 10% |
| Observe-invalidation error % | > 0% |

---

## Mapping to Paper Claims

| Experiment | File | Paper Claim |
|---|---|---|
| Descriptor A1 analogue | `exp_descriptor.py` | Std grows super-linearly with observation count (Section 6.1) |
| Descriptor A3 analogue | `exp_descriptor.py` | Marginal std increases are non-decreasing with length (Section 6.3) |
| SLE fitting | `exp_sle_fitting.py` | SLE is measurable outside Hiesenoether; log-linear in nonlinearity degree (Section 6.2) |
| Cache invalidation | `exp_cache_invalidation.py` | Memoization is silently invalidated under drift (Section 7.6) |
| Observe-invalidation | `exp_cache_invalidation.py` | A single observe() call stales a cached read (Section 3.2) |

Three ordered-chaos preconditions and their Python implementations:

| Precondition | Hiesenoether | Python |
|---|---|---|
| Access-count-sensitive state | `UnstableValue.get()` | `UnstableObject.read()` / `UnstableDescriptor.__get__` |
| Observation-induced perturbation | `inspect` keyword | `UnstableObject.observe()` |
| Nonlinear composition | `y * x`, `y * y * x` | cap functions in `run_single()` |

---

## Reproducibility Guarantee

Running `run_validation.py` with the committed `config.py`
(`RANDOM_SEED=42`, `NUM_RUNS=100000`) produces bitwise-identical summary CSVs
to those committed in `results/summary/`. All randomness is fully controlled by
`random.seed(config.RANDOM_SEED)` called once at the start of `run_all()`.
No external data sources, network calls, or platform-dependent operations are used.

---

## Known Limitations

- NumPy subclass extension is not yet implemented (`ENABLE_NUMPY_EXP=False` in `config.py`).
- SLE is fitted from four nonlinearity degrees; treat as theoretically grounded estimate, not high-DoF regression.
- Cache invalidation study is qualitative (small fixed case set), not distributional.

---

## Future Work

- NumPy subclass implementing `__array_ufunc__` with access-count drift.
- Reactive framework analogue (signals, MobX-style computed values).
- Session-type enforcement as a formal prevention mechanism for the preconditions.