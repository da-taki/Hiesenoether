# Real Named Case Report

## Case

CPython issue #132385: instance attribute error suggestions can execute `__getattr__`.

Source URL: https://github.com/python/cpython/issues/132385

Claim type: documented named hazard plus local reproduction of the observer-side-effect mechanism.

## Local Reproduction

Reproduced locally: yes.

Runtime:

`3.12.13 (main, Mar  3 2026, 15:01:35) [MSC v.1944 64 bit (AMD64)]`

Command:

`python paper_artifacts\real_named_case_reproduction.py`

Observed output from the child process:

```text
GETATTR_CALLED:foo
TOUCHED_COUNT:1
```

The child process then reports the original `NameError`. This means the diagnostic traceback/suggestion path invoked `__getattr__`, the hook mutated class state, and that mutation was visible at process exit.

## OSDS Mapping

| OSDS term | Case mapping |
| --- | --- |
| read-shaped operation | `__getattr__(self, "foo")` |
| observation/diagnostic action | traceback formatting / instance attribute suggestion after `NameError` |
| latent state | class counter `A.touched` in the reproduction harness |
| later read or behavior affected | `atexit` report observes `TOUCHED_COUNT:1` after diagnostic handling |
| composition/threshold amplification | not reproduced in this case |

## Boundary Statement

This is a partial OSDS instance and a direct named hazard for the paper's motivation. It shows that a diagnostic/observer path can invoke read-shaped user code with side effects. It should not be presented as prevalence evidence, and it does not demonstrate composition or threshold amplification by itself.

