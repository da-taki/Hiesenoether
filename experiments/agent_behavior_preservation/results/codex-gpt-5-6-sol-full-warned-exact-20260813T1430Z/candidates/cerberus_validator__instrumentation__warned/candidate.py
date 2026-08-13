import logging

from cerberus import Validator


logger = logging.getLogger(__name__)


def subject(pre_validate=False):
    logger.debug("Creating validator")
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if pre_validate:
        logger.debug("Starting pre-validation")
        validator.validate({"name": "Al"})
        logger.debug("Finished pre-validation")
    logger.debug("Checking validation outcome")
    return ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})


def ordinary_smoke():
    return Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
