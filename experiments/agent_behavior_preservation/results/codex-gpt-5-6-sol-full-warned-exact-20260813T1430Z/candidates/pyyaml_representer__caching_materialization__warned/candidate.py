from yaml.representer import SafeRepresenter


def subject(pre_represent=False):
    rep = SafeRepresenter()
    payload = ["before"]
    node = None
    if pre_represent:
        node = rep.represent_data(payload)
    payload[0] = "after"
    if node is None:
        node = rep.represent_data(payload)
    value = node.value[0].value
    return ("after_payload", value) if value == "after" else ("before_payload", value)


def ordinary_smoke():
    node = SafeRepresenter().represent_data(["ok"])
    return bool(node.value)
