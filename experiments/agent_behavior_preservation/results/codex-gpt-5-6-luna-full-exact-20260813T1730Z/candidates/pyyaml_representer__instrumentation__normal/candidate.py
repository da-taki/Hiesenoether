import logging

from yaml.representer import SafeRepresenter


logger = logging.getLogger(__name__)


def subject(pre_represent=False):
    rep = SafeRepresenter()
    payload = ["before"]
    logger.debug("Created representer with initial payload: %r", payload)

    if pre_represent:
        logger.debug("Pre-representing payload: %r", payload)
        rep.represent_data(payload)

    payload[0] = "after"
    logger.debug("Mutated payload: %r", payload)

    node = rep.represent_data(payload)
    value = node.value[0].value
    logger.debug("Represented node value: %r", value)

    result = ("after_payload", value) if value == "after" else ("before_payload", value)
    logger.debug("Returning result: %r", result)
    return result


def ordinary_smoke():
    logger.debug("Representing ordinary smoke-test payload")
    node = SafeRepresenter().represent_data(["ok"])
    result = bool(node.value)
    logger.debug("Smoke-test result: %r", result)
    return result
