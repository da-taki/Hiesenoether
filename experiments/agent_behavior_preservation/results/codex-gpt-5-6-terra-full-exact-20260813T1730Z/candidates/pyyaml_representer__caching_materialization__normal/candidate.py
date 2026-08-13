from yaml.representer import SafeRepresenter


def subject(pre_represent=False):
    rep = SafeRepresenter()
    payload = ["before"]
    node = rep.represent_data(payload) if pre_represent else None
    payload[0] = "after"
    node = node or rep.represent_data(payload)
    value = node.value[0].value
    return ("after_payload", value) if value == "after" else ("before_payload", value)


def ordinary_smoke():
    node = SafeRepresenter().represent_data(["ok"])
    return bool(node.value)
