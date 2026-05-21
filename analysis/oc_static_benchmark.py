from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from analysis.oc_static import analyze_file


EXPECTED_ORDER = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
BENCHMARK_FILE = Path(__file__).with_name("benchmark_examples.py")


def expected_labels(path: Path) -> Dict[str, str]:
    labels: Dict[str, str] = {}
    namespace: dict = {}
    exec(path.read_text(), namespace)
    for name, obj in namespace.items():
        label = getattr(obj, "expected_risk", None)
        if label is not None:
            labels[name] = label
    return labels


def evaluate_benchmark(path: Path = BENCHMARK_FILE) -> dict:
    expected = expected_labels(path)
    result = analyze_file(path)
    observed = {c["class"]: c["risk_label"] for c in result["classes"]
                if c["class"] in expected}

    rows: List[dict] = []
    tp = fp = fn = 0
    for cls, expected_label in sorted(expected.items()):
        observed_label = observed.get(cls, "MISSING")
        expected_positive = expected_label != "SAFE"
        observed_positive = observed_label != "SAFE"
        if expected_positive and observed_positive:
            tp += 1
        elif not expected_positive and observed_positive:
            fp += 1
        elif expected_positive and not observed_positive:
            fn += 1
        rows.append({
            "class": cls,
            "expected": expected_label,
            "observed": observed_label,
            "exact_match": expected_label == observed_label,
            "severity_delta": None if observed_label == "MISSING"
                              else EXPECTED_ORDER[observed_label] - EXPECTED_ORDER[expected_label],
        })

    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    exact = sum(1 for row in rows if row["exact_match"])

    return {
        "benchmark_file": str(path),
        "cases": len(rows),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "exact_label_accuracy": round(exact / len(rows), 4) if rows else 1.0,
        "rows": rows,
        "module_level_nonlinear_uses": result["module_level_nonlinear_uses"],
    }


def main() -> int:
    report = evaluate_benchmark()
    print(json.dumps(report, indent=2))
    return 0 if report["false_negatives"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
