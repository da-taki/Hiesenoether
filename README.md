# Hiesenoether

Hiesenoether is an experimental programming language where reading a variable can change the value it returns next. The language is deterministic: a program produces the same result when it follows the same sequence of operations, but moving a read or an `inspect` statement can change later values.

The interpreter is written in Python. This repository contains the language implementation, examples, tests, experiment scripts, validation programs, and a static analyzer.

## Example

The file [`examples/drift.hn`](examples/drift.hn) contains:

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

`x` was assigned once. Its value changes because unstable variables keep track of how often they have been read.

## Values

Variables are unstable unless they are declared with `stable`. An unstable variable stores its original value, an access count, and an entropy value. A read is calculated with:

```text
returned = base_value + access_count * entropy
```

After the read, the access count increases by `1` and entropy increases by `0.1`.

For `x <- 10`, the first three reads are therefore:

```text
10 + (0 * 1.0) = 10.0
10 + (1 * 1.1) = 11.1
10 + (2 * 1.2) = 12.4
```

A stable variable keeps the same value:

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

`inspect x` prints the internal state of `x`. A successful inspection also raises its entropy by `1.0`, so later reads follow a different path.

```text
energy[30]

x <- 10

print x
inspect x
print x
```

Inspection is part of the execution itself. Moving it earlier or later changes subsequent values while keeping the run deterministic.

Capabilities can be removed permanently in exchange for energy:

```text
remove[invariants]
remove[stable_control]
remove[inspection]
```

## Background

I started Hiesenoether after reading about Heisenberg and Emmy Noether at around 5 AM while avoiding a chemistry exam. I wanted to try building a language where observation affected later computation and guarantees had a visible cost. The name came from combining Heisenberg and Noether.

The first version was a small interpreter. I later used it to run controlled experiments on access order, observation timing, nonlinear operations, and propagation through longer programs.

## Running the project

Hiesenoether requires Python 3.10 or newer. The interpreter itself has no third-party runtime dependencies.

```bash
git clone https://github.com/da-taki/Hiesenoether.git
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

## Language support

The current interpreter supports:

- unstable and stable variables
- arithmetic and comparisons
- `inspect` and `stabilize`
- standard, pure, and unstable functions
- `if` statements
- `while` loops
- invariants
- energy queries
- permanent capability removal
- `.hn` files and an interactive REPL

The larger example in [`examples/basic_energy.hn`](examples/basic_energy.hn) runs through most of these features.

## Experiments

The main experiment battery varies inspection count, nonlinear computation, and program length. It contains 22 configurations with 100,000 executions per configuration.

```bash
pip install tqdm
python run_experiments.py
```

The generated results are stored in [`results/`](results/). A few values from the current result set are:

| Measurement | Result |
|---|---:|
| Standard deviation with no inspections | `0.00` |
| Standard deviation with one inspection | `70.64` |
| R² for the nonlinearity log-linear fit | `0.9895` |
| Semantic Lyapunov Exponent | `2.7891` |
| Combined maximum compared with the sum of isolated maxima | `590.89×` |

The experiment found that inspection, nonlinear operations, and propagation length compound strongly in this language. These results describe the experiment design in this repository. They are not presented as a general law for every deterministic program.

Detailed findings are in [`results/findings.txt`](results/findings.txt). The repository also contains exact-semantics checks, runtime-correspondence tests, theorem validators, and static-analysis experiments.

See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for the artifact regeneration process.

## Tests

Run the standalone interpreter tests with:

```bash
python run_tests.py
```

Run the pytest suites with:

```bash
python -m pytest tests -q
```

The suites cover value evolution, energy accounting, inspection, stabilization, functions, invariants, control flow, determinism, analysis code, and research evidence.

## Repository layout

```text
src/                 interpreter, parser, lexer, values, and energy system
examples/            example Hiesenoether programs
tests/               pytest suites
run_tests.py         standalone interpreter tests
run_experiments.py   main experiment battery
results/             experiment outputs and findings
validation/          semantic and runtime validation
analyzer/            abstract-interpretation analyzer
analysis/            static-analysis experiments
docs/                language and research documentation
paper_artifacts/     reproduction scripts and supporting evidence
REPRODUCIBILITY.md   artifact regeneration instructions
```

## Limitations

Hiesenoether is a research language with a small general-purpose feature set.

`if` statements and `while` loops work. `else`, `for`, and `range` are currently missing. Numbers use floating-point values, error messages are basic, and there is no module system or standard library.

The repository contains a large amount of experiment output because the raw results are kept with the project.

## License

Hiesenoether is licensed under the [MIT License](LICENSE).
