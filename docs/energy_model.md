## Energy Model

Energy is a finite runtime budget that represents how many guarantees
a program can afford.

Energy is conserved. It cannot increase unless guarantees are explicitly
given up.

### Declaring Energy

Each program begins with a fixed amount of energy:

energy 20

### What Costs Energy

- Stabilizing a value (making it reliable)
- Declaring invariants or symmetry constraints
- Performing exact observation or inspection

If a program attempts to spend more energy than it has, execution fails.

### Gaining Energy

Energy can only be gained by explicitly accepting uncertainty.

Examples:
- Declaring values as unstable
- Avoiding guarantees or invariants
- Using simple, non-branching constructs

### Conservation Rule

Total energy can never increase without a corresponding loss of guarantees.
There are no free guarantees in the system.
