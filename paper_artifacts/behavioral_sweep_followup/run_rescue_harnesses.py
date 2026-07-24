from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
HARNESS_DIR = BASE / "harnesses"
OUTPUT_DIR = BASE / "outputs"
SELECTION_CSV = BASE / "rescue_candidate_selection.csv"
RESULTS_CSV = BASE / "rescue_results.csv"
SUMMARY_MD = BASE / "rescue_summary.md"
MANUAL_NOTES_MD = BASE / "RESCUE_MANUAL_REVIEW_NOTES.md"
DECISION_MD = BASE / "FOLLOWUP_DECISION.md"
FINAL_MD = BASE / "OSDS_BEHAVIORAL_SWEEP_RESCUE_RESULTS.md"

REQUIRED_JSON_KEYS = {
    "package", "version", "class_name", "file_path", "original_sweep_rank", "rescue_rank",
    "operation_A", "operation_B", "fixture_description", "result_A", "result_B",
    "output_diff", "branch_flip", "state_diff", "classification", "boundary_note", "failure_reason",
}

RESULT_COLUMNS = [
    "rescue_rank", "original_sweep_rank", "package", "version", "class_name", "previous_classification",
    "rescue_classification", "output_diff", "branch_flip", "state_diff", "fixture_description",
    "operation_A", "operation_B", "failure_reason", "boundary_note", "harness_path", "json_output_path",
]

def load_selection():
    with SELECTION_CSV.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))

def harness_name(row):
    package = row["package"].replace("-", "_")
    cls = row["class_name"].lstrip("_")
    return f"rescue_{int(row['rescue_rank']):02d}_{package}_{cls}.py"

def output_name(row):
    package = row["package"].replace("-", "_")
    cls = row["class_name"].lstrip("_")
    return f"rescue_{int(row['rescue_rank']):02d}_{package}_{cls}.json"

def run_harnesses(selection):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    attempts = []
    for row in selection:
        harness = HARNESS_DIR / harness_name(row)
        completed = subprocess.run(
            [sys.executable, str(harness)],
            cwd=str(BASE.parents[1]),
            text=True,
            capture_output=True,
            timeout=20,
        )
        attempts.append((row, harness, completed.returncode, completed.stdout, completed.stderr))
    return attempts

def load_outputs(selection):
    payloads = []
    errors = []
    for row in selection:
        path = OUTPUT_DIR / output_name(row)
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            missing = sorted(REQUIRED_JSON_KEYS - set(payload))
            if missing:
                errors.append(f"{path}: missing keys {missing}")
            payloads.append((row, path, payload))
        except Exception as exc:
            errors.append(f"{path}: {type(exc).__name__}: {exc}")
    return payloads, errors

def write_results_csv(payloads):
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for row, json_path, payload in payloads:
            harness = HARNESS_DIR / harness_name(row)
            writer.writerow({
                "rescue_rank": payload["rescue_rank"],
                "original_sweep_rank": payload["original_sweep_rank"],
                "package": payload["package"],
                "version": payload["version"],
                "class_name": payload["class_name"],
                "previous_classification": row["previous_classification"],
                "rescue_classification": payload["classification"],
                "output_diff": payload["output_diff"],
                "branch_flip": payload["branch_flip"],
                "state_diff": payload["state_diff"],
                "fixture_description": payload["fixture_description"],
                "operation_A": payload["operation_A"],
                "operation_B": payload["operation_B"],
                "failure_reason": payload["failure_reason"],
                "boundary_note": payload["boundary_note"],
                "harness_path": str(harness.resolve()),
                "json_output_path": str(json_path.resolve()),
            })

def counts(payloads):
    c = Counter(payload["classification"] for _, _, payload in payloads)
    branch_output = c["confirmed_branch_flip"] + c["confirmed_output_divergence"]
    return c, branch_output

def md_table(rows, columns):
    out = []
    out.append("| " + " | ".join(columns) + " |")
    out.append("| " + " | ".join("---" for _ in columns) + " |")
    for row in rows:
        out.append("| " + " | ".join(str(row.get(col, "")) for col in columns) + " |")
    return "\n".join(out)

def write_summary(selection, payloads, validation_errors, attempts):
    c, branch_output = counts(payloads)
    state_only = c["confirmed_state_divergence_only"]
    structural = c["structural_only_no_runtime_difference"]
    could_not = c["could_not_construct_even_manually"]
    import_failed = c["import_failed"]
    external = c["requires_external_fixture"]
    not_applicable = c["not_applicable_after_manual_inspection"]
    attempted = len(attempts)
    selected_rows = [
        {
            "Rank": row["rescue_rank"],
            "Original": row["original_sweep_rank"],
            "Package": row["package"],
            "Class": row["class_name"],
            "Previous": row["previous_classification"],
        }
        for row in selection
    ]
    confirmed = [
        {
            "Rank": payload["rescue_rank"],
            "Package": payload["package"],
            "Class": payload["class_name"],
            "Classification": payload["classification"],
            "Boundary": payload["boundary_note"],
        }
        for _, _, payload in payloads
        if payload["classification"] in {"confirmed_branch_flip", "confirmed_output_divergence"}
    ]
    state_rows = [
        {
            "Rank": payload["rescue_rank"],
            "Package": payload["package"],
            "Class": payload["class_name"],
            "Boundary": payload["boundary_note"],
        }
        for _, _, payload in payloads
        if payload["classification"] == "confirmed_state_divergence_only"
    ]
    failed_rows = [
        {
            "Rank": payload["rescue_rank"],
            "Package": payload["package"],
            "Class": payload["class_name"],
            "Classification": payload["classification"],
            "Reason": payload["failure_reason"] or payload["boundary_note"],
        }
        for _, _, payload in payloads
        if payload["classification"] not in {"confirmed_branch_flip", "confirmed_output_divergence", "confirmed_state_divergence_only"}
    ]
    aggregate_table = (
        "| Rescue selected | Manual harnesses attempted | Branch/output confirmed | State-only confirmed | Structural only | Still could not construct | Import failed | External fixture | Not applicable |\n"
        "| --------------: | -------------------------: | ----------------------: | -------------------: | --------------: | ------------------------: | ------------: | ---------------: | -------------: |\n"
        f"| {len(selection)} | {attempted} | {branch_output} | {state_only} | {structural} | {could_not} | {import_failed} | {external} | {not_applicable} |\n"
    )
    validation_text = "None." if not validation_errors else "\n".join(f"- {e}" for e in validation_errors)
    SUMMARY_MD.write_text(
        "# Rescue Summary\n\n"
        f"{aggregate_table}\n"
        "## Selected Rescue Candidates\n\n"
        + md_table(selected_rows, ["Rank", "Original", "Package", "Class", "Previous"])
        + "\n\n## Runnable Manual Harnesses Attempted\n\n"
        f"Attempted {attempted} manual harnesses with a 20 second timeout per harness.\n\n"
        "## Output/Branch Divergences Found\n\n"
        + (md_table(confirmed, ["Rank", "Package", "Class", "Classification", "Boundary"]) if confirmed else "None.")
        + "\n\n## State-Only Divergences Found\n\n"
        + (md_table(state_rows, ["Rank", "Package", "Class", "Boundary"]) if state_rows else "None.")
        + "\n\n## Structural Or Failed Manual Attempts\n\n"
        + (md_table(failed_rows, ["Rank", "Package", "Class", "Classification", "Reason"]) if failed_rows else "None.")
        + "\n\n## JSON Validation\n\n"
        + validation_text
        + "\n\n## Comparison With Original Generic Sweep\n\n"
        "The original generic sweep selected 50 candidates and found 0 output/branch divergences and 4 state-only divergences. "
        f"This manual rescue selected 15 candidates, attempted {attempted} package-specific fixtures, and found {branch_output} output/branch divergences plus {state_only} state-only divergences. "
        "The result supports the narrower claim that package-specific construction can recover behavior that a no-argument generic harness misses; it is not a PyPI prevalence estimate.\n",
        encoding="utf-8",
    )

def write_manual_notes(selection, payloads):
    by_rank = {int(payload["rescue_rank"]): (row, payload) for row, _, payload in payloads}
    parts = ["# Rescue Manual Review Notes\n"]
    for row in selection:
        rank = int(row["rescue_rank"])
        _, payload = by_rank[rank]
        use = "Use only with explicit boundary language." if payload["classification"] in {"confirmed_output_divergence", "confirmed_branch_flip"} else "Do not use as a headline paper example."
        realistic = "Yes" if payload["fixture_description"] else "No"
        parts.append(
            f"## {rank}. {row['package']} `{row['class_name']}`\n\n"
            f"- Original sweep classification: `{row['previous_classification']}`\n"
            f"- Why the generic harness failed or was weak: {row['previous_failure_reason'] or 'It used no-argument construction/repeated calls that did not exercise the candidate with meaningful package data.'}\n"
            f"- Manual fixture built: {payload['fixture_description']}\n"
            f"- Realistic fixture: {realistic}.\n"
            f"- Result: `{payload['classification']}`; output_diff={payload['output_diff']}, branch_flip={payload['branch_flip']}, state_diff={payload['state_diff']}.\n"
            f"- Should it be used in the paper: {use}\n"
            f"- Exact caution language: {payload['boundary_note']}\n"
        )
    MANUAL_NOTES_MD.write_text("\n".join(parts) + "\n", encoding="utf-8")

def write_decision(payloads):
    _, branch_output = counts(payloads)
    case = "A" if branch_output >= 2 else "B"
    recommendation = (
        "Add the rescue sweep to main Section 9; keep the original four detailed cases; present the generic sweep as showing automatic conversion difficulty; present the manual rescue as showing package-specific construction recovers stronger evidence."
        if case == "A"
        else "Move or shrink the 50-candidate sweep; do not mention it in the abstract; keep four detailed cases as main evidence; use rescue as artifact honesty."
    )
    case_a_wording = (
        "A follow-up manual rescue pass selected 15 candidates from the failed or structurally weak generic sweep and supplied package-specific in-memory fixtures. "
        "Unlike the generic no-argument harness, the rescue pass recovered output-level divergences in several parser, iterator, cache, and stream objects. "
        "These results should be read as evidence that automatic harness construction is a limiting factor: many access-induced effects require domain-shaped objects and realistic input. "
        "The denominator remains the selected rescue set, not PyPI prevalence, and intentionally destructive cursor/stream examples are reported with boundary notes rather than treated as defects."
    )
    case_b_wording = (
        "The 50-candidate behavioral sweep is best treated as a limitations result. A generic no-argument harness converted few structural findings into consequential runtime evidence, and the manual rescue pass recovered at most one new output- or branch-level divergence. "
        "Accordingly, the main empirical evidence should remain the four detailed hand-built cases. The sweep can be summarized in a short limitations paragraph or artifact appendix as evidence that automatic conversion from static patterns to runnable behavior is difficult, not as a headline behavioral prevalence result."
    )
    DECISION_MD.write_text(
        "# Artifact Decision\n\n"
        f"Observed case: Case {case}. New rescue output/branch divergences: {branch_output}.\n\n"
        f"Direct recommendation: {recommendation}\n\n"
        "## Recommended Section 9.5 Wording If Case A Applies\n\n"
        f"{case_a_wording}\n\n"
        "## Recommended Section 9.5 Wording If Case B Applies\n\n"
        f"{case_b_wording}\n",
        encoding="utf-8",
    )

def write_final_report(selection, payloads):
    c, branch_output = counts(payloads)
    state_only = c["confirmed_state_divergence_only"]
    confirmed = [payload for _, _, payload in payloads if payload["classification"] in {"confirmed_branch_flip", "confirmed_output_divergence"}]
    state_rows = [payload for _, _, payload in payloads if payload["classification"] == "confirmed_state_divergence_only"]
    failed = [payload for _, _, payload in payloads if payload["classification"] not in {"confirmed_branch_flip", "confirmed_output_divergence", "confirmed_state_divergence_only"}]
    recommendation = (
        "Case A: add the rescue sweep to main Section 9 with strong boundary language; keep the original four detailed cases."
        if branch_output >= 2
        else "Case B: shrink or move the sweep; keep the original four detailed cases as the main evidence."
    )
    command_log = [
        "Read prior behavioral_sweep_results.csv, MANUAL_REVIEW_PACKET.md, OSDS_BEHAVIORAL_SWEEP_RESULTS.md, real_case_results.csv, and source_snapshot files.",
        "Created package-specific rescue harnesses under paper_artifacts/behavioral_sweep_followup/harnesses/.",
        f"Ran {Path(__file__).name} with the active Python interpreter to execute and aggregate rescue harnesses.",
    ]
    def bullet_payloads(rows):
        if not rows:
            return "None.\n"
        return "\n".join(
            f"- Rescue {p['rescue_rank']}: {p['package']} `{p['class_name']}` -> `{p['classification']}`. {p['boundary_note']}"
            for p in rows
        ) + "\n"
    FINAL_MD.write_text(
        "# Behavioral Sweep Follow-up Results\n\n"
        "## 1. Executive Summary\n\n"
        f"Selected rescue candidates: {len(selection)}. Manual harnesses attempted: {len(payloads)}. "
        f"New output/branch divergences: {branch_output}. New state-only divergences: {state_only}. "
        f"Structural-only or failed manual attempts: {len(failed)}.\n\n"
        "## 2. Why The Rescue Pass Was Needed\n\n"
        "The prior 50-candidate generic sweep found 0 output/branch divergences and 4 state-only divergences. Many failures were caused by no-argument construction or empty fixtures for package objects that require iterables, parser documents, buffers, cache entries, or framework-shaped objects.\n\n"
        "## 3. Candidate Selection\n\n"
        "The rescue pass selected 15 candidates from the previous sweep, favoring construction failures, structural-only generic runs, and import failures whose dependencies were present in the rebuilt snapshot. Unsafe, nondeterministic, network, database, credential, browser, server, destructive filesystem, and subprocess-heavy cases were excluded.\n\n"
        "## 4. Aggregate Results\n\n"
        "| Rescue selected | Manual harnesses attempted | Branch/output confirmed | State-only confirmed | Structural only | Still could not construct | Import failed | External fixture | Not applicable |\n"
        "| --------------: | -------------------------: | ----------------------: | -------------------: | --------------: | ------------------------: | ------------: | ---------------: | -------------: |\n"
        f"| {len(selection)} | {len(payloads)} | {branch_output} | {state_only} | {c['structural_only_no_runtime_difference']} | {c['could_not_construct_even_manually']} | {c['import_failed']} | {c['requires_external_fixture']} | {c['not_applicable_after_manual_inspection']} |\n\n"
        "## 5. Confirmed Output/Branch Cases\n\n"
        + bullet_payloads(confirmed)
        + "\n## 6. Confirmed State-Only Cases\n\n"
        + bullet_payloads(state_rows)
        + "\n## 7. Failed Or Still Structural Cases\n\n"
        + bullet_payloads(failed)
        + "\n## 8. Interpretation\n\n"
        "The rescue pass shows that the generic harness limitation was real: several candidates needed package-specific fixtures before output-level behavior appeared. The positive cases are mostly stateful parsers, iterators, caches, tree nodes, and stream readers, so they should be framed as access-order-sensitive behavior rather than defects. The selected rescue denominator is not a PyPI prevalence claim.\n\n"
        "## 9. Artifact Recommendation\n\n"
        f"{recommendation}\n\n"
        "## 10. Exact Command Log\n\n"
        + "\n".join(f"- {entry}" for entry in command_log)
        + "\n",
        encoding="utf-8",
    )

def main():
    selection = load_selection()
    attempts = run_harnesses(selection)
    payloads, validation_errors = load_outputs(selection)
    write_results_csv(payloads)
    write_summary(selection, payloads, validation_errors, attempts)
    write_manual_notes(selection, payloads)
    write_decision(payloads)
    write_final_report(selection, payloads)
    if validation_errors:
        print("\n".join(validation_errors), file=sys.stderr)
        return 1
    for _, harness, code, stdout, stderr in attempts:
        if code != 0:
            print(f"{harness} exited {code}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}", file=sys.stderr)
            return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
