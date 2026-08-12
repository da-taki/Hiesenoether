from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[1]
ORACLE = REPO / "paper_artifacts" / "scp_realcode_metamorphic_oracle"
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(ORACLE))

import metamorphic_candidates as C
import metamorphic_fixtures as F
import run_branch_flip_cases as B
import run_metamorphic_controls as K
import run_metamorphic_oracle as O


HIDDEN = ["rc01_httpcore_Response", "rc03_pytest_catching_logs", "rc02_PyYAML_SafeRepresenter", "re10_cerberus_Validator"]
CALIBRATION = ["re08_boltons_LRU", "re11_dnspython_Tokenizer", "re12_h11_ChunkedReader", "re01_markdown_Markdown", "re06_beautifulsoup4_PageElement"]


def run_candidate_without_writing(cand: dict[str, object]) -> dict[str, object]:
    record = {
        "candidate_id": cand["candidate_id"],
        "package_name": cand["package_name"],
        "package_version": cand["package_version"],
        "constructed": False,
        "classification": "could_not_construct",
        "failure_reason": "",
    }
    try:
        spec = cand["harness"](F)
        if "custom" in spec:
            payload = spec["custom"]()
            order_a = O._normalize_custom(payload["order_A"])
            order_b = O._normalize_custom(payload["order_B"])
        else:
            spec["class_hint"] = cand["class_name"]
            if spec.get("pair_type", cand["pair_type"]) == "pair3":
                order_a, order_b = O._run_pair3(spec)
            else:
                order_a, order_b = O._run_pair1(spec)
        diff = O._classify(order_a, order_b)
        record.update(diff)
        record["constructed"] = True
        record["order_A"] = order_a
        record["order_B"] = order_b
    except Exception as exc:
        record["failure_reason"] = f"{type(exc).__name__}: {exc}"
    return record


def run_branch_cases() -> list[dict[str, object]]:
    selected = set(HIDDEN + CALIBRATION)
    rows = []
    for case in B.CASES:
        try:
            row = case()
        except Exception as exc:
            row = {
                "branch_case_id": case.__name__,
                "underlying_candidate_id": "",
                "classification": "could_not_construct",
                "branch_changed": False,
                "boundary_note": f"{type(exc).__name__}: {exc}",
            }
        if row.get("underlying_candidate_id") in selected or row["branch_case_id"].startswith("bc_"):
            rows.append(row)
    return rows


def run_controls() -> list[dict[str, object]]:
    K.rows.clear()
    for fn in (
        K.controls_httpcore,
        K.controls_markdown,
        K.controls_boltons_lru,
        K.controls_dnspython_tokenizer,
        K.controls_cerberus,
        K.controls_pytest,
        K.controls_pyyaml,
        K.controls_h11,
    ):
        try:
            fn()
        except Exception as exc:
            K.add(fn.__name__, "error", "n/a", f"{type(exc).__name__}: {exc}", False, "control raised unexpectedly")
    return list(K.rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    F.add_snapshot_paths()
    selected_ids = HIDDEN + CALIBRATION
    metamorphic = [run_candidate_without_writing(C.CANDIDATES_BY_ID[cid]) for cid in selected_ids]
    branch = run_branch_cases()
    controls = run_controls()
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "selected_ids": selected_ids,
        "metamorphic": metamorphic,
        "branch": branch,
        "controls": controls,
        "summary": {
            "metamorphic_counts": dict(Counter(str(r["classification"]) for r in metamorphic)),
            "branch_counts": dict(Counter(str(r["classification"]) for r in branch)),
            "controls": len(controls),
            "controls_removed_true": sum(1 for r in controls if r["divergence_removed"] is True),
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



