from __future__ import annotations

import json
import sys
from pathlib import Path

SNAPSHOT = Path(__file__).resolve().parents[1] / "source_snapshot" / "pyyaml-6.0.3"
TEMP = Path.home() / "AppData" / "Local" / "Temp" / "hiesenoether_pypi_static_benchmark" / "sources" / "pyyaml"
if SNAPSHOT.exists():
    sys.path.insert(0, str(SNAPSHOT))
elif TEMP.exists():
    sys.path.insert(0, str(TEMP))

import yaml
from yaml.representer import SafeRepresenter

OUT = Path(__file__).resolve().parents[1] / "real_case_outputs" / "case_3_pyyaml_SafeRepresenter.json"

def node_payload(node: object) -> str:
    value = getattr(node, "value", None)
    return repr(value)

def order_a() -> dict[str, object]:
    rep = SafeRepresenter()
    data = ["before"]
    data[0] = "after"
    node = rep.represent_data(data)
    return {
        "represented_objects": len(rep.represented_objects),
        "object_keeper": len(rep.object_keeper),
        "node_payload": node_payload(node),
    }

def order_b() -> dict[str, object]:
    rep = SafeRepresenter()
    data = ["before"]
    first = rep.represent_data(data)
    before_mutation_payload = node_payload(first)
    data[0] = "after"
    second = rep.represent_data(data)
    return {
        "represented_objects": len(rep.represented_objects),
        "object_keeper": len(rep.object_keeper),
        "first_payload": before_mutation_payload,
        "node_payload": node_payload(second),
        "same_node_returned": first is second,
    }

def main() -> int:
    a = order_a()
    b = order_b()
    output_diff = a["node_payload"] != b["node_payload"]
    state_diff = a["represented_objects"] != b["represented_objects"] or a["object_keeper"] != b["object_keeper"]
    data = {
        "case_id": "case_3_pyyaml_SafeRepresenter",
        "package": "PyYAML",
        "version": yaml.__version__,
        "class_name": "SafeRepresenter",
        "file_path": "yaml/representer.py",
        "operation_A": "mutate list; then represent_data(list)",
        "result_A": a,
        "operation_B": "represent_data(list); mutate same list; then represent_data(list)",
        "result_B": b,
        "branch_flip": False,
        "output_diff": output_diff,
        "state_diff": state_diff,
        "classification": "confirmed_output_divergence" if output_diff else "structural_only_no_runtime_difference",
        "read_or_observer_operation": "SafeRepresenter.represent_data()",
        "latent_state": "represented_objects/object_keeper alias cache",
        "later_read_or_behavior": "later represent_data() of the same object",
        "notes": "Low-level representer API. The full dumper resets state after represent(); this harness demonstrates the underlying access-observation feedback boundary.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
