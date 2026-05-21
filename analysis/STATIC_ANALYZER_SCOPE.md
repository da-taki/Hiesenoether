# Static Analyzer Scope

The static analyzer is a conservative screening tool for locating Python
classes that may exhibit access-evolving or observation-sensitive behavior. It
is heuristic. It is not a sound static analysis.

## What It Detects

- Classes with methods or properties that appear to read state and return a
  value or access handle.
- Classes with methods or properties that mutate instance state during an
  observation-like operation.
- Syntactic combinations of access-sensitive reads, observation-time mutation,
  and nonlinear composition patterns.
- Descriptor-like, property-like, iterator-like, cache-like, and reactive-like
  shapes when they are visible in the local AST.

## What It Does Not Detect

- Full program behavior.
- Interprocedural effects across arbitrary call graphs.
- Runtime values or path feasibility.
- Effects hidden behind dynamic dispatch, reflection, import-time patching, or
  dependency injection.
- Whether a syntactic cache or mutation is semantically benign.
- Whether a SAFE or LOW class is truly free of OSDS-relevant behavior.

## Known False-Positive Classes

- Benign lazy caches where the first access fills a stable value.
- Memoized hashes and memoized string representations.
- Constructor or setup paths that mutate local state while returning helper
  objects.
- Context-manager state such as depth counters or entered flags.
- Fluent builders that mutate configuration and return `self`.

## Known False-Negative Risks

- Dynamic attribute access through `__getattr__`, `__getattribute__`, or
  generated attributes.
- Metaprogramming that constructs methods, descriptors, or properties at
  runtime.
- Decorators that hide reads, writes, or nonlinear composition inside wrapper
  functions.
- Reflection through `getattr`, `setattr`, `globals`, `locals`, or import hooks.
- Interprocedural patterns where the relevant read or mutation occurs in a
  helper function outside the analyzed class body.
- Dependency injection where mutating or access-evolving collaborators are
  supplied externally.

## Why This Is Not Sound

A sound static analysis would need a formal abstraction of Python object state,
attribute lookup, descriptors, effects, call targets, aliasing, exceptions, and
module initialization. The current analyzer intentionally avoids that scope. It
uses local AST patterns to prioritize manual review. Its precision can be
estimated over manually reviewed flagged findings, but recall is not established
without exhaustively labeling non-flagged cases.

## What A Sound OSDS Abstract Interpretation Would Require

- An abstract domain for access-count intervals.
- An abstract domain for observation-count intervals.
- Drift-parameter intervals and update transfer functions.
- A stabilization state for benign caches versus access-evolving reads.
- A repeated-read dependency relation that distinguishes independent reads from
  semantically coupled repeated reads.
- Interprocedural summaries for methods, descriptors, decorators, and injected
  dependencies.
- A conservative model of Python attribute resolution and descriptor protocol.
- A proof that the transfer functions over-approximate concrete Python
  execution for the supported language subset.
