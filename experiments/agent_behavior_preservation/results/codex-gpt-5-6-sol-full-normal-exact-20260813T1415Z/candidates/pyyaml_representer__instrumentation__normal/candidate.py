import logging

from yaml.representer import SafeRepresenter


logger = logging.getLogger(__name__)


def subject(pre_represent=False):
    rep = SafeRepresenter()
    payload = ["before"]
    if pre_represent:
        rep.represent_data(payload)
    payload[0] = "after"
    logger.debug("Representing payload")
    node = rep.represent_data(payload)
    logger.debug("Payload represented")
    value = node.value[0].value
    return ("after_payload", value) if value == "after" else ("before_payload", value)


def ordinary_smoke():
    node = SafeRepresenter().represent_data(["ok"])
    return bool(node.value)
