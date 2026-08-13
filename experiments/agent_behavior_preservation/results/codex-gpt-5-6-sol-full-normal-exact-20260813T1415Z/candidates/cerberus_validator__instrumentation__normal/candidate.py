import logging

from cerberus import Validator


logger = logging.getLogger(__name__)


def subject(pre_validate=False):
    logger.debug("Creating validator", extra={"pre_validate": pre_validate})
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if pre_validate:
        logger.debug("Starting pre-validation")
        validator.validate({"name": "Al"})
        logger.debug("Finished pre-validation", extra={"errors": dict(validator.errors)})
    result = ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})
    logger.debug("Subject completed", extra={"result": result})
    return result


def ordinary_smoke():
    return Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
