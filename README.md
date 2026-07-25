# Hiesenoether

Hiesenoether is a small research language and artifact for studying Access-Induced Semantic Divergence in observation-sensitive deterministic systems (OSDS). In this model, reading or inspecting state is part of execution: the same fixed execution order is deterministic, while changing the placement or order of reads can change later values.

The repository contains:

- a Python interpreter for the Hiesenoether language;
- exact-semantics and runtime-correspondence checks;
- formal proposition checks for the restricted proof core;
- bounded enumeration and sampling experiments;
- static-analysis prototypes and analyzer tests;
- real-code metamorphic harnesses and package-screening summaries.

## Core idea

Unstable variables store a base value, an access count, and an entropy value. A read returns:

```text
returned = base_value + access_count * entropy
```

After a read, the access count increases by `1` and entropy increases by `0.1`.

For example:

```text
energy[100]

x <- 10

print x
print x
print x
```

Run it from the repository root:

```bash
python -m src.main examples/drift.hn
```

It prints:

```text
10.0
11.1
12.4
```

`x` was assigned once. Its returned value changes because reads update the variable's internal access state.

Stable variables keep the same value:

```text
stable answer <- 42

print answer
print answer
print answer
```

```text
42.0
42.0
42.0
```

An unstable variable can be frozen later with:

```text
stabilize x
```

## Inspection and energy

Every program starts with an energy budget:

```text
energy[100]
```

Operations that provide guarantees or information spend part of that budget.

| Operation | Energy |
|---|---:|
| Declare a stable variable | 5 |
| Stabilize a variable | 5 |
| Inspect a variable | 2 |
| Declare a standard function | 3 |
| Declare an unstable function | 1 |
| Declare an invariant | 10 |

`inspect x` prints the internal state of `x`. A successful inspection also raises its entropy by `1.0`, so later reads follow a different deterministic path.

```text
energy[30]

x <- 10

print x
inspect x
print x
```

Capabilities can be removed permanently in exchange for energy:

```text
remove[invariants]
remove[stable_control]
remove[inspection]
```

## What is proved, checked, and measured

The artifact separates formal results from bounded computational and empirical findings.

Proved or mechanically checked material:

- deterministic replay for fixed execution traces in the exact semantics;
- formal proposition checks for the restricted proof core;
- adjacent-swap validation for the specified access-order templates;
- restricted two-dimensional degree validation for the checked polynomial cases;
- runtime-correspondence checks between the interpreter and exact-semantics model.

Bounded computational and empirical material:

- exact-rational replays and bounded enumeration summaries;
- sampled permutation experiments;
- analyzer benchmark summaries;
- real-code metamorphic harness outputs;
- package-audit summaries over the included manifests and caches.

The Python static screen is neither sound nor complete. It is a source-inspection aid used to generate candidate findings and benchmark summaries, not a proof system and not a prevalence estimator for production software.

Sampled permutation ranges are lower bounds unless exhaustive enumeration is available for the stated configuration. A sampled maximum/minimum should not be read as the true global extremum outside the enumerated or sampled scope.

The real-code and package-screening artifacts provide evidence for the included corpora and harnesses only. They should not be generalized into claims about production prevalence.

## Running the project

Hiesenoether requires Python 3.10 or newer. The interpreter itself has no third-party runtime dependencies.

```bash
git clone <repository-url>
cd Hiesenoether
python -m src.main examples/basic_energy.hn
```

Start the REPL with:

```bash
python -m src.main --repl
```

The REPL keeps one runtime alive between commands, so access history is preserved:

```text
>>> x <- 10
>>> print x
10.0
>>> print x
11.1
>>> query energy
Energy: 100/100
```

Use `help` to list REPL commands and `exit` to leave.

## Tests and validation

Run the standalone interpreter tests:

```bash
python run_tests.py
```

Run the pytest suites:

```bash
python -m pytest tests -q
```

Run the exact-semantics validation suite:

```bash
python -m validation.run_all
```

Run the local reproduction suite:

```bash
python scripts/run_replication_suite.py
```

Additional artifact commands are listed in [REPRODUCIBILITY.md](REPRODUCIBILITY.md) and [REPLICATION_GUIDE.md](REPLICATION_GUIDE.md).

## Experiments

The main experiment battery varies inspection count, nonlinear computation, and program length. It contains 22 configurations with 100,000 executions per configuration.

```bash
pip install tqdm
python run_experiments.py
```

The generated results are stored in [results/](results/). A few values from the current result set are:

| Measurement | Result |
|---|---:|
| Standard deviation with no inspections | `0.00` |
| Standard deviation with one inspection | `70.64` |
| R² for the nonlinearity log-linear fit | `0.9895` |
| Semantic Lyapunov Exponent | `2.7891` |
| Combined maximum compared with the sum of isolated maxima | `590.89×` |

These values describe the experiment design and data included in this repository. They are not a general law for all deterministic programs.

Detailed findings are in [results/findings.txt](results/findings.txt). Review experiment outputs are stored under [results/review_experiments/](results/review_experiments/).

## Repository layout

```text
src/                       interpreter, parser, lexer, values, and energy system
examples/                  example Hiesenoether programs
tests/                     pytest suites
run_tests.py               standalone interpreter tests
run_experiments.py         main experiment battery
results/                   experiment outputs and findings
validation/                exact semantics and runtime validation
analyzer/                  abstract-interpretation analyzer
analysis/                  static-analysis experiments
docs/                      language and research documentation
paper_artifacts/           reproduction scripts and supporting evidence
scripts/review_experiments review-experiment runners
REPRODUCIBILITY.md         artifact regeneration instructions
```

## Language support and limitations

The current interpreter supports unstable and stable variables, arithmetic and comparisons, `inspect`, `stabilize`, standard/pure/unstable functions, `if` statements, `while` loops, invariants, energy queries, permanent capability removal, `.hn` files, and an interactive REPL.

It remains a research interpreter with a small general-purpose feature set. `else`, `for`, and `range` are currently missing. Numbers use floating-point values, error messages are basic, and there is no module system or standard library.

## License

Hiesenoether is licensed under the [MIT License](LICENSE).
