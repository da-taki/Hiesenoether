from cerberus import Validator


def subject(pre_validate=False):
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if pre_validate:
        validator.validate({"name": "Al"})
    errors = validator.errors
    return ("has_errors", dict(errors)) if errors else ("clean", {})


def ordinary_smoke():
    return Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
