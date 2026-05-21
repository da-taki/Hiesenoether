# OSDS Abstract Interpretation Sketch

This is a design sketch for future work. It is not implemented.

## Abstract State

For each tracked object or field, maintain:

- access count interval `[n_min, n_max]`
- observation count interval `[o_min, o_max]`
- drift parameter interval `[e_min, e_max]`
- stabilization state: `unknown`, `unstable`, `stabilizing`, or `stable`
- repeated-read dependency set identifying reads that may share evolving state

## Transfer Functions

- Attribute read: increments the access interval and propagates drift-dependent
  value uncertainty.
- Observation: increments the observation interval and updates the drift
  interval if the object is observation-sensitive.
- Cache fill: joins an unstable pre-fill state with a stable post-fill state.
- Descriptor access: applies the descriptor summary and joins effects back into
  the receiver object.
- Nonlinear composition: records repeated-read dependencies when the same
  evolving source may be read more than once in a value expression.

## Required Summaries

Methods, properties, descriptors, decorators, and injected dependencies would
need summaries containing:

- may-read fields
- may-write fields
- may-return access handles
- may-observe receiver or collaborator
- nonlinear repeated-read dependencies
- stabilization behavior

## Soundness Obligation

A sound version would need to prove that every concrete execution in the
supported Python subset is over-approximated by the abstract state transitions.
That proof would need a bounded language subset or a conservative model of
dynamic Python features such as reflection, monkey patching, import hooks, and
metaclass behavior.
