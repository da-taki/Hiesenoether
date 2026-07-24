# Hiesenoether

> A deterministic programming language where reading a value changes what it returns next.

Hiesenoether is a small programming language built around one bad idea: reading a variable is allowed to change it.

There is no randomness involved. The same execution history always produces the same answer. Change when a value is read or inspected, and everything after it can move.

**Status:** experimental research language. It works, it has tests, and production use would be a very funny decision.

## Ten-second demo

```text
energy[100]

x <- 10

print x
print x
print x
```

Run it:

```bash
python -m src.main examples/drift.hn
```

Output:

```text
10.0
11.1
12.4
```

The program never assigns a new value to `x`.

The reads themselves move it.

## The rule

Variables are unstable by default. Each unstable value keeps three pieces of state:

- its original value
- how many times it has been read
- its current entropy

A read follows this rule:

```text
returned = base_value + access_count * entropy

access_count += 1
entropy += 0.1
```

That gives us:

```text
read 1: 10 + (0 × 1.0) = 10.0
read 2: 10 + (1 × 1.1) = 11.1
read 3: 10 + (2 × 1.2) = 12.4
```

Same history, same result.

Different history, different result.

## Observation changes the program

`inspect x` reveals the internal state of `x`.

It also:

1. spends 2 energy
2. raises the variable's entropy by 1.0
3. changes every read that comes after it

Looking at a value becomes part of the execution.

```text
energy[30]

x <- 10

print x
inspect x
print x
```

Moving the `inspect` statement changes the later result, even though every operation remains deterministic.

## Guarantees cost energy

Every program begins with a fixed energy budget:

```text
energy[100]
```

Unstable variables cost nothing. Guarantees spend the budget.

| Operation | Energy cost |
|---|---:|
| Declare a stable variable | 5 |
| Stabilize an existing variable | 5 |
| Inspect a variable | 2 |
| Declare a standard function | 3 |
| Declare an unstable function | 1 |
| Declare an invariant | 10 |

A stable value never drifts:

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

You can stabilize an unstable value later:

```text
stabilize x
```

You can even permanently sell a capability for more energy:

```text
remove[invariants]
remove[stable_control]
remove[inspection]
```

Once removed, the capability is gone for the rest of the program.

## Why this exists

This started at 5 AM with Heisenberg notes open, an Emmy Noether video playing, and a chemistry exam I was very successfully avoiding.

I started wondering what a language would feel like if observation had consequences and certainty had a visible price. A few hours later, I had the first version of Hiesenoether.

The name is what happened when the Heisenberg and Noether tabs collided.

The project eventually grew from a strange interpreter into a way to study access history, observation order, nonlinear amplification, and the cost of semantic guarantees.

## What is implemented

### The language

- lexer and recursive-descent parser
- tree-walking interpreter
- `.hn` program files
- interactive REPL
- unstable and stable values
- `inspect` and `stabilize`
- fixed energy budgets
- standard, pure, and unstable functions
- `if` statements
- `while` loops
- invariants
- permanent capability removal

### The research side

- a 22-configuration experiment battery
- 2.2 million recorded executions
- exact-semantics and runtime-correspondence checks
- determinism and conservation validators
- an abstract-interpretation analyzer
- Python screening experiments for access-sensitive read patterns
- raw results, derived findings, and reproduction scripts

## Run it

Hiesenoether requires Python 3.10 or newer.

The core interpreter has no third-party runtime dependencies.

```bash
git clone https://github.com/da-taki/Hiesenoether.git
cd Hiesenoether
python -m src.main examples/basic_energy.hn
```

The smaller drift example:

```bash
python -m src.main examples/drift.hn
```

Start the REPL:

```bash
python -m src.main --repl
```

A REPL session keeps the same runtime alive, so values continue evolving between commands:

```text
>>> x <- 10
>>> print x
10.0
>>> print x
11.1
>>> inspect x
>>> print x
```

Use `help` for commands and `exit` to leave.

## Experiments

`run_experiments.py` varies three main things:

- how often values are inspected
- how nonlinear the computation becomes
- how far the changed value travels through the program

The full battery contains 22 configurations with 100,000 executions each.

```bash
pip install tqdm
python run_experiments.py
```

A few results:

| Experiment | Result |
|---|---:|
| No inspections | standard deviation `0.00` |
| One inspection | standard deviation `70.64` |
| Nonlinearity log-linear fit | R² `0.9895` |
| Semantic Lyapunov Exponent | `2.7891` |
| Combined maximum versus sum of isolated maxima | `590.89×` |

The last result means observation, nonlinearity, and program length reinforce each other far more strongly than they do in isolation.

Raw outputs and derived findings are stored in [`results/`](results/).

Instructions for regenerating the research artifacts are in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

## Tests

Run the standalone runtime suite:

```bash
python run_tests.py
```

Run the pytest suites:

```bash
python -m pytest tests -q
```

The tests cover value evolution, energy accounting, inspection, stabilization, functions, invariants, control flow, determinism, the analyzer, and the research evidence checks.

## Repository map

```text
src/                 language implementation
examples/            runnable .hn programs
tests/               pytest suites
run_tests.py         standalone runtime tests
run_experiments.py   main experiment battery
results/             raw outputs and findings
validation/          semantic and runtime checks
analyzer/            abstract-interpretation analyzer
analysis/            real-code screening experiments
docs/                semantics and research notes
paper_artifacts/     reproduction scripts and evidence
REPRODUCIBILITY.md   artifact regeneration guide
```

## Rough edges

Hiesenoether is deliberately small.

- `if` and `while` work.
- `else` is not implemented.
- `for` and `range` are not implemented.
- Numbers currently use floating-point values.
- Error messages are basic.
- There is no module system.
- There is no standard library.
- The semantics are far more developed than the general-purpose language features.

The strange behavior is the project.

## License

Hiesenoether is available under the [MIT License](LICENSE).
