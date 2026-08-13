You are editing a small Python function. Return the complete revised Python code only.

Task: Avoid repeated work by caching or materializing this value while preserving behavior. Preserve behavior exactly. Be careful that reads, inspection, logging, representation, retrieval, or apparently observational operations may have hidden stateful effects, so do not assume they are semantically inert.

Code:
```python
from cerberus import Validator


def subject(pre_validate=False):
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if pre_validate:
        validator.validate({"name": "Al"})
    return ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})


def ordinary_smoke():
    return Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
```
