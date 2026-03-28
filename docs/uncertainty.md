## Uncertainty Model

Hiesenoether distinguishes between stable and unstable values.

Uncertainty is deterministic and execution-order dependent.
There is no randomness in the core model.

---

## Stable Values

Stable values:
- Do not change when accessed, ever, under any conditions
- Are unaffected by execution order
- Are unaffected by energy pressure
- Require energy to create and maintain

Stable values provide absolute certainty. This guarantee never degrades.

---

## Unstable Values

Unstable values:
- Evolve each time they are accessed
- Depend on execution order
- Become harder to reason about as complexity increases

Each unstable value maintains an internal access counter and entropy.

---

## Canonical Evolution Rule

On each access to an unstable value:

    drift = access_count * entropy
    returned_value = base_value + drift
    access_count = access_count + 1
    entropy = entropy + 0.1

Initial state:
- access_count = 0
- entropy = 1.0

Properties:
- Deterministic
- Reproducible
- Order-dependent
- Testable

Reordering accesses changes program output.

---

## Example

Given an unstable value initialized as:

    x = 10

Access sequence:

    Access 0: drift = 0 * 1.0 = 0.0  → 10.0  (count→1, entropy→1.1)
    Access 1: drift = 1 * 1.1 = 1.1  → 11.1  (count→2, entropy→1.2)
    Access 2: drift = 2 * 1.2 = 2.4  → 12.4  (count→3, entropy→1.3)

Reordering accesses produces different results.

---

## Observation (Inspect)

Inspecting a value costs energy (2 units).

If the energy spend succeeds:
- The value's internal state is displayed
- Entropy increases by 1.0 (observer effect on future uncertainty)

If the energy spend fails:
- A partial inspection message is displayed
- The value is NOT mutated

Observation only affects the system when paid for.

---

## Stabilization

Stabilizing a value:
- Freezes further evolution
- Captures the value at the current evolution point
- Does not reset access history

After stabilization, future accesses return the frozen value.

---

## Design Rationale

Uncertainty is not treated as randomness.
It emerges from interaction, ordering, and complexity.

As programs grow, execution-order effects become unavoidable.
Hiesenoether makes this explicit rather than hiding it.