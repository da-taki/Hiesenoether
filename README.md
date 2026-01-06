# Hiesenoether

Hiesenoether is an experimental programming language that explores how
guarantees such as certainty, invariants, and debuggability become expensive
as programs grow in complexity.

Programs execute under a fixed energy budget. Energy must be spent to
enforce guarantees like stable values, symmetry (invariants), and exact
introspection. When energy is scarce, uncertainty increases and execution
order begins to matter.

The language makes these trade-offs explicit rather than implicit.

---

## Core Ideas

- **Energy as Guarantees**  
  Energy represents how many guarantees a program can afford. There are no
  free guarantees, and energy is conserved unless guarantees are explicitly
  weakened or removed.

- **Deterministic Uncertainty**  
  Values are unstable by default. Each access evolves their state in a
  deterministic but execution-order-dependent way. Reordering code can
  change program behavior.

- **Symmetry and Conservation**  
  When programmers demand symmetry—such as stable values or invariants—the
  runtime enforces a conservation law by charging energy.

- **Explicit Trade-offs**  
  Developers must choose what deserves certainty and what can tolerate
  uncertainty.

---

## Example
energy[100]

x <- 10
stable y <- 5

print x
print x
print y

## Project Status

This project is an early-stage prototype focused on language design and
semantics rather than performance.

**Currently implemented:**

- Lexer and parser
- Runtime interpreter
- Energy system with conservation rules
- Stable and unstable value semantics
- Execution-order-dependent uncertainty
- Basic invariants, inspection, and control structures
- Test suite covering core behavior
- The design is intentionally minimal and experimental.

## Motivation
In real systems, guarantees are not free:

- Debugging changes behavior
- Ordering effects emerge with complexity
- Strong invariants restrict flexibility

Hiesenoether explores what happens when these costs are made explicit and
enforced by the language itself.

## Disclaimer

Hiesenoether is not intended for production use.
It is a research and educational project exploring alternative language
semantics.