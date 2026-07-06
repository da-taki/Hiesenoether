from __future__ import annotations

import ast
import csv
import json
import re
import textwrap
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FINDINGS = REPO / "results_static" / "pypi_static_benchmark_findings.csv"
SUMMARY = REPO / "results_static" / "pypi_static_benchmark.csv"
MANIFEST = REPO / "paper_artifacts" / "scp_realworld_revision" / "source_snapshot_manifest.csv"
PREVIOUS_RESULTS = REPO / "paper_artifacts" / "scp_realworld_revision" / "real_case_results.csv"
CANDIDATES = OUT / "behavioral_sweep_candidates.csv"
RULE_MD = OUT / "CANDIDATE_SELECTION_RULE.md"
HARNESS_DIR = OUT / "harnesses"
NOTES_DIR = OUT / "harness_notes"
OUTPUT_DIR = OUT / "outputs"
PACKET = OUT / "MANUAL_REVIEW_PACKET.md"
INTEGRATION = OUT / "MANUSCRIPT_INTEGRATION_NOTES.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def norm_path(text: str) -> str:
    return text.replace("\\", "/")


def source_manifest() -> dict[str, dict[str, str]]:
    return {row["package"]: row for row in read_csv(MANIFEST)}


def path_parts(text: str) -> list[str]:
    return [part for part in norm_path(text).split("/") if part]


def find_source_file(root: Path, finding_path: str) -> Path | None:
    wanted = path_parts(finding_path)
    files = list(root.rglob("*.py"))
    for path in files:
        parts = path_parts(str(path.relative_to(root)))
        if wanted[-len(parts):] == parts:
            return path
    for path in files:
        parts = path_parts(str(path.relative_to(root)))
        if len(wanted) >= 2 and len(parts) >= 2 and wanted[-2:] == parts[-2:]:
            return path
    for path in files:
        if path.name == wanted[-1]:
            return path
    return None


def parse_class(path: Path, class_name: str, line: int) -> ast.ClassDef | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return None
    candidates = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name == class_name]
    for node in candidates:
        if node.lineno == line:
            return node
    return candidates[0] if candidates else None


def method_from_reason(reason: str) -> str:
    match = re.search(r"method ([^(]+)\(\)", reason)
    return match.group(1) if match else ""


def mutated_state(reason: str) -> str:
    match = re.search(r"mutates self\.\{([^}]*)\}", reason)
    return match.group(1) if match else ""


def simple_constructor(node: ast.ClassDef | None) -> str:
    if node is None:
        return "unknown"
    for child in node.body:
        if isinstance(child, ast.FunctionDef) and child.name in {"__init__", "__new__"}:
            args = child.args.args[1:]
            defaults = len(child.args.defaults)
            required = len(args) - defaults
            if required <= 0:
                return "simple"
            return "requires_args"
    return "simple"


def abstract_like(node: ast.ClassDef | None, class_name: str) -> bool:
    if node is None:
        return False
    text = class_name.lower()
    if any(bit in text for bit in ("abstract", "protocol", "interface", "base")):
        return True
    for base in node.bases:
        name = getattr(base, "id", "") or getattr(base, "attr", "")
        if name in {"ABC", "Protocol"}:
            return True
    return False


def score(row: dict[str, str], node: ast.ClassDef | None, source_file: Path | None) -> tuple[int, list[str], str, str, str]:
    reason = row["short_reason"]
    mechanisms = row["detected_mechanisms"]
    note = row["manual_review_note"]
    method = method_from_reason(reason)
    state = mutated_state(reason)
    s = 0
    reasons = []
    if row["manual_review"] == "likely true positive":
        s += 4
        reasons.append("+4 likely true positive")
    if row["analyzer_label"] == "HIGH":
        s += 3
        reasons.append("+3 HIGH")
    if re.search(r"read|get|value|property|__getitem__|__next__|__call__|__hash__|open|content", reason, re.I):
        s += 2
        reasons.append("+2 read/getter-like mutation")
    if re.search(r"observe|inspect|repr|str|logging|debug|snapshot|render", reason + " " + note, re.I):
        s += 2
        reasons.append("+2 observer/repr/logging/debug-like mutation")
    if re.search(r"later|composition|threshold|cache|branch|cached|returns|semantic", mechanisms + " " + reason + " " + note, re.I):
        s += 2
        reasons.append("+2 later/cache/branch/composition hint")
    ctor = simple_constructor(node)
    if ctor == "simple":
        s += 1
        reasons.append("+1 simple constructor")
    import_feasibility = "source_file_available" if source_file else "missing_source"
    if source_file:
        s += 1
        reasons.append("+1 source import path available")
    path_lower = row["file_path"].lower()
    if any(part in path_lower for part in ("test", "tests", "docs", "examples", "example")):
        s -= 2
        reasons.append("-2 tests/docs/examples path")
    if abstract_like(node, row["name"]):
        s -= 2
        reasons.append("-2 abstract/protocol/base-like")
    if re.search(r"database|network|socket|server|client|connection|request|django|flask|sql", row["name"] + " " + row["file_path"] + " " + reason, re.I):
        s -= 3
        reasons.append("-3 external service/framework likelihood")
    return s, reasons, ctor, import_feasibility, method or ""


def select_candidates() -> tuple[list[dict[str, object]], dict[str, int]]:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = source_manifest()
    findings = read_csv(FINDINGS)
    likely = [row for row in findings if row["manual_review"] == "likely true positive"]
    scored = []
    source_available = 0
    for row in likely:
        man = manifest.get(row["package"])
        if not man or man["source_status"] == "missing":
            continue
        root = Path(man["source_path"])
        source_file = find_source_file(root, row["file_path"])
        if source_file is None:
            continue
        source_available += 1
        node = parse_class(source_file, row["name"], int(row["line"]))
        s, reasons, ctor, import_feasibility, method = score(row, node, source_file)
        scored.append(
            {
                "package": row["package"],
                "version": row["version"],
                "file_path": row["file_path"],
                "class_name": row["name"],
                "line_start": row["line"],
                "manual_review": row["manual_review"],
                "risk_label": row["analyzer_label"],
                "mechanisms": row["detected_mechanisms"],
                "manual_review_note": row["manual_review_note"],
                "score": s,
                "source_path": str(source_file),
                "source_root": str(root),
                "constructor_feasibility": ctor,
                "import_feasibility": import_feasibility,
                "expected_observer_or_read_operation": method,
                "expected_latent_state": mutated_state(row["short_reason"]),
                "expected_later_behavior": "repeat the same read-shaped operation and compare result/state",
                "selection_reason": "; ".join(reasons),
                "_node": node,
            }
        )
    scored.sort(key=lambda item: (-int(item["score"]), str(item["package"]).lower(), str(item["file_path"]), str(item["class_name"]), int(item["line_start"])))
    selected = scored[:50]
    for idx, item in enumerate(selected, 1):
        item["sweep_rank"] = idx
    counts = {
        "reviewed_findings": len(findings),
        "likely_true_positives": len(likely),
        "source_available_likely_true_positives": source_available,
        "selected": len(selected),
    }
    return selected, counts


def write_candidates(selected: list[dict[str, object]]) -> None:
    cols = [
        "sweep_rank", "package", "version", "file_path", "class_name", "line_start",
        "manual_review", "risk_label", "mechanisms", "manual_review_note", "score",
        "source_path", "constructor_feasibility", "import_feasibility",
        "expected_observer_or_read_operation", "expected_latent_state",
        "expected_later_behavior", "selection_reason",
    ]
    with CANDIDATES.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols)
        writer.writeheader()
        for item in selected:
            writer.writerow({key: item.get(key, "") for key in cols})


def clean_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_")[:80] or "case"


def write_harnesses(selected: list[dict[str, object]]) -> None:
    HARNESS_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    common = "from pathlib import Path\nimport sys\n\nROOT = Path(__file__).resolve().parents[3]\nSWEEP = Path(__file__).resolve().parents[1]\nsys.path.insert(0, str(SWEEP))\nfrom harness_common import write_case\n\n"
    for item in selected:
        rank = int(item["sweep_rank"])
        stem = f"case_{rank:02d}_{clean_name(str(item['package']))}_{clean_name(str(item['class_name']))}"
        harness = HARNESS_DIR / f"{stem}.py"
        out_json = OUTPUT_DIR / f"{stem}.json"
        meta = {key: value for key, value in item.items() if not key.startswith("_")}
        meta["output_json"] = str(out_json)
        harness.write_text(
            common
            + "META = "
            + json.dumps(meta, indent=2)
            + "\n\nif __name__ == '__main__':\n    raise SystemExit(write_case(META, META['output_json']))\n",
            encoding="utf-8",
        )
        note = NOTES_DIR / f"{stem}.md"
        note.write_text(
            "\n".join(
                [
                    f"# Case {rank}: {item['package']} {item['class_name']}",
                    "",
                    f"- Runnable harness: `{harness}`",
                    f"- Expected operation: `{item['expected_observer_or_read_operation']}`",
                    f"- Expected latent state: `{item['expected_latent_state']}`",
                    f"- Construction feasibility: `{item['constructor_feasibility']}`",
                    f"- Selection reason: {item['selection_reason']}",
                    "",
                    "If the generic harness cannot construct or safely call the class, the JSON result records the failure classification and reason.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def source_snippet(path: str, line: int, limit: int = 40) -> str:
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, line - 5)
    end = min(len(lines), start + limit - 1)
    return "\n".join(f"{idx}: {lines[idx - 1]}" for idx in range(start, end + 1))


def write_packet(selected: list[dict[str, object]]) -> None:
    lines = ["# Manual Review Packet", ""]
    for item in selected:
        rank = int(item["sweep_rank"])
        lines.extend(
            [
                f"## {rank}. {item['package']} `{item['class_name']}`",
                "",
                f"- Path: `{item['file_path']}`",
                f"- Score: {item['score']}",
                f"- Selection reason: {item['selection_reason']}",
                f"- Suspected operation: `{item['expected_observer_or_read_operation']}`",
                f"- Suspected latent state: `{item['expected_latent_state']}`",
                f"- Suspected later behavior: {item['expected_later_behavior']}",
                f"- Harness status: generated; see sweep results after runner.",
                "",
                "```python",
                source_snippet(str(item["source_path"]), int(item["line_start"])),
                "```",
                "",
            ]
        )
    PACKET.write_text("\n".join(lines), encoding="utf-8")


def write_rule(counts: dict[str, int], selected: list[dict[str, object]]) -> None:
    previous = set()
    if PREVIOUS_RESULTS.exists():
        for row in read_csv(PREVIOUS_RESULTS):
            previous.add((row["package"].lower(), row["class_name"].lower()))
    selected_prev = [
        f"{item['package']}.{item['class_name']}"
        for item in selected
        if (str(item["package"]).lower(), str(item["class_name"]).lower()) in previous
    ]
    RULE_MD.write_text(
        "\n".join(
            [
                "# Candidate Selection Rule",
                "",
                "Input pool: `results_static/pypi_static_benchmark_findings.csv`, restricted to rows with `manual_review = likely true positive` and an existing source file in the rebuilt exact-version snapshot.",
                "",
                "Scoring:",
                "",
                "- +4 likely true positive",
                "- +3 HIGH risk label",
                "- +2 read/property/getter-like mutation hint",
                "- +2 observer/repr/str/logging/debug/snapshot mutation hint",
                "- +2 later read/composition/threshold/cache/branch hint",
                "- +1 simple/no-required-args constructor inferred from AST",
                "- +1 source import path available",
                "- -2 tests/docs/examples path",
                "- -2 abstract/protocol/base-like class",
                "- -3 likely external service/network/database/framework context",
                "",
                "Tie-breaks: higher score, package name, file path, class name, line number.",
                "",
                f"- reviewed findings: {counts['reviewed_findings']}",
                f"- likely true positives: {counts['likely_true_positives']}",
                f"- likely true positives with source available: {counts['source_available_likely_true_positives']}",
                f"- selected candidates: {counts['selected']}",
                f"- previous four confirmed cases selected by this rule: {', '.join(selected_prev) if selected_prev else 'none'}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_integration_notes() -> None:
    INTEGRATION.write_text(
        """# Manuscript Integration Notes

The sweep is suitable for the main paper only as a high-confidence conversion audit, not a prevalence estimate. Keep the four detailed cases as case studies and use this 50-candidate sweep as supporting systematic evidence.

Recommended Section 9 wording:

\"We additionally ran a deterministic 50-candidate behavioral sweep over high-confidence reviewed analyzer findings. Each selected candidate was assigned a generated harness or an explicit failure classification. The sweep measures conversion from structural finding to runnable behavioral evidence within this selected high-confidence set; it is not an ecosystem prevalence estimate.\"

Recommended table caption:

\"Behavioral harness outcomes for 50 systematically selected high-confidence reviewed PyPI findings. Failures are counted as outcomes; previous hand-confirmed cases are reported separately as controls unless selected by the rule.\"

Do not claim:

- prevalence in all PyPI;
- analyzer completeness;
- that every confirmed behavior is a bug;
- that generic harness failures refute the structural finding.
""",
        encoding="utf-8",
    )


def main() -> int:
    selected, counts = select_candidates()
    write_candidates(selected)
    write_harnesses(selected)
    write_packet(selected)
    write_rule(counts, selected)
    write_integration_notes()
    print(f"wrote {CANDIDATES}")
    print(f"selected={len(selected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
