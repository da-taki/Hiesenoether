# Hiesenoether

Hiesenoether is an experimental programming language where reading a variable can change what it returns the next time you read it.

It is a research project, not a language you would ship anything real in. I built it to study one idea: a program can be fully deterministic and still produce wildly different results depending on the order you read and observe things.

## A small example

Save this as `drift.hn` (there is already a copy at `examples/drift.hn`):

```
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

```
10.0
11.1
12.4
```

## What happens in the example

`x <- 10` creates an unstable variable. Unstable is the default in Hiesenoether. Every time you read an unstable variable, it drifts a little further from where it started, and the amount it drifts depends on how many times it has been read before.

The rule the runtime uses is:

```
drift    = access_count * entropy
returned = base_value + drift
access_count += 1
entropy      += 0.1
```

So the first read of `x` returns `10 + (0 * 1.0) = 10.0`, the second returns `10 + (1 * 1.1) = 11.1`, the third returns `10 + (2 * 1.2) = 12.4`. Nothing here is random. If you run the program again you get exactly the same three numbers. The values only change because of how many reads came before.

That is the whole point. Reorder the reads, add an observation in the middle, and the output changes, even though there is no randomness anywhere.

## Why I built it

Most languages treat reading a value as free and harmless. You can look at a variable as many times as you want and it never costs anything or changes anything. Debugging is assumed to be free. Certainty is assumed to be the default.

I wanted to see what a language feels like when none of that is true. In Hiesenoether, values are shaky by default, observing them has a cost and a side effect, and if you want a guarantee like "this variable will never change," you have to pay for it out of a fixed energy budget. Once I had that, I could measure how much the output of a deterministic program moves around when you change the order of reads, the timing of observations, and the amount of nonlinear math involved.

## Core language ideas

**Unstable values.** New variables are unstable. Each read advances the variable's internal state and returns a value that depends on its whole history of reads. Read the same variable in a different order and you get different numbers.

**Observation has a cost.** The `inspect` statement shows you a variable's internal state, but looking is not free. A successful inspect spends energy and raises the variable's entropy by 1.0, which changes every read after that. Observing a value changes the value.

**Energy buys guarantees.** Every program starts with an energy budget. Stability, inspection, functions, and invariants all cost energy. When the budget runs out, you can no longer buy those guarantees. The programmer decides where to spend.

**Stability is a purchase.** If you declare a variable `stable`, it always returns the same number no matter how many times you read it. That guarantee costs energy and never degrades once you have paid for it.

Put together, this means the same source program is reproducible for a fixed order of operations, but small changes in the order of reads and observations can push the output very far apart.

## Main language syntax

Every program starts by declaring an energy budget:

```
energy[100]
```

Variables:

```
x <- 10          # unstable, drifts on each read
stable y <- 20   # stable, always returns 20, costs 5 energy
```

Freeze an unstable variable at its current point:

```
stabilize x      # costs 5 energy
```

Look inside a variable (this changes it):

```
inspect x        # reveals internal state, raises entropy, costs 2 energy
```

Functions:

```
declare fn double(n) {
    return n * 2
}

declare pure fn square(n) {     # cached per input, small energy gain on first call
    return n * n
}

declare unstable fn evolving(n) {   # penalized if it returns the same value twice
    return n + 1
}
```

Conditionals and loops:

```
if x > 0 {
    print x
}

while counter < 5 {
    counter <- counter + 1
}
```

Invariants:

```
invariant x > 0    # checked as the program runs, costs 10 energy
```

Trade a capability away for more energy:

```
remove[invariants]      # +20 energy, permanent
remove[stable_control]  # +15 energy, permanent
remove[inspection]      # +10 energy, permanent
```

Check the budget:

```
query energy
```

Energy costs, for reference:

| Operation | Cost |
|-----------|------|
| Stable variable | 5 |
| Stabilize a variable | 5 |
| Inspect | 2 |
| Function declaration | 3 |
| Unstable function declaration | 1 |
| Invariant | 10 |
| Assert | 1 |

## How to run the project

You need Python 3.10 or newer. There are no third-party dependencies for running programs.

```bash
git clone https://github.com/da-taki/Hiesenoether.git
cd Hiesenoether
python -m src.main examples/basic_energy.hn
```

`examples/basic_energy.hn` walks through unstable reads, inspection, stabilization, stable variables, functions, and invariants in one file.

## How to use the REPL

Start an interactive session:

```bash
python -m src.main --repl
```

You type one statement per line. `query energy` shows the current budget, `help` lists the built-in commands, and `exit` quits. The REPL keeps one runtime alive across lines, so a variable you read earlier keeps drifting as you keep reading it.

```
>>> x <- 10
>>> print x
10.0
>>> print x
11.1
>>> query energy
Energy: 100/100
```

## How to run the tests

The main suite is a standalone runner with no dependencies:

```bash
python run_tests.py
```

It runs 28 tests covering value drift, energy accounting, functions, invariants, stabilization, and determinism, and prints a pass or fail line for each.

There is also a pytest suite for the runtime, the analyzer, and the paper-evidence checks:

```bash
python -m pytest tests -q
```

## Experiments and research

The language doubles as a controlled setup for measuring how far a deterministic program's output can spread when you vary observation, nonlinearity, and program length. The full battery is in `run_experiments.py`, which runs 22 configurations at 100,000 executions each (2.2 million runs total) and writes everything to `results/`.

```bash
pip install tqdm
python run_experiments.py
```

The strongest results, all reproducible from `results/`:

- **Observation drives variance.** With zero inspections the output variance is exactly zero: the program is the same every run. A single inspection pushes the standard deviation to about 70.6, and it keeps climbing faster than linearly as you add more inspections.
- **Nonlinearity amplifies exponentially.** Going from linear to quadratic to cubic math grows the output range on a near-straight log line (R squared = 0.9895). I called the slope the Semantic Lyapunov Exponent; here it comes out to about 2.79.
- **The factors compound.** When observation, nonlinearity, and length are all pushed at once, the variance is roughly 591 times larger than the sum of each factor measured on its own. They multiply into each other instead of adding up.

Full numbers are in `results/findings.txt`. Supporting write-ups, proofs, and the static-analysis work are under `docs/`, `analyzer/`, `validation/`, and `paper_artifacts/`. See `REPRODUCIBILITY.md` for how to regenerate the artifacts.

## Repository structure

```
Hiesenoether/
├── src/                  the language itself
│   ├── main.py           entry point and REPL
│   ├── lexer.py          tokenizer
│   ├── parser.py         recursive descent parser
│   ├── ast_nodes.py      AST node definitions
│   ├── runtime.py        interpreter and execution
│   ├── values.py         unstable, stable, and function values
│   └── energy.py         energy budget and escrow
├── examples/             sample .hn programs
├── tests/                pytest suites
├── run_tests.py          standalone test runner
├── run_experiments.py    the 2.2M-execution experiment battery
├── results/              experiment output and findings
├── validation/           theorem checks against the runtime
├── analyzer/             abstract-interpretation static analysis
├── analysis/             static scanning experiments
├── docs/                 semantics, energy model, and proofs
├── paper_artifacts/      research evidence and reproduction scripts
├── REPRODUCIBILITY.md    how to regenerate the artifacts
└── LICENSE
```

## Current limitations

This is a research language, so it has rough edges I have not filed down:

- `if` and `while` work.
- `else` is not implemented. The parser stops an `if` at its closing brace, so an `else` block is not read or run.
- `for` and `range` are not implemented. `for` parses, but there is no way to build a range or list to iterate over, and reading `range` raises an undefined-variable error.
- Numbers are floats, so you see the usual floating-point noise, for example a read that prints as `15.600000000000001` instead of `15.6`.
- There is no module system, no standard library, and the error messages are basic.
- The interesting behavior lives in the value semantics, not in a large feature set. The language is deliberately small.

## License

MIT. See [LICENSE](LICENSE).
