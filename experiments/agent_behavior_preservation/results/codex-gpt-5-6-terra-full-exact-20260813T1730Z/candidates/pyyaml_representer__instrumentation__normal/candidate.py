from yaml.representer import SafeRepresenter
import logging


logger = logging.getLogger(__name__)


def subject(pre_represent=False):
    rep = SafeRepresenter()
    payload = ["before"]
    logger.debug("Created payload: %r", payload)

    if pre_represent:
        logger.debug("Representing payload before mutation")
        rep.represent_data(payload)

    payload[0] = "after"
    logger.debug("Mutated payload: %r", payload)

    node = rep.represent_data(payload)
    value = node.value[0].value
    result = ("after_payload", value) if value == "after" else ("before_payload", value)
    logger.debug("Representation value: %r; result: %r", value, result)
    return result


def ordinary_smoke():
    node = SafeRepresenter().represent_data(["ok"])
    return bool(node.value)
