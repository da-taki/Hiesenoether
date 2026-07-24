from __future__ import annotations

import ast
import csv
import random
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SNAPSHOT = OUT / "source_snapshot"
MANIFEST = OUT / "source_snapshot_manifest.csv"
FINDINGS = REPO / "results_static" / "pypi_static_benchmark_findings.csv"
SUMMARY = REPO / "results_static" / "pypi_static_benchmark.csv"
SAMPLE_CSV = OUT / "unflagged_audit_v2_sample.csv"
SUMMARY_CSV = OUT / "unflagged_audit_v2_summary.csv"
REPORT = OUT / "unflagged_audit_v2_report.md"
SEED = 20260706

READ_NAMES = {"read", "get", "fetch", "peek", "value", "current", "__get__", "__getattr__", "__getitem__", "__iter__", "__next__", "__call__", "__len__", "__bool__", "__hash__", "content"}
OBS_NAMES = {"observe", "inspect", "snapshot", "debug", "trace", "log", "__repr__", "__str__", "__format__"}
MUTATING_CALLS = {"append", "extend", "insert", "pop", "remove", "clear", "update", "add", "discard", "setdefault"}

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def norm(name: str) -> str:
    return name.replace("_", "-").lower()

def path_parts(text: str) -> list[str]:
    return [part for part in text.replace("\\", "/").split("/") if part]

def path_matches(finding_path: str, rel_path: str) -> bool:
    f_parts = path_parts(finding_path)
    r_parts = path_parts(rel_path)
    if not f_parts or not r_parts:
        return False
    if f_parts[-len(r_parts):] == r_parts:
        return True
    if len(f_parts) >= 2 and len(r_parts) >= 2 and f_parts[-2:] == r_parts[-2:]:
        return True
    if f_parts[-1] == r_parts[-1]:
        return True
    return False

def source_roots() -> dict[str, Path]:
    roots = {}
    if not MANIFEST.exists():
        return roots
    for row in read_csv(MANIFEST):
        if row["source_status"] != "missing" and int(row["files_count"] or 0) > 0:
            roots[row["package"]] = Path(row["source_path"])
    return roots

def class_nodes(package: str, root: Path) -> list[dict[str, object]]:
    out = []
    for path in root.rglob("*.py"):
        parts = {part.lower() for part in path.relative_to(root).parts[:-1]}
        if parts & {"test", "tests", "docs", "doc", "examples", "example"}:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                out.append({"package": package, "path": path, "rel": str(path.relative_to(root)), "node": node})
    return out

def self_attr(node: ast.AST) -> str | None:
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
        return node.attr
    return None

def assigned_fields(fn: ast.FunctionDef) -> set[str]:
    fields = set()
    for node in ast.walk(fn):
        targets = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, ast.AugAssign):
            targets = [node.target]
        for target in targets:
            attr = self_attr(target)
            if attr:
                fields.add(attr)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in MUTATING_CALLS:
            attr = self_attr(node.func.value)
            if attr:
                fields.add(attr)
    return fields

def returned_fields(fn: ast.FunctionDef) -> set[str]:
    fields = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and node.value is not None:
            for sub in ast.walk(node.value):
                attr = self_attr(sub)
                if attr:
                    fields.add(attr)
    return fields

def is_property(fn: ast.FunctionDef) -> bool:
    return any(isinstance(dec, ast.Name) and dec.id == "property" for dec in fn.decorator_list)

def audit(item: dict[str, object]) -> dict[str, object]:
    node: ast.ClassDef = item["node"]
    methods = [child for child in node.body if isinstance(child, ast.FunctionDef)]
    read_methods = [m for m in methods if m.name in READ_NAMES or m.name.startswith(("read", "get", "fetch")) or is_property(m)]
    obs_methods = [m for m in methods if m.name in OBS_NAMES or m.name.startswith(("observe", "inspect", "debug"))]
    mutating_reads = [m for m in read_methods if assigned_fields(m)]
    mutating_obs = [m for m in obs_methods if assigned_fields(m)]
    mutated = set().union(*(assigned_fields(m) for m in mutating_reads + mutating_obs)) if (mutating_reads or mutating_obs) else set()
    consumed = set().union(*(returned_fields(m) for m in read_methods)) if read_methods else set()
    concrete = bool(mutated & consumed)
    if concrete:
        label = "likely_missed_match"
        evidence = f"mutated fields consumed by read-shaped return: {sorted(mutated & consumed)}"
    elif mutating_reads or mutating_obs:
        label = "uncertain"
        evidence = f"mutating read/observer found but no concrete later consumed field: {sorted(mutated)}"
    else:
        label = "likely_nonmatch"
        evidence = "no concrete read/observer mutate-then-consume loop"
    return {
        "package": item["package"],
        "file_path": item["rel"],
        "class_name": node.name,
        "line_start": node.lineno,
        "line_end": getattr(node, "end_lineno", node.lineno),
        "read_shaped_methods_or_properties": ";".join(m.name for m in read_methods),
        "observation_like_methods": ";".join(m.name for m in obs_methods),
        "mutated_state": ";".join(sorted(mutated)),
        "audit_label": label,
        "evidence_note": evidence,
    }

def frac(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"

def run() -> dict[str, object]:
    roots = source_roots()
    all_classes = []
    for package, root in roots.items():
        all_classes.extend(class_nodes(package, root))
    finding_rows = read_csv(FINDINGS)
    flagged_matches = set()
    for item in all_classes:
        node = item["node"]
        for row in finding_rows:
            if row["package"] == item["package"] and row["name"] == node.name and path_matches(row["file_path"], str(item["rel"])):
                flagged_matches.add((item["package"], item["rel"], node.name))
                break
    unflagged = [
        item for item in all_classes
        if (item["package"], item["rel"], item["node"].name) not in flagged_matches
    ]
    rng = random.Random(SEED)
    sample_n = min(200, len(unflagged))
    sample = rng.sample(unflagged, sample_n) if sample_n < len(unflagged) else unflagged
    rows = [audit(item) for item in sorted(sample, key=lambda x: (str(x["package"]), str(x["rel"]), x["node"].lineno))]
    with SAMPLE_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["package", "file_path", "class_name", "line_start", "line_end", "read_shaped_methods_or_properties", "observation_like_methods", "mutated_state", "audit_label", "evidence_note"])
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(row["audit_label"] for row in rows)
    review_counts = Counter(row["manual_review"] for row in read_csv(FINDINGS))
    tp = review_counts["likely true positive"]
    fp = review_counts["likely false positive"]
    if not all_classes or sample_n == 0:
        est_fn = recall = None
    else:
        unflagged_count = len(unflagged)
        est_fn = Fraction(counts["likely_missed_match"], sample_n) * unflagged_count
        recall = Fraction(tp, 1) / (Fraction(tp, 1) + est_fn) if tp or est_fn else Fraction(0)
    def sensitivity(uncertain_weight: Fraction) -> tuple[Fraction | None, Fraction | None]:
        if not sample_n:
            return None, None
        misses = Fraction(counts["likely_missed_match"], 1) + uncertain_weight * counts["uncertain"]
        fn = misses / sample_n * len(unflagged)
        rec = Fraction(tp, 1) / (Fraction(tp, 1) + fn) if tp or fn else Fraction(0)
        return fn, rec
    sens = {
        "nonmatch": sensitivity(Fraction(0)),
        "half_missed": sensitivity(Fraction(1, 2)),
        "missed": sensitivity(Fraction(1)),
    }
    summary = {
        "total_corpus_classes": len(all_classes),
        "flagged_classes_or_findings": len(finding_rows),
        "likely_flagged_matches": tp,
        "likely_flagged_false_positives": fp,
        "unflagged_classes": len(unflagged),
        "sampled_unflagged_classes": sample_n,
        "likely_missed_matches": counts["likely_missed_match"],
        "likely_nonmatches": counts["likely_nonmatch"],
        "uncertain_cases": counts["uncertain"],
        "estimated_false_negatives": "not_computed_no_snapshot" if est_fn is None else frac(est_fn),
        "estimated_recall": "not_computed_no_snapshot" if recall is None else frac(recall),
        "uncertainty_note": "computed only over successfully rebuilt source snapshot; not full reviewed corpus unless total classes=4437",
    }
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summary))
        writer.writeheader()
        writer.writerow(summary)
    write_report(summary, sens)
    return summary

def write_report(summary: dict[str, object], sens: dict[str, tuple[Fraction | None, Fraction | None]]) -> None:
    lines = [
        "# Unflagged Recall Audit V2",
        "",
        "| total_corpus_classes | flagged_classes_or_findings | likely_flagged_matches | likely_flagged_false_positives | unflagged_classes | sampled_unflagged_classes | likely_missed_matches | likely_nonmatches | uncertain_cases | estimated_false_negatives | estimated_recall |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        f"| {summary['total_corpus_classes']} | {summary['flagged_classes_or_findings']} | {summary['likely_flagged_matches']} | {summary['likely_flagged_false_positives']} | {summary['unflagged_classes']} | {summary['sampled_unflagged_classes']} | {summary['likely_missed_matches']} | {summary['likely_nonmatches']} | {summary['uncertain_cases']} | {summary['estimated_false_negatives']} | {summary['estimated_recall']} |",
        "",
        "## Sensitivity",
        "",
        "| Treat uncertain as | Estimated FN | Estimated recall |",
        "| --- | ---: | ---: |",
    ]
    for label, (fn, rec) in sens.items():
        lines.append(f"| {label} | {'not_computed' if fn is None else frac(fn)} | {'not_computed' if rec is None else frac(rec)} |")
    lines.extend(["", f"Uncertainty note: {summary['uncertainty_note']}"])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    summary = run()
    print(f"wrote {SAMPLE_CSV}")
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {REPORT}")
    print(summary)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
