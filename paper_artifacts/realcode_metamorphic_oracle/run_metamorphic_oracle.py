from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import metamorphic_fixtures as F
import metamorphic_candidates as C

TRACES_DIR = BASE / "traces"
POOL_CSV = BASE / "metamorphic_candidate_pool.csv"
RESULTS_JSON = BASE / "metamorphic_results.json"
RESULTS_CSV = BASE / "metamorphic_results.csv"

CONFIRMED = {
    "confirmed_output_divergence",
    "confirmed_exception_divergence",
    "confirmed_branch_divergence",
    "confirmed_output_and_branch_divergence",
    "confirmed_state_only_divergence",
}
CONSTRUCTED_CLASSES = CONFIRMED | {"no_divergence"}

RESULT_FIELDS = [
    "candidate_id", "package_name", "package_version", "class_name",
    "observation_operation", "target_read_operation", "pair_type", "fixture_family",
    "constructed", "order_A_steps", "order_B_steps", "order_A_output", "order_B_output",
    "order_A_exception", "order_B_exception", "order_A_state", "order_B_state",
    "output_changed", "exception_changed", "branch_changed", "state_changed",
    "classification", "boundary_note", "failure_reason",
]

def _cap(fn):
    try:
        return {"kind": "value", "value": F.snapshot(fn())}
    except Exception as exc:
        return {"kind": "exception", "type": type(exc).__name__, "message": str(exc)[:400]}

def _run_pair1(spec):
    builder, obs, target = spec["builder"], spec["observation"], spec["target"]
    state = spec.get("state", lambda o: {})
    obs_label, read_label = spec.get("obs_label", "observe"), spec.get("read_label", "read")

    oa = builder()
    ra = _cap(lambda: target(oa))
    sa = F.snapshot(state(oa))

    ob = builder()
    obs_res = _cap(lambda: obs(ob))
    rb = _cap(lambda: target(ob))
    sb = F.snapshot(state(ob))

    order_A = {"steps": [f"construct {spec.get('class_hint','object')}", read_label],
               "results": [ra], "state": sa}
    order_B = {"steps": [f"construct {spec.get('class_hint','object')}", obs_label, read_label],
               "results": [rb], "state": sb, "observation": obs_res}
    return order_A, order_B

def _run_pair3(spec):
    builder, obs, target = spec["builder"], spec["observation"], spec["target"]
    state = spec.get("state", lambda o: {})
    obs_label, read_label = spec.get("obs_label", "observe"), spec.get("read_label", "read")

    oa = builder()
    ra1 = _cap(lambda: target(oa))
    ra2 = _cap(lambda: target(oa))
    sa = F.snapshot(state(oa))

    ob = builder()
    obs_res = _cap(lambda: obs(ob))
    rb1 = _cap(lambda: target(ob))
    rb2 = _cap(lambda: target(ob))
    sb = F.snapshot(state(ob))

    order_A = {"steps": ["construct", read_label, read_label], "results": [ra1, ra2], "state": sa}
    order_B = {"steps": ["construct", obs_label, read_label, read_label],
               "results": [rb1, rb2], "state": sb, "observation": obs_res}
    return order_A, order_B

def _normalize_custom(order):
    if order.get("exception") is not None:
        exc = order["exception"]
        cap = {"kind": "exception", "type": exc.get("type", "Exception"),
               "message": str(exc.get("message", ""))[:400]}
    else:
        cap = {"kind": "value", "value": F.snapshot(order.get("output"))}
    return {"steps": order.get("steps", []), "results": [cap],
            "state": F.snapshot(order.get("state", {}))}

def _classify(order_A, order_B):
    ra, rb = order_A["results"], order_B["results"]
    n = max(len(ra), len(rb))
    branch_changed = exception_changed = output_changed = False
    for i in range(n):
        a = ra[i] if i < len(ra) else {"kind": "missing"}
        b = rb[i] if i < len(rb) else {"kind": "missing"}
        ka, kb = a.get("kind"), b.get("kind")
        if ka != kb:
            branch_changed = True
        elif ka == "value":
            if a.get("value") != b.get("value"):
                output_changed = True
        elif ka == "exception":
            if (a.get("type"), a.get("message")) != (b.get("type"), b.get("message")):
                exception_changed = True
    state_changed = order_A.get("state") != order_B.get("state")

    if branch_changed and output_changed:
        classification = "confirmed_output_and_branch_divergence"
    elif branch_changed:
        classification = "confirmed_branch_divergence"
    elif exception_changed:
        classification = "confirmed_exception_divergence"
    elif output_changed:
        classification = "confirmed_output_divergence"
    elif state_changed:
        classification = "confirmed_state_only_divergence"
    else:
        classification = "no_divergence"
    return {
        "output_changed": output_changed,
        "exception_changed": exception_changed,
        "branch_changed": branch_changed,
        "state_changed": state_changed,
        "classification": classification,
    }

def _summ_outputs(order):
    return [r.get("value") for r in order["results"] if r.get("kind") == "value"]

def _summ_exceptions(order):
    return [f"{r.get('type')}: {r.get('message')}" for r in order["results"]
            if r.get("kind") == "exception"]

def run_candidate(cand):
    cid = cand["candidate_id"]
    record = {
        "candidate_id": cid,
        "package_name": cand["package_name"],
        "package_version": cand["package_version"],
        "class_name": cand["class_name"],
        "observation_operation": cand["observation_operation"],
        "target_read_operation": cand["target_read_operation"],
        "pair_type": cand["pair_type"],
        "fixture_family": cand["fixture_family"],
        "constructed": False,
        "order_A_steps": "", "order_B_steps": "",
        "order_A_output": "", "order_B_output": "",
        "order_A_exception": "", "order_B_exception": "",
        "order_A_state": "", "order_B_state": "",
        "output_changed": False, "exception_changed": False,
        "branch_changed": False, "state_changed": False,
        "classification": "could_not_construct",
        "boundary_note": cand["expected_boundary"],
        "failure_reason": "",
    }
    trace = {"candidate_id": cid, "metadata": {k: cand[k] for k in C.POOL_FIELDS}}

    harness = cand["harness"]
    try:
        spec = harness(F)
        if "custom" in spec:
            payload = spec["custom"]()
            order_A = _normalize_custom(payload["order_A"])
            order_B = _normalize_custom(payload["order_B"])
            pair_type = cand["pair_type"]
        else:
            pair_type = spec.get("pair_type", cand["pair_type"])
            spec["class_hint"] = cand["class_name"]
            if pair_type == "pair3":
                order_A, order_B = _run_pair3(spec)
            else:
                order_A, order_B = _run_pair1(spec)
                pair_type = "pair1"
        record["pair_type"] = pair_type
        diff = _classify(order_A, order_B)
        record.update(diff)
        record["constructed"] = True
        record["order_A_steps"] = " | ".join(order_A["steps"])
        record["order_B_steps"] = " | ".join(order_B["steps"])
        record["order_A_output"] = json.dumps(_summ_outputs(order_A))
        record["order_B_output"] = json.dumps(_summ_outputs(order_B))
        record["order_A_exception"] = json.dumps(_summ_exceptions(order_A))
        record["order_B_exception"] = json.dumps(_summ_exceptions(order_B))
        record["order_A_state"] = json.dumps(order_A.get("state"))
        record["order_B_state"] = json.dumps(order_B.get("state"))
        trace["order_A"] = order_A
        trace["order_B"] = order_B
        trace["diff"] = diff
    except (ImportError, ModuleNotFoundError) as exc:
        record["classification"] = "import_failed"
        record["failure_reason"] = f"{type(exc).__name__}: {exc}"
    except F.FixtureUnavailable as exc:
        record["classification"] = "fixture_unavailable"
        record["failure_reason"] = str(exc)
    except C.CouldNotConstruct as exc:
        record["classification"] = "could_not_construct"
        record["failure_reason"] = str(exc)
    except C.NotRelevant as exc:
        record["classification"] = "not_relevant_after_inspection"
        record["failure_reason"] = str(exc)
    except C.UnsafeToExecute as exc:
        record["classification"] = "unsafe_to_execute"
        record["failure_reason"] = str(exc)
    except Exception as exc:
        record["classification"] = "could_not_construct"
        record["failure_reason"] = f"{type(exc).__name__}: {exc}"

    trace["record"] = record
    (TRACES_DIR / f"{cid}.json").write_text(
        json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record

def write_pool_csv():
    with POOL_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=C.POOL_FIELDS)
        writer.writeheader()
        for cand in C.CANDIDATES:
            writer.writerow({k: cand[k] for k in C.POOL_FIELDS})

def main() -> int:
    F.add_snapshot_paths()
    TRACES_DIR.mkdir(parents=True, exist_ok=True)
    write_pool_csv()

    records = []
    for cand in C.CANDIDATES:
        if cand["selected_for_harness"] != "yes":
            continue
        records.append(run_candidate(cand))

    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)

    from collections import Counter
    counts = Counter(r["classification"] for r in records)
    summary = {
        "selected": len(records),
        "constructed": sum(1 for r in records if r["constructed"]),
        "classification_counts": dict(sorted(counts.items())),
        "confirmed_output_divergence": counts.get("confirmed_output_divergence", 0)
        + counts.get("confirmed_output_and_branch_divergence", 0),
        "confirmed_exception_divergence": counts.get("confirmed_exception_divergence", 0),
        "confirmed_branch_divergence": counts.get("confirmed_branch_divergence", 0)
        + counts.get("confirmed_output_and_branch_divergence", 0),
        "confirmed_state_only_divergence": counts.get("confirmed_state_only_divergence", 0),
        "no_divergence": counts.get("no_divergence", 0),
        "failed": sum(1 for r in records if not r["constructed"]),
    }
    RESULTS_JSON.write_text(
        json.dumps({"summary": summary, "records": records}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
