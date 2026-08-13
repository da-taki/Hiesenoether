from cerberus import Validator
import logging


logger = logging.getLogger(__name__)


def subject(pre_validate=False):
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if pre_validate:
        logger.debug("Running pre-validation")
        validator.validate({"name": "Al"})
        logger.debug("Pre-validation completed")
    logger.debug("Inspecting validator state")
    return ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})


def ordinary_smoke():
    logger.debug("Running ordinary validation")
    result = Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
    logger.debug("Ordinary validation completed")
    return result
