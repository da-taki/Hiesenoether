from cerberus import Validator
import logging


logger = logging.getLogger(__name__)


def subject(pre_validate=False):
    logger.debug("Creating validator")
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if pre_validate:
        logger.debug("Running pre-validation")
        validator.validate({"name": "Al"})
    result = ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})
    logger.debug("Returning subject result")
    return result


def ordinary_smoke():
    return Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
