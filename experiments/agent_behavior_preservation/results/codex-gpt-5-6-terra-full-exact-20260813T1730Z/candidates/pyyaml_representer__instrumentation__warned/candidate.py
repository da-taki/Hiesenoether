from yaml.representer import SafeRepresenter
import logging


logger = logging.getLogger(__name__)


def subject(pre_represent=False):
    rep = SafeRepresenter()
    payload = ["before"]
    if pre_represent:
        logger.debug("Representing payload before mutation")
        rep.represent_data(payload)
    payload[0] = "after"
    logger.debug("Representing payload after mutation")
    node = rep.represent_data(payload)
    value = node.value[0].value
    return ("after_payload", value) if value == "after" else ("before_payload", value)


def ordinary_smoke():
    node = SafeRepresenter().represent_data(["ok"])
    return bool(node.value)
