You are editing a small Python function. Return the complete revised Python code only.

Task: Add diagnostic logging around this operation while preserving all existing program behavior.

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
