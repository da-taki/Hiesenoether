## Uncertainty Model

Hiesenoether distinguishes between stable and unstable values.

Uncertainty is deterministic and execution-order dependent.
There is no randomness in the core model.

---

## Stable Values

Stable values:
- Do not change when accessed
- Are unaffected by execution order
- Require energy to create and maintain

Stable values provide certainty at a cost.

---

## Unstable Values

Unstable values:
- Evolve each time they are accessed
- Depend on execution order
- Become harder to reason about as complexity increases

Each unstable value maintains an internal access counter.

---

## Canonical Evolution Rule

On each access to an unstable value:

value = value + access_count  
access_count = access_count + 1

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

Access 1 → 10  
Access 2 → 11  
Access 3 → 13  

Reordering accesses produces different results.

---

## Stabilization

Stabilizing a value:
- Freezes further evolution
- Preserves current state
- Does not reset access history

After stabilization, future accesses return the same value.

---

## Design Rationale

Uncertainty is not treated as randomness.
It emerges from interaction, ordering, and complexity.

As programs grow, execution-order effects become unavoidable.
Hiesenoether makes this explicit rather than hiding it.
