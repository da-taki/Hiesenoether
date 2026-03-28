# Hiesenoether - Ordered Chaos in Deterministic Computation

## Overview

Hiesenoether is a deterministic programming language designed to explore how **execution order and observation affect computation**.

Unlike traditional models where programs produce a single fixed output, Hiesenoether demonstrates that:

> Deterministic programs can produce **structured output distributions** purely through execution-order-dependent state evolution, without any randomness.

---

## Core Idea

Hiesenoether introduces:

* **Unstable values** that evolve on access
* **Observation (`inspect`)** that modifies system state (entropy injection)
* **Energy-bounded execution** controlling guarantees

This makes **execution order a semantic parameter**, not just an implementation detail.

---

## Key Finding

Through **2,200,000 executions across 22 configurations**, we observe:

> Deterministic programs exhibit **strong superadditive divergence**, where combined effects of observation, nonlinearity, and program length exceed the sum of individual effects by ~590×.

This divergence is:

* **Deterministic** (no randomness involved)
* **Structured** (not noise)
* **Amplified by nonlinearity**
* **Driven by observation timing**

---

## Experimental Results

### Scale

* 22 configurations
* 100,000 runs per configuration
* **2.2 million executions total**
* Runtime: ~10 minutes (optimized in-process execution)

---

### Axes Explored

1. **Observation multiplicity (inspect count)**
2. **Nonlinearity depth (linear → extreme)**
3. **Program length (3 → 20 steps)**
4. **Interaction effects (combined factors)**

---

### Highlights

* **Super-linear growth with observation**

  * std increases **5.18×** from 1 → 5 inspects

* **Exponential amplification via nonlinearity**

  * log(range) scales linearly (R² ≈ 0.99)
  * Semantic Lyapunov-like coefficient ≈ **2.79**

* **No plateau in program length**

  * divergence grows continuously with execution depth

* **Superadditivity (core result)**

  * Combined std: **8,209,836**
  * Sum of isolated stds: **13,894**
  * Ratio: **~590×**

---

## Repository Structure

```
src/                # Interpreter implementation
docs/               # Language model and semantics
tests/              # Runtime tests
examples/           # Example programs

run_experiments.py  # Full experiment pipeline

results/
  ├── summary.csv           # Per-configuration metrics
  ├── A1/A2/A3/A4.csv       # Axis summaries
  ├── raw_*.csv             # Full 100k outputs per config
  ├── findings.txt          # Human-readable results
  ├── findings.json         # Structured results
  └── checkpoint.json       # Resume state
```

---

## Reproducibility

To reproduce all experiments:

```bash
python -m src.main examples/basic_energy.hn
python run_experiments.py
```

All results are deterministic and reproducible.

---

## Research Direction

This project investigates:

* Execution-order-dependent semantics
* Observation as a state-changing operation
* Nonlinear amplification in deterministic systems
* Emergent behavior from interacting computational factors

---

## Status

* ✅ Interpreter complete
* ✅ Experiment pipeline complete
* ✅ 2.2M executions completed
* ✅ Results analyzed
* ⏳ Paper in progress

---

## Author

Taknoor Singh (Taki)

---

## Note

This project focuses on **measurable properties of deterministic computation**, not probabilistic or stochastic systems.
