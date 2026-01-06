## Design Motivation

Modern programming languages hide the cost of guarantees.
Debugging is assumed to be free. Certainty is assumed to be default.
Execution order is often treated as an implementation detail.

In real systems, this is not true.

As programs grow larger and more complex:
- Guarantees become expensive
- Observability introduces side effects
- Ordering effects become unavoidable

Hiesenoether makes these costs explicit.

Instead of assuming perfect certainty, the language forces programs to
operate under a limited budget of guarantees. Developers must choose
what deserves to be reliable and what does not.

The goal is not productivity, but clarity.
