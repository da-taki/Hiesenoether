from __future__ import annotations

import json
from pathlib import Path

import httpcore


OUT = Path(__file__).resolve().parents[1] / "real_case_outputs" / "case_1_httpcore_Response.json"


def make_response() -> httpcore.Response:
    return httpcore.Response(200, content=[b"alpha", b"beta"])


def state(resp: httpcore.Response) -> dict[str, object]:
    return {
        "has__content": hasattr(resp, "_content"),
        "stream_consumed": getattr(resp, "_stream_consumed", None),
    }


def order_a() -> dict[str, object]:
    resp = make_response()
    before = state(resp)
    try:
        later = resp.content
        result = {"kind": "value", "value": later.decode()}
    except Exception as exc:
        result = {"kind": "exception", "type": type(exc).__name__, "message": str(exc)}
    return {"before": before, "after": state(resp), "result": result}


def order_b() -> dict[str, object]:
    resp = make_response()
    before = state(resp)
    observed = resp.read()
    mid = state(resp)
    try:
        later = resp.content
        result = {"kind": "value", "value": later.decode()}
    except Exception as exc:
        result = {"kind": "exception", "type": type(exc).__name__, "message": str(exc)}
    return {
        "before": before,
        "observation_result": observed.decode(),
        "after_observation": mid,
        "after": state(resp),
        "result": result,
    }


def main() -> int:
    a = order_a()
    b = order_b()
    output_diff = a["result"] != b["result"]
    state_diff = a["after"] != b["after"]
    data = {
        "case_id": "case_1_httpcore_Response",
        "package": "httpcore",
        "version": httpcore.__version__,
        "class_name": "Response",
        "file_path": "httpcore/_models.py",
        "operation_A": "response.content without prior response.read()",
        "result_A": a,
        "operation_B": "response.read(); then response.content",
        "result_B": b,
        "branch_flip": output_diff,
        "output_diff": output_diff,
        "state_diff": state_diff,
        "classification": "confirmed_branch_flip" if output_diff else "structural_only_no_runtime_difference",
        "read_or_observer_operation": "Response.read()",
        "latent_state": "_content and _stream_consumed",
        "later_read_or_behavior": "Response.content",
        "notes": "Real package API; read-shaped access materializes content and changes later content access from exception to value.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
