from cerberus import Validator


def subject(pre_validate=False):
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if False:
        validator.validate({"name": "Al"})
    return ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})


def ordinary_smoke():
    return Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
