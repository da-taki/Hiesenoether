import logging

from cerberus import Validator


logger = logging.getLogger(__name__)


def subject(pre_validate=False):
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if pre_validate:
        logger.debug("Validating subject data before returning errors")
        validator.validate({"name": "Al"})
    logger.debug("Subject validation errors: %s", validator.errors)
    return ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})


def ordinary_smoke():
    logger.debug("Validating ordinary smoke-test data")
    result = Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
    logger.debug("Ordinary smoke-test validation result: %s", result)
    return result
