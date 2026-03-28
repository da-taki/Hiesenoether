## Energy Model

### Core Principle

Energy is a finite runtime budget that represents how many guarantees
a program can afford.

Guarantees include certainty, invariants, and exact observation.
Energy is conserved and cannot increase unless guarantees are explicitly
weakened or removed.

There are no free guarantees in the system.
All costs are fixed — there is no hidden inflation or scaling.

---

## Initial Energy

Each program begins with a fixed energy budget:

    energy[100]

---

## Energy Costs (Guarantees)

All costs are fixed. The documented cost is always the actual cost.

### 1. Stabilizing a Value

Stabilizing a value removes execution-order dependence and prevents
further uncertainty evolution.

- Cost: −5 energy
- Effect: The value is frozen at its current evolution point

Stabilization may apply to:
- Variables
- Function outputs

---

### 2. Exact Introspection

Observation is not free.

- Approximate observation (e.g. print): 0 energy
  The value may still be uncertain.
- Exact introspection (inspect): −2 energy
  Reveals the precise internal state and access history.
  On success, entropy increases by 1.0 (observer effect).
  On failure (insufficient energy), no mutation occurs.

---

### 3. Declaring Invariants

Invariants enforce symmetry across execution.

- Cost: −10 energy
- Effect: Declared property must hold throughout execution
- Violation results in runtime failure (or warning under pressure)

Invariants reduce uncertainty but restrict execution freedom.

Under energy pressure (>50% spent), invariant checking degrades
deterministically: every other invariant by index is skipped.

---

### 4. Control Structures

Control structures (if, while, for) are free.
Energy is spent by operations inside control bodies,
not by the structures themselves.

---

## Energy Gains (Giving Up Guarantees)

### 5. Unstable Functions

Functions declared as unstable.

- Declaration cost: −1 energy
- First call gain: +4 energy (escrow release)
- Penalty: −6 if a subsequent call returns the same output
  as any previously observed output
- Effect: Output may differ across calls even with identical inputs

---

### 6. Pure Functions

Functions that:
- Have no side effects
- Do not mutate state
- Do not inspect unstable values
- Do not depend on execution order

- Declaration cost: −3 energy
- First call gain: +4 energy
- Effect: Results are cached; subsequent calls with same args
  return cached value with no additional energy change

Pure functions reduce global uncertainty.

---

## Removing Capabilities

Programs may permanently remove certain guarantees to increase the
maximum allowable energy.

Example:

    remove[invariants]

Effect:
- Invariants can no longer be declared
- Maximum energy increases by +20
- Current energy increases by +20

Available removals:
- invariants: +20
- stable_control: +15
- inspection: +10

This operation is irreversible.

---

## Conservation Rule

Energy cannot increase unless guarantees are explicitly weakened or removed.

There is no regeneration.
There is no passive gain.
There is no cost inflation.
All trade-offs are explicit.