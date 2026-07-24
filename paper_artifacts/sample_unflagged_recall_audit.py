from __future__ import annotations

import ast
import csv
import random
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from analysis.oc_static import analyze_file
from analysis.pypi_static_benchmark import (
    FINDINGS_CSV,
    SKIP_DIRS,
    SOURCE_DIR,
    SUMMARY_CSV,
    normalize_name,
    version_from_metadata,
)

OUT_DIR = REPO / "paper_artifacts"
SAMPLE_CSV = OUT_DIR / "unflagged_audit_sample.csv"
SUMMARY_CSV_OUT = OUT_DIR / "unflagged_audit_summary.csv"
REPORT_MD = OUT_DIR / "unflagged_audit_report.md"
FALLBACK_QUEUE = REPO / "results" / "review_experiments" / "pypi_expanded_manual_review_queue.csv"
SEED = 20260706
TARGET_SAMPLE = 200

READ_NAMES = {
    "read",
    "get",
    "fetch",
    "peek",
    "value",
    "current",
    "__get__",
    "__getattr__",
    "__getattribute__",
    "__getitem__",
    "__iter__",
    "__next__",
    "__call__",
    "__len__",
    "__bool__",
    "__contains__",
    "__hash__",
}
OBS_NAMES = {
    "observe",
    "inspect",
    "snapshot",
    "sample",
    "watch",
    "debug",
    "trace",
    "log",
    "__repr__",
    "__str__",
    "__format__",
}
MUTATING_METHODS = {
    "append",
    "extend",
    "insert",
    "pop",
    "remove",
    "clear",
    "update",
    "add",
    "discard",
    "setdefault",
}

@dataclass(frozen=True)
class ClassRecord:
    package: str
    version: str
    root: Path
    file_path: str
    abs_path: Path
    class_name: str
    line: int
    end_line: int
    analyzer_label: str

    @property
    def key(self) -> tuple[str, str, str, int]:
        return (self.package, self.file_path, self.class_name, self.line)

def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def iter_python_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.py")):
        parts = {p.lower() for p in path.relative_to(root).parts[:-1]}
        if parts & SKIP_DIRS:
            continue
        name = path.name.lower()
        if name.startswith("test") or name == "conftest.py":
            continue
        yield path

def python_file_count(root: Path | None) -> int:
    return 0 if root is None else sum(1 for _ in root.rglob("*.py"))

def unwrap_single_source_dir(root: Path) -> Path:
    if python_file_count(root):
        return root
    children = [child for child in root.iterdir() if child.is_dir()]
    if len(children) == 1 and python_file_count(children[0]):
        return children[0]
    return root

def source_root_for_package(package: str) -> Path | None:
    target = SOURCE_DIR / normalize_name(package)
    if target.exists():
        root = unwrap_single_source_dir(target)
        if python_file_count(root):
            return root
    return None

def collect_classes() -> list[ClassRecord]:
    package_rows = [row for row in read_csv(SUMMARY_CSV) if row["status"] == "analyzed"]
    records: list[ClassRecord] = []
    for row in package_rows:
        package = row["package"]
        root = source_root_for_package(package)
        if root is None:
            continue
        version = row.get("version") or version_from_metadata(root)
        for py_file in iter_python_files(root):
            try:
                result = analyze_file(py_file)
            except (SyntaxError, UnicodeDecodeError, OSError):
                continue
            rel_file = str(py_file.relative_to(root))
            for cls in result["classes"]:
                records.append(
                    ClassRecord(
                        package=package,
                        version=version,
                        root=root,
                        file_path=rel_file,
                        abs_path=py_file,
                        class_name=cls["class"],
                        line=int(cls["line"]),
                        end_line=int(cls.get("end_line") or cls["line"]),
                        analyzer_label=cls["risk_label"],
                    )
                )
    return records

def node_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return node_name(node.func)
    return ""

def is_property(method: ast.FunctionDef) -> bool:
    return any(node_name(dec) == "property" for dec in method.decorator_list)

def is_read_shaped(method: ast.FunctionDef) -> bool:
    return (
        method.name in READ_NAMES
        or method.name.startswith(("read", "get", "fetch"))
        or is_property(method)
    )

def is_observation_shaped(method: ast.FunctionDef) -> bool:
    return method.name in OBS_NAMES or method.name.startswith(("observe", "inspect", "debug"))

def self_attr(node: ast.AST) -> str | None:
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
        return node.attr
    return None

def assigned_self_fields(method: ast.FunctionDef) -> set[str]:
    fields: set[str] = set()
    for node in ast.walk(method):
        targets = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        elif isinstance(node, ast.AugAssign):
            targets = [node.target]
        elif isinstance(node, ast.Delete):
            targets = list(node.targets)
        for target in targets:
            attr = self_attr(target)
            if attr:
                fields.add(attr)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in MUTATING_METHODS:
                owner = self_attr(node.func.value)
                if owner:
                    fields.add(owner)
    return fields

def return_reads(method: ast.FunctionDef) -> set[str]:
    fields: set[str] = set()
    for node in ast.walk(method):
        if isinstance(node, ast.Return) and node.value is not None:
            for sub in ast.walk(node.value):
                attr = self_attr(sub)
                if attr:
                    fields.add(attr)
    return fields

def method_has_return_value(method: ast.FunctionDef) -> bool:
    return any(isinstance(node, ast.Return) and node.value is not None for node in ast.walk(method))

def has_dynamic_state_access(class_node: ast.ClassDef) -> bool:
    for node in ast.walk(class_node):
        if isinstance(node, ast.Call) and node_name(node.func) in {"setattr", "delattr", "getattr"}:
            return True
        if isinstance(node, ast.Attribute) and node.attr == "__dict__":
            return True
    return False

def has_composition_or_threshold(class_node: ast.ClassDef) -> bool:
    for node in ast.walk(class_node):
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Mult, ast.Pow)):
            return True
        if isinstance(node, ast.Compare):
            return True
        if isinstance(node, ast.If):
            return True
    return False

def find_class_node(path: Path, class_name: str, line: int) -> ast.ClassDef | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (SyntaxError, OSError):
        return None
    candidates = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == class_name
    ]
    exact = [node for node in candidates if node.lineno == line]
    if exact:
        return exact[0]
    return candidates[0] if candidates else None

def snippet(path: Path, start: int, end: int) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    lo = max(1, start)
    hi = min(len(lines), max(end, start + 10))
    return "\\n".join(f"{idx}: {lines[idx - 1]}" for idx in range(lo, hi + 1))

def audit_record(record: ClassRecord) -> dict[str, object]:
    node = find_class_node(record.abs_path, record.class_name, record.line)
    if node is None:
        return {
            "package": record.package,
            "version": record.version,
            "file_path": record.file_path,
            "class_name": record.class_name,
            "line_start": record.line,
            "line_end": record.end_line,
            "read_shaped_methods_or_properties": False,
            "read_shaped_methods_mutate_state": False,
            "observation_like_methods_mutate_state": False,
            "mutated_state_consumed_by_later_reads": False,
            "composition_or_threshold_visible": False,
            "audit_label": "uncertain",
            "evidence_note": "Could not parse or locate class node for audit.",
            "code_snippet_or_lines": "",
        }

    methods = [child for child in node.body if isinstance(child, ast.FunctionDef)]
    read_methods = [method for method in methods if is_read_shaped(method)]
    obs_methods = [method for method in methods if is_observation_shaped(method)]
    read_mutators = [method for method in read_methods if assigned_self_fields(method)]
    obs_mutators = [method for method in obs_methods if assigned_self_fields(method)]
    mutated = set().union(*(assigned_self_fields(method) for method in read_mutators + obs_mutators)) if (read_mutators or obs_mutators) else set()
    returned_by_reads = set().union(*(return_reads(method) for method in read_methods)) if read_methods else set()
    consumed = bool(mutated & returned_by_reads)
    composition = has_composition_or_threshold(node)
    dynamic = has_dynamic_state_access(node)

    concrete_read_loop = any(
        method_has_return_value(method) and (assigned_self_fields(method) & return_reads(method) or return_reads(method))
        for method in read_mutators
    )
    concrete_obs_loop = bool(obs_mutators and consumed)

    if concrete_read_loop or concrete_obs_loop:
        label = "likely_missed_match"
        note = "Concrete static evidence: read/observation-shaped method mutates self state and a read-shaped return consumes self state."
    elif dynamic or any(method.name in {"__getattr__", "__getattribute__"} for method in methods):
        label = "uncertain"
        note = "Dynamic attribute access or generic attribute hook prevents a confident static nonmatch label."
    elif read_methods or obs_methods:
        label = "likely_nonmatch"
        note = "Read/observation-shaped methods were present, but no concrete OSDS-like mutate-then-consume loop was found."
    else:
        label = "likely_nonmatch"
        note = "No read-shaped or observation-shaped method/property was found in this sampled class."

    method_bits = []
    for method in read_mutators[:3]:
        method_bits.append(f"{method.name} mutates {sorted(assigned_self_fields(method))} at line {method.lineno}")
    for method in obs_mutators[:3]:
        method_bits.append(f"{method.name} mutates {sorted(assigned_self_fields(method))} at line {method.lineno}")
    if method_bits:
        note += " " + "; ".join(method_bits)

    return {
        "package": record.package,
        "version": record.version,
        "file_path": record.file_path,
        "class_name": record.class_name,
        "line_start": record.line,
        "line_end": getattr(node, "end_lineno", record.end_line),
        "read_shaped_methods_or_properties": bool(read_methods),
        "read_shaped_methods_mutate_state": bool(read_mutators),
        "observation_like_methods_mutate_state": bool(obs_mutators),
        "mutated_state_consumed_by_later_reads": consumed,
        "composition_or_threshold_visible": composition,
        "audit_label": label,
        "evidence_note": note,
        "code_snippet_or_lines": snippet(record.abs_path, record.line, min(getattr(node, "end_lineno", record.line), record.line + 10)),
    }

def flagged_keys() -> set[tuple[str, str, str]]:
    rows = read_csv(FINDINGS_CSV)
    return {(row["package"], row["file_path"], row["name"]) for row in rows}

def reviewed_counts() -> tuple[int, int, int]:
    rows = read_csv(FINDINGS_CSV)
    counts = Counter(row["manual_review"] for row in rows)
    return (
        counts["likely true positive"],
        counts["likely false positive"],
        len(rows),
    )

def static_summary_counts() -> tuple[int, int, int]:
    rows = [row for row in read_csv(SUMMARY_CSV) if row["status"] == "analyzed"]
    total = sum(int(row["classes_scanned"]) for row in rows)
    flagged = sum(int(row["MEDIUM"]) + int(row["HIGH"]) for row in rows)
    return total, flagged, total - flagged

def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def run() -> dict[str, object]:
    OUT_DIR.mkdir(exist_ok=True)
    classes = collect_classes()
    flagged = flagged_keys()
    total_from_summary, flagged_from_summary, unflagged_from_summary = static_summary_counts()
    unflagged = [
        record
        for record in classes
        if (record.package, record.file_path, record.class_name) not in flagged
    ]
    if not unflagged:
        return run_fallback_missing_source(
            total_from_summary,
            flagged_from_summary,
            unflagged_from_summary,
        )
    unflagged_sorted = sorted(unflagged, key=lambda record: record.key)
    rng = random.Random(SEED)
    sample_n = min(TARGET_SAMPLE, len(unflagged_sorted))
    sample = rng.sample(unflagged_sorted, sample_n) if sample_n < len(unflagged_sorted) else unflagged_sorted
    sample = sorted(sample, key=lambda record: record.key)
    audit_rows = [audit_record(record) for record in sample]
    write_csv(
        SAMPLE_CSV,
        audit_rows,
        [
            "package",
            "version",
            "file_path",
            "class_name",
            "line_start",
            "line_end",
            "read_shaped_methods_or_properties",
            "read_shaped_methods_mutate_state",
            "observation_like_methods_mutate_state",
            "mutated_state_consumed_by_later_reads",
            "composition_or_threshold_visible",
            "audit_label",
            "evidence_note",
            "code_snippet_or_lines",
        ],
    )

    label_counts = Counter(str(row["audit_label"]) for row in audit_rows)
    tp, fp, reviewed = reviewed_counts()
    likely_missed = label_counts["likely_missed_match"]
    estimated_fn = Fraction(likely_missed * len(unflagged), sample_n) if sample_n else Fraction(0)
    recall_hat = Fraction(tp, 1) / (Fraction(tp, 1) + estimated_fn) if tp or estimated_fn else Fraction(0)
    upper_miss_rate = Fraction(3, sample_n) if sample_n else Fraction(0)
    upper_fn = upper_miss_rate * len(unflagged)
    lower_recall_rule3 = Fraction(tp, 1) / (Fraction(tp, 1) + upper_fn) if tp or upper_fn else Fraction(0)

    summary_row = {
        "total_corpus_classes": len(classes),
        "flagged_classes_or_findings": len(flagged),
        "reviewed_flagged_findings": reviewed,
        "likely_flagged_matches": tp,
        "likely_flagged_false_positives": fp,
        "unflagged_classes": len(unflagged),
        "sampled_unflagged_classes": sample_n,
        "likely_missed_matches": likely_missed,
        "likely_nonmatches": label_counts["likely_nonmatch"],
        "uncertain_cases": label_counts["uncertain"],
        "estimated_false_negatives_from_likely_missed": fraction_text(estimated_fn),
        "estimated_recall_from_likely_missed": fraction_text(recall_hat),
        "estimated_recall_float": f"{float(recall_hat):.6f}",
        "rule_of_three_upper_miss_rate": fraction_text(upper_miss_rate),
        "rule_of_three_upper_false_negatives": fraction_text(upper_fn),
        "rule_of_three_lower_recall": fraction_text(lower_recall_rule3),
        "rule_of_three_lower_recall_float": f"{float(lower_recall_rule3):.6f}",
        "seed": SEED,
        "claim_type": "sampled audit",
    }
    write_csv(SUMMARY_CSV_OUT, [summary_row], list(summary_row))
    write_report(summary_row, audit_rows)
    return summary_row

def fallback_queue_rows() -> list[dict[str, object]]:
    if not FALLBACK_QUEUE.exists():
        return []
    rows = [row for row in read_csv(FALLBACK_QUEUE) if row["analyzer_label"] in {"SAFE", "LOW"}]
    rng = random.Random(SEED)
    sample_n = min(TARGET_SAMPLE, len(rows))
    sample = rng.sample(rows, sample_n) if sample_n < len(rows) else rows
    sample = sorted(sample, key=lambda row: (row["package"], row["file"], row["class"], row["review_id"]))
    out = []
    for row in sample:
        out.append(
            {
                "package": row["package"],
                "version": row["version"],
                "file_path": row["file"],
                "class_name": row["class"],
                "line_start": "",
                "line_end": "",
                "read_shaped_methods_or_properties": "",
                "read_shaped_methods_mutate_state": "",
                "observation_like_methods_mutate_state": "",
                "mutated_state_consumed_by_later_reads": "",
                "composition_or_threshold_visible": "",
                "audit_label": "uncertain",
                "evidence_note": (
                    "Reviewed-corpus source files are missing from the repo/cache. "
                    "This fallback row comes from the expanded SAFE manual-review queue; "
                    "the stored excerpt is insufficient to prove an OSDS miss or nonmatch."
                ),
                "code_snippet_or_lines": row["code_excerpt"],
            }
        )
    return out

def run_fallback_missing_source(
    total_classes: int,
    flagged_classes: int,
    unflagged_classes: int,
) -> dict[str, object]:
    audit_rows = fallback_queue_rows()
    write_csv(
        SAMPLE_CSV,
        audit_rows,
        [
            "package",
            "version",
            "file_path",
            "class_name",
            "line_start",
            "line_end",
            "read_shaped_methods_or_properties",
            "read_shaped_methods_mutate_state",
            "observation_like_methods_mutate_state",
            "mutated_state_consumed_by_later_reads",
            "composition_or_threshold_visible",
            "audit_label",
            "evidence_note",
            "code_snippet_or_lines",
        ],
    )
    tp, fp, reviewed = reviewed_counts()
    summary_row = {
        "total_corpus_classes": total_classes,
        "flagged_classes_or_findings": flagged_classes,
        "reviewed_flagged_findings": reviewed,
        "likely_flagged_matches": tp,
        "likely_flagged_false_positives": fp,
        "unflagged_classes": unflagged_classes,
        "sampled_unflagged_classes": len(audit_rows),
        "likely_missed_matches": 0,
        "likely_nonmatches": 0,
        "uncertain_cases": len(audit_rows),
        "estimated_false_negatives_from_likely_missed": "not_computed_missing_reviewed_source",
        "estimated_recall_from_likely_missed": "not_computed_missing_reviewed_source",
        "estimated_recall_float": "",
        "rule_of_three_upper_miss_rate": "not_computed_missing_reviewed_source",
        "rule_of_three_upper_false_negatives": "not_computed_missing_reviewed_source",
        "rule_of_three_lower_recall": "not_computed_missing_reviewed_source",
        "rule_of_three_lower_recall_float": "",
        "seed": SEED,
        "claim_type": "missing-data audit fallback",
    }
    write_csv(SUMMARY_CSV_OUT, [summary_row], list(summary_row))
    write_report(summary_row, audit_rows)
    return summary_row

def write_report(summary: dict[str, object], audit_rows: list[dict[str, object]]) -> None:
    interesting = [row for row in audit_rows if row["audit_label"] in {"likely_missed_match", "uncertain"}]
    recall_cell = str(summary["estimated_recall_from_likely_missed"])
    if summary.get("estimated_recall_float"):
        recall_cell = f"{recall_cell} ({summary['estimated_recall_float']})"
    lower_recall = str(summary["rule_of_three_lower_recall"])
    if summary.get("rule_of_three_lower_recall_float"):
        lower_recall = f"{lower_recall} ({summary['rule_of_three_lower_recall_float']})"
    lines = [
        "# Unflagged Recall Audit",
        "",
        f"Claim type: {summary['claim_type']}. This is not a proof of analyzer recall, soundness, or completeness.",
        "",
        "## Summary",
        "",
        "| Corpus classes | Flagged reviewed | Likely flagged matches | Unflagged classes | Unflagged sample | Likely missed matches | Uncertain | Estimated recall |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        f"| {summary['total_corpus_classes']} | {summary['reviewed_flagged_findings']} | {summary['likely_flagged_matches']} | {summary['unflagged_classes']} | {summary['sampled_unflagged_classes']} | {summary['likely_missed_matches']} | {summary['uncertain_cases']} | {recall_cell} |",
        "",
        "Estimated recall treats only `likely_missed_match` rows as misses when reviewed-corpus source is available:",
        "",
        "`recall_hat = TP / (TP + estimated_FN)`.",
        "",
        f"Here, estimated_FN = {summary['estimated_false_negatives_from_likely_missed']} and TP = {summary['likely_flagged_matches']}. A rule-of-three uncertainty check gives upper miss rate {summary['rule_of_three_upper_miss_rate']} and lower recall {lower_recall}. Uncertain rows are not counted as misses, so this estimate should be presented cautiously.",
        "",
        "## Likely Missed Or Uncertain Cases",
        "",
        "| package | class | file | lines | audit_label | evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    if interesting:
        for row in interesting:
            evidence = str(row["evidence_note"]).replace("|", "\\|")
            lines.append(
                f"| {row['package']} | {row['class_name']} | {row['file_path']} | "
                f"{row['line_start']}-{row['line_end']} | {row['audit_label']} | {evidence} |"
            )
    else:
        lines.append("| none | none | none | none | none | No likely missed or uncertain cases in sampled rows. |")

    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- The sample is deterministic but not a new random draw from all of PyPI.",
            "- Static inspection can miss dynamic behavior.",
            "- `uncertain` is intentionally not converted into a false-negative count.",
            "- A class is labeled `likely_missed_match` only when the sampled source shows a read-shaped or observation-shaped state mutation whose state is consumed by a later read-shaped return.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main() -> int:
    summary = run()
    print(f"wrote {SAMPLE_CSV}")
    print(f"wrote {SUMMARY_CSV_OUT}")
    print(f"wrote {REPORT_MD}")
    print(
        "sampled={sampled_unflagged_classes} likely_missed={likely_missed_matches} "
        "uncertain={uncertain_cases}".format(**summary)
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
