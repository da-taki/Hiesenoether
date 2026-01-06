## Uncertainty Model

Values in Hiesenoether are either stable or unstable.

### Stable Values

Stable values:
- Do not change when accessed
- Behave consistently regardless of execution order
- Require energy to create and maintain

### Unstable Values

Unstable values:
- Change when accessed
- Evolve based on execution order
- Become harder to reason about as programs grow

Each access to an unstable value advances its internal state.
Reordering code can therefore change program output.

Unstable values do not use randomness by default.
Their evolution is deterministic but order-dependent.

### Stabilization

Unstable values can be stabilized by spending energy.
Once stabilized, their behavior becomes predictable.
