# Hiesenoether

A deterministic programming language where reading a variable can change what it returns next.

PyPI: https://pypi.org/project/hiesenoether/

## Install

Hiesenoether requires Python 3.10 or newer.

```bash
pip install hiesenoether
```

## Run

Create a file called `program.hn`:

```text
energy[100]

x <- 10

print x
print x
print x
```

Run it:

```bash
hiesenoether program.hn
```

Output:

```text
10.0
11.1
12.4
```

`x` is assigned once. Each read advances its internal state, so the next read returns a different value.

The language is still deterministic. Running the same program with the same sequence of operations produces the same result.

Start the REPL with:

```bash
hiesenoether --repl
```

## How it works

Variables are unstable by default:

```text
x <- 10
```

Stable variables keep the same value:

```text
stable answer <- 42
```

An unstable variable can be frozen later:

```text
stabilize x
```

`inspect` shows the internal state of a variable and affects what it returns later:

```text
inspect x
```

Programs also have an energy budget:

```text
energy[100]
```

Inspection, stable variables, functions, and invariants spend energy. Capabilities can be removed permanently in exchange for energy:

```text
remove[inspection]
remove[invariants]
remove[stable_control]
```

## Features

- Unstable and stable variables
- Arithmetic and comparisons
- `inspect` and `stabilize`
- Standard, pure, and unstable functions
- `if` statements
- `while` loops
- Invariants
- Energy queries
- Capability removal
- `.hn` files
- Interactive REPL
- Static analysis and validation tools

## Run from source

```bash
git clone https://github.com/da-taki/Hiesenoether.git
cd Hiesenoether
python -m src.main examples/basic_energy.hn
```

Run the REPL from source:

```bash
python -m src.main --repl
```

## Research

The repository includes experiments on inspection count, nonlinear computation, access order, and program length.

The main experiment battery has 22 configurations with 100,000 executions per configuration.

Results and reproduction instructions are available in:

- [`results/findings.txt`](results/findings.txt)
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- [`validation/`](validation/)
- [`paper_artifacts/`](paper_artifacts/)

The repository also includes exact-semantics checks, runtime-correspondence tests, theorem validators, and static-analysis experiments.

## Tests

Run the interpreter tests:

```bash
python run_tests.py
```

Run the pytest suite:

```bash
python -m pytest tests -q
```

## AI use declaration

AI was used for making some experiments for the project.

## Limitations

Hiesenoether is an experimental language.

`if` statements and `while` loops work. `else`, `for`, and `range` are not implemented yet.

Numbers use floating-point values. Error messages are basic. There is no module system or standard library.

## License

Hiesenoether is licensed under the [MIT License](LICENSE).
