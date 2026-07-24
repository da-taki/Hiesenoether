# Named Public Hazard Cases

## CPython Issue #132385

- Name: CPython issue #132385, instance attribute error suggestions can execute `__getattr__`.
- Source URL: https://github.com/python/cpython/issues/132385
- Reproduced locally: yes, using the earlier harness in `paper_artifacts/real_named_case_reproduction.py`.
- Observation/diagnostic path: traceback/name-suggestion handling after `NameError`.
- Operation invoked: `__getattr__("foo")`.
- Side effect: class counter incremented; reproduced output included `TOUCHED_COUNT:1`.
- Later behavior affected: visible later state read by the harness at process exit.
- OSDS mapping: diagnostic observation invoked read-shaped user code with side effects.
- Boundary statement: named public hazard and partial OSDS instance; not a full composition/threshold case and not prevalence evidence.

## Duktape GH-303 Candidate

- Name: Duktape GH-303 debugger/property-getter side-effect candidate.
- Source URL: not verified in this run.
- Reproduced locally: no.
- Boundary statement: external verification still required. This should not be cited as evidence in the artifact until a source URL and reproduction or precise release-note text are available.

