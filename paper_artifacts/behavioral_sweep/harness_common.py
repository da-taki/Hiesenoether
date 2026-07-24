from __future__ import annotations

import importlib
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any

UNSAFE_METHOD_BITS = {
    "delete",
    "remove",
    "unlink",
    "rmdir",
    "write",
    "send",
    "connect",
    "request",
    "download",
    "upload",
    "commit",
    "execute",
}

NONDETERMINISTIC_METHOD_BITS = {
    "random",
    "entropy",
}

NOT_READ_OR_OBSERVER_METHODS = {
    "close",
}

def short(value: Any, limit: int = 500) -> str:
    try:
        text = repr(value)
    except Exception as exc:
        text = f"<repr failed: {type(exc).__name__}: {exc}>"
    text = re.sub(r"0x[0-9A-Fa-f]+", "0xADDR", text)
    return text if len(text) <= limit else text[: limit - 3] + "..."

def safe_state(obj: Any) -> dict[str, str]:
    try:
        raw = vars(obj)
    except Exception:
        return {}
    return {str(key): short(value, 160) for key, value in sorted(raw.items(), key=lambda kv: str(kv[0]))}

def find_import_name(source_root: Path, source_file: Path) -> tuple[str, Path]:
    path = source_file.resolve()
    package_parts = [path.stem]
    parent = path.parent
    while (parent / "__init__.py").exists():
        package_parts.insert(0, parent.name)
        parent = parent.parent
    return ".".join(package_parts), parent

def import_class(source_root: str, source_file: str, class_name: str) -> tuple[type[Any] | None, str]:
    root = Path(source_root)
    path = Path(source_file)
    module_name, import_root = find_import_name(root, path)
    candidates = [str(import_root), str(root), str(root / "src")]
    for candidate in reversed(candidates):
        if candidate not in sys.path:
            sys.path.insert(0, candidate)
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return None, f"import_failed: {type(exc).__name__}: {exc}"
    cls = getattr(module, class_name, None)
    if not isinstance(cls, type):
        return None, f"class_not_found: {class_name} in {module_name}"
    return cls, ""

def required_params(callable_obj: Any, skip_first: bool) -> list[str]:
    try:
        sig = inspect.signature(callable_obj)
    except (TypeError, ValueError):
        return ["<unknown signature>"]
    params = list(sig.parameters.values())
    if skip_first and params:
        params = params[1:]
    required = []
    for param in params:
        if param.kind in {param.VAR_POSITIONAL, param.VAR_KEYWORD}:
            continue
        if param.default is param.empty:
            required.append(param.name)
    return required

def construct(cls: type[Any]) -> tuple[Any | None, str]:
    req = required_params(cls, skip_first=False)
    if req:
        return None, "constructor requires arguments: " + ", ".join(req)
    try:
        return cls(), ""
    except Exception as exc:
        return None, f"constructor raised {type(exc).__name__}: {exc}"

def call_operation(obj: Any, method_name: str) -> dict[str, Any]:
    try:
        if method_name == "__next__":
            value = next(obj)
        elif method_name == "__iter__":
            value = iter(obj)
        elif method_name == "__hash__":
            value = hash(obj)
        elif method_name == "__bool__":
            value = bool(obj)
        elif method_name == "__len__":
            value = len(obj)
        elif method_name == "__str__":
            value = str(obj)
        elif method_name == "__repr__":
            value = repr(obj)
        elif method_name == "__enter__":
            value = obj.__enter__()
        elif method_name == "__exit__":
            value = obj.__exit__(None, None, None)
        else:
            target = getattr(obj, method_name)
            if callable(target):
                req = required_params(target, skip_first=False)
                if req:
                    return {"kind": "not_callable_without_args", "required": req}
                value = target()
            else:
                value = target
        return {"kind": "value", "value": short(value)}
    except Exception as exc:
        return {"kind": "exception", "type": type(exc).__name__, "message": str(exc)}

def run_case(meta: dict[str, Any]) -> dict[str, Any]:
    method_name = str(meta.get("expected_observer_or_read_operation") or "")
    if not method_name:
        return base_result(meta, "not_applicable_after_inspection", "no candidate operation parsed")
    if any(bit in method_name.lower() for bit in NONDETERMINISTIC_METHOD_BITS):
        return base_result(meta, "not_applicable_after_inspection", f"method name treated as nondeterministic: {method_name}")
    if method_name.lower() in NOT_READ_OR_OBSERVER_METHODS:
        return base_result(meta, "not_applicable_after_inspection", f"method is not treated as read/observer-shaped: {method_name}")
    if any(bit in method_name.lower() for bit in UNSAFE_METHOD_BITS):
        return base_result(meta, "unsafe_to_execute", f"method name treated as unsafe: {method_name}")

    cls, import_error = import_class(meta["source_root"], meta["source_path"], meta["class_name"])
    if cls is None:
        return base_result(meta, "import_failed", import_error)

    obj_a, err_a = construct(cls)
    obj_b, err_b = construct(cls)
    if obj_a is None or obj_b is None:
        return base_result(meta, "could_not_construct", err_a or err_b)

    before_a = safe_state(obj_a)
    before_b = safe_state(obj_b)
    if before_a != before_b:
        return base_result(
            meta,
            "not_applicable_after_inspection",
            "fresh instances were not comparable under canonical state snapshot",
        )
    result_a = call_operation(obj_a, method_name)
    after_a = safe_state(obj_a)

    observed_b = call_operation(obj_b, method_name)
    after_observed_b = safe_state(obj_b)
    result_b = call_operation(obj_b, method_name)
    after_b = safe_state(obj_b)

    output_diff = result_a != result_b
    branch_flip = result_a.get("kind") != result_b.get("kind")
    state_diff = after_a != after_b or before_b != after_observed_b
    if branch_flip:
        classification = "confirmed_branch_flip"
    elif output_diff:
        classification = "confirmed_output_divergence"
    elif state_diff:
        classification = "confirmed_state_divergence_only"
    else:
        classification = "structural_only_no_runtime_difference"

    return {
        **common_fields(meta),
        "classification": classification,
        "reproduced": classification.startswith("confirmed"),
        "output_diff": output_diff,
        "branch_flip": branch_flip,
        "state_diff": state_diff,
        "operation_A": f"{method_name}() once on fresh instance",
        "operation_B": f"{method_name}() once first; then {method_name}() again",
        "result_A": {"before": before_a, "result": result_a, "after": after_a},
        "result_B": {
            "before": before_b,
            "observation_result": observed_b,
            "after_observation": after_observed_b,
            "result": result_b,
            "after": after_b,
        },
        "failure_reason": "",
        "notes": "generic safe repeated-operation harness; confirmation depends on no-arg construction and no-arg operation",
    }

def common_fields(meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "sweep_rank": int(meta["sweep_rank"]),
        "package": meta["package"],
        "version": meta["version"],
        "class_name": meta["class_name"],
        "file_path": meta["file_path"],
        "selected_score": int(meta["score"]),
    }

def base_result(meta: dict[str, Any], classification: str, reason: str) -> dict[str, Any]:
    return {
        **common_fields(meta),
        "classification": classification,
        "reproduced": False,
        "output_diff": False,
        "branch_flip": False,
        "state_diff": False,
        "operation_A": "",
        "operation_B": "",
        "result_A": {},
        "result_B": {},
        "failure_reason": reason,
        "notes": "generic harness did not execute candidate behavior",
    }

def write_case(meta: dict[str, Any], output_path: str) -> int:
    result = run_case(meta)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0
