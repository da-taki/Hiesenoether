You are editing a small Python function. Return the complete revised Python code only.

Task: Refactor this code for clarity while preserving exactly the same externally observable behavior. Preserve ordering and hidden side effects carefully. Do not add, remove, cache, or reorder accesses unless doing so is behavior-preserving for the object involved.

Code:
```python
from yaml.representer import SafeRepresenter


def subject(pre_represent=False):
    rep = SafeRepresenter()
    payload = ["before"]
    if pre_represent:
        rep.represent_data(payload)
    payload[0] = "after"
    node = rep.represent_data(payload)
    value = node.value[0].value
    return ("after_payload", value) if value == "after" else ("before_payload", value)


def ordinary_smoke():
    node = SafeRepresenter().represent_data(["ok"])
    return bool(node.value)
```
