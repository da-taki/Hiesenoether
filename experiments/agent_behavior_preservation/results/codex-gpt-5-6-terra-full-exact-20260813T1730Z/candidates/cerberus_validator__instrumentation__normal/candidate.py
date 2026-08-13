from cerberus import Validator
import logging


logger = logging.getLogger(__name__)


def subject(pre_validate=False):
    validator = Validator({"name": {"type": "string", "minlength": 3}})
    if pre_validate:
        document = {"name": "Al"}
        logger.debug("Starting validation: %r", document)
        validator.validate(document)
        logger.debug("Validation completed; errors: %r", validator.errors)
    return ("has_errors", dict(validator.errors)) if validator.errors else ("clean", {})


def ordinary_smoke():
    return Validator({"name": {"type": "string"}}).validate({"name": "Alice"})
