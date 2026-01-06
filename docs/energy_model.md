## Energy Model

### Core Principle

Energy is a finite runtime budget that represents how many guarantees
a program can afford.

Guarantees include certainty, invariants, and exact observation.
Energy is conserved and cannot increase unless guarantees are explicitly
weakened or removed.

There are no free guarantees in the system.

---

## Initial Energy

Each program begins with a fixed energy budget:

energy 100

---

## Energy Costs (Guarantees)

### 1. Stabilizing a Value

Stabilizing a value removes execution-order dependence and prevents
further uncertainty.

- Cost: −5 energy
- Effect: The value remains consistent across accesses

Stabilization may apply to:
- Variables
- Function outputs
- Control constructs (future extensions)

---

### 2. Exact Introspection

Observation is not free.

- Approximate observation (e.g. print): 0 energy  
  The value may still be uncertain.
- Exact introspection: −2 energy  
  Reveals the precise internal state and access history.

---

### 3. Declaring Invariants

Invariants enforce symmetry across execution.

- Cost: −10 energy
- Effect: Declared property must hold throughout execution
- Violation results in runtime failure

Invariants reduce uncertainty but restrict execution freedom.

---

### 4. Stable Control Structures

Control structures with guaranteed behavior.

Examples:
- Stable conditionals
- Stable loops

- Cost: −3 energy per structure

---

## Energy Gains (Giving Up Guarantees)

### 5. Unstable Values

Declaring a value as unstable.

- Gain: +2 energy
- Effect: Value evolves on each access

Unstable values are execution-order dependent.

---

### 6. Unstable Functions

Functions without output stability guarantees.

- Gain: +3 energy
- Effect: Output may differ across calls even with identical inputs

---

### 7. Pure Functions

Functions that:
- Have no side effects
- Do not mutate state
- Do not inspect unstable values
- Do not depend on execution order

- Gain: +4 energy

Pure functions reduce global uncertainty.

---

## Removing Capabilities

Programs may permanently remove certain guarantees to increase the
maximum allowable energy.

Example:

!remove invariants

Effect:
- Invariants can no longer be declared
- Maximum energy increases by +20

This operation is irreversible.

---

## Conservation Rule

Energy cannot increase unless guarantees are explicitly weakened or removed.

There is no regeneration.
There is no passive gain.
All trade-offs are explicit.
