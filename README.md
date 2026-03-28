# Hiesenoether

> *"Deterministic programs can exhibit high-variance, structurally sensitive outputs, not through randomness, but through the interaction of execution order, observation, and nonlinear computation."*

Hiesenoether is an experimental programming language and research platform built to study a single question: **can a fully deterministic system produce chaotic output?**

The answer, demonstrated empirically across 2.2 million program executions, is yes.

---

## What This Is

Hiesenoether is two things simultaneously:

**A programming language** with unusual semantics. Values are unstable by default, each access to an unguarded variable advances its internal state deterministically, producing a value that depends on the cumulative history of prior accesses. Observation is not passive: the `inspect` primitive costs energy and permanently increases a variable's entropy, altering every future access. Stability must be purchased explicitly, at a cost.

**A research instrument** for studying ordered chaos, structured, reproducible, yet dramatically divergent behavior arising purely from differences in when and how values are observed, and in what sequence operations are applied. The language makes these effects measurable and controllable in a way no general-purpose language does.

---

## Core Ideas

### Unstable Values

Values in Hiesenoether are unstable by default. Each access evolves the value deterministically according to:

```
drift      = access_count × entropy
returned   = base_value + drift
access_count += 1
entropy      += 0.1
```

This means the same variable returns different values depending on how many times it has been accessed before. Reordering statements changes program output. There is no randomness, only order-dependence.

```
x <- 10

print x   →  10.0   (access 0: drift = 0 × 1.0 = 0)
print x   →  11.1   (access 1: drift = 1 × 1.1 = 1.1)
print x   →  12.4   (access 2: drift = 2 × 1.2 = 2.4)
```

### Observation as Perturbation

The `inspect` operation reveals a variable's internal state, but it is not passive. On a successful inspection, the variable's entropy increases by 1.0, permanently altering the trajectory of all future accesses. This is enforced by the runtime, not optional. Observation changes what it observes.

```
inspect x   →  reveals {base: 10, access_count: 3, entropy: 1.3}
              AND sets entropy to 2.3 for all future accesses
```

### Energy as Guarantees

Every program begins with a finite energy budget. Guarantees cost energy:

| Operation | Cost |
|-----------|------|
| Stable variable | −5 energy |
| Stabilize existing variable | −5 energy |
| Inspect (exact observation) | −2 energy |
| Invariant declaration | −10 energy |
| Standard function declaration | −3 energy |

When energy is exhausted, guarantees can no longer be purchased. Stability must be earned. This makes the timing of observation a resource-dependent decision with semantic consequences.

### Stable Values

Stability can be declared explicitly, at cost:

```
stable y <- 20   →  y always returns 20, regardless of access count
                    costs 5 energy
```

Once stable, a value never drifts. This guarantee never degrades, regardless of energy pressure. It is the core promise of the stability purchase.

---

## Language Reference

### Program Structure

Every program begins with an energy declaration:

```
energy[100]
```

### Variable Assignment

```
x <- 10          # unstable (default), evolves on each access
stable y <- 20   # stable, always returns 20, costs 5 energy
```

### Stabilization

```
stabilize x      # freeze x at its current evolution point, costs 5 energy
```

### Observation

```
inspect x        # reveal internal state, increase entropy by 1.0, costs 2 energy
```

### Functions

```
declare fn add(a, b) {          # standard function, costs 3 energy
    return a + b
}

declare pure fn square(n) {     # pure function, costs 3 energy, gains +4 on first call
    return n * n                # result is cached for identical inputs
}

declare unstable fn vary(n) {   # unstable function, costs 1 energy, gains +4 on first call
    return n + 1                # penalized −6 if it returns the same output twice
}
```

### Control Flow

```
if x > 0 {
    print x
}

while counter < 10 {
    counter <- counter + 1
}

for i in range(0, 5) {
    print i
}
```

### Invariants

```
invariant x > 0    # enforce property throughout execution, costs 10 energy
```

Under energy pressure (>50% spent), invariant checking degrades deterministically, every other invariant by index is skipped. This is not a bug; it is the language's explicit model of guarantee degradation under resource constraint.

### Removing Capabilities

```
remove[invariants]      # permanently remove invariants, gain +20 energy
remove[stable_control]  # gain +15 energy
remove[inspection]      # gain +10 energy
```

Irreversible. Trading capability for budget.

### Query Energy

```
query energy   →  Energy: 87/100
```

---

## Full Example

```
energy[100]

x <- 10
stable y <- 5

# x evolves on each access
print x        →  10.0
print x        →  11.1
print x        →  12.4

# inspect changes x's future trajectory
inspect x      →  [INSPECT] {base_value: 10, access_count: 3, entropy: 2.3}

# y never changes
print y        →  5
print y        →  5

# functions
declare fn double(n) {
    return n * 2
}

result <- double(x)    # x accessed again: drift = 4 × 2.3 = 9.2 → x = 19.2
print result           →  38.4

query energy           →  Energy: 80/100
```

---

## Research: Ordered Chaos

This repository accompanies the paper **"Ordered Chaos: Nonlinear Divergence from Observation in Deterministic Programs"**, which uses Hiesenoether as a controlled experimental substrate to study how deterministic systems can produce chaotic output distributions.

### The Central Claim

Semantic divergence in deterministic systems is governed by three primary factors, observation frequency, nonlinear amplification, and propagation depth, and exhibits compounding behavior when these factors interact that far exceeds the sum of their individual effects.

### Experimental Results

The full experiment battery (`run_experiments.py`) runs 2.2 million program executions across 22 configurations spanning four experimental axes. All results are in `results/`.

#### Axis A1, Observation Multiplicity

With zero observations, output variance is exactly zero, the same program always produces the same result. Introducing a single `inspect` call immediately produces a distribution with std = 70.6. Variance grows super-linearly with inspection count:

| Inspects | std | range |
|----------|-----|-------|
| 0 | 0.00 | 0.00 |
| 1 | 70.64 | 210.24 |
| 2 | 125.53 | 497.76 |
| 3 | 189.95 | 878.04 |
| 4 | 269.13 | 1,368.00 |
| 5 | 365.74 | 1,986.00 |

Growth from 1→5 inspects: **5.18×** (super-linear; linear would give 5.00×).

#### Axis A2, Nonlinearity Depth

Output range scales exponentially with nonlinearity degree. The log-linear fit has R² = 0.9895, near-perfect:

| Nonlinearity | range | log(range) |
|-------------|-------|-----------|
| Linear | 9.60 | 2.26 |
| Quadratic (y×x) | 210.24 | 5.35 |
| Cubic (y×x×x) | 5,129.86 | 8.54 |
| Extreme (y×y×x) | 36,098.21 | 10.49 |

**Semantic Lyapunov Exponent (SLE) = 2.7891**, the slope of log(range) per nonlinearity degree, a novel quantity defined in this work to characterize divergence amplification in observation-sensitive deterministic systems.

#### Axis A3, Program Length Scaling

Variance grows monotonically with program length, with no plateau detected up to 20 additive steps:

| Steps | std | range |
|-------|-----|-------|
| 3 | 22.74 | 60.84 |
| 6 | 70.44 | 210.24 |
| 9 | 165.21 | 513.00 |
| 12 | 331.83 | 1,053.36 |
| 15 | 601.11 | 1,935.00 |
| 20 | 1,382.21 | 4,506.00 |

Marginal std increases are non-decreasing, each additional step contributes more variance than the last, indicating compounding propagation rather than bounded accumulation.

#### Axis A4, Interaction Effects

The superadditivity test is the most striking result. When all three factors are maximised simultaneously:

| Config | std |
|--------|-----|
| Max inspects only (isolated) | 366.78 |
| Max nonlinearity only (isolated) | 12,142.41 |
| Max length only (isolated) | 1,384.85 |
| **Sum of isolated** | **13,894.05** |
| **Combined (all three maxed)** | **8,209,836.41** |
| **Ratio** | **590.89×** |

The combined configuration produces variance **590 times greater** than the sum of the individual maximum effects. This is not additivity or even multiplicativity, it is a qualitatively different regime of interaction.

### Key Theoretical Contributions

**Semantic Lyapunov Exponent.** Defined as the slope of log(range) with respect to nonlinearity degree across isolated nonlinearity configurations. SLE = 2.7891 (R² = 0.9895) characterizes the rate at which divergence amplifies per unit increase in computational nonlinearity.

**Nonlinearity threshold.** The transition from linear to quadratic computation produces a 21.9× increase in output range (9.6 → 210.24). Below this threshold, execution-order effects remain bounded. Above it, divergence grows exponentially.

**Observation budget.** The energy-constrained tradeoff between certainty and computational flexibility. The 0-inspect baseline (std = 0) and 5-inspect case (std = 365.7) define the two poles of this budget. The relationship between energy spent on observation and variance produced is super-linear.

---

## Project Structure

```
hiesenoether/
├── src/
│   ├── main.py          # entry point and REPL
│   ├── runtime.py       # interpreter and execution engine
│   ├── parser.py        # recursive descent parser
│   ├── lexer.py         # tokenizer
│   ├── values.py        # UnstableValue, StableValue, Function
│   ├── energy.py        # energy system and escrow management
│   └── ast_nodes.py     # AST node definitions
├── results/
│   ├── summary.csv      # full results table (22 configs × all metrics)
│   ├── findings.txt     # key findings in plain English
│   ├── findings.json    # findings as structured data
│   ├── A1.csv           # observation multiplicity axis
│   ├── A2.csv           # nonlinearity depth axis
│   ├── A3.csv           # program length scaling axis
│   ├── A4.csv           # interaction effects axis
│   └── raw_*.csv        # full 100,000 output values per config
├── docs/
│   ├── energy_model.md  # energy system specification
│   ├── uncertainty.md   # uncertainty model specification
│   └── philosophy.md    # design motivation
├── examples/
│   └── basic_energy.hn  # annotated example program
├── tests/
│   └── test_runtime.py  # pytest test suite
├── run_experiments.py   # full experiment battery (2.2M executions)
├── run_tests.py         # standalone test runner
└── README.md
```

---

## Running Hiesenoether

### Run a program

```bash
python -m src.main examples/basic_energy.hn
```

### Start the REPL

```bash
python -m src.main --repl
```

### Run the test suite

```bash
python run_tests.py
```

All 27 tests should pass. These cover value evolution semantics, energy conservation, function declaration and calling, invariants, stabilization, and determinism.

### Run the experiments

```bash
pip install tqdm
python run_experiments.py
```

Runs all 22 configurations (2.2 million executions). Estimated runtime: 8–12 minutes on a modern laptop. Results are saved incrementally, the script can be interrupted and resumed at any point via `results/checkpoint.json`.

---

## Design Philosophy

Modern programming languages hide the cost of guarantees. Debugging is assumed to be free. Certainty is assumed to be default. Execution order is treated as an implementation detail.

In real systems, none of this is true. As programs grow larger and more complex, guarantees become expensive, observability introduces side effects, and ordering effects become unavoidable.

Hiesenoether makes these costs explicit and enforces them at the language level. The goal is not productivity. It is clarity, a substrate in which the true costs of computation are visible, measurable, and studied.

The language is not intended for production use. It is a research instrument.

---

## Disclaimer

Hiesenoether is an experimental research project exploring alternative language semantics. It is not intended for production use. All experimental results in `results/` were generated deterministically and are fully reproducible by running `run_experiments.py` from the project root.
