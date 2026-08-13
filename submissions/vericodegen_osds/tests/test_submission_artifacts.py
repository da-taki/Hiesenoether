import csv
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "submissions" / "vericodegen_osds"


def test_prospective_compliance_counts():
    rows = list(csv.DictReader((ROOT / "analysis/prospective_task_compliance.csv").open(encoding="utf-8")))
    assert len(rows) == 42
    assert sum(r["task_compliance"] == "compliant_transformation" for r in rows) == 23
    assert sum(r["task_compliance"] == "unchanged_output" for r in rows) == 19
    assert sum(r["task_compliance"] in {"partial_or_noncompliant", "invalid"} for r in rows) == 0
    assert sum(r["osds_preservation"] == "verified_divergence" for r in rows) == 0


def test_submission_packages_have_required_files():
    with zipfile.ZipFile(OUT / "vericodegen_osds_source_package.zip") as archive:
        names = set(archive.namelist())
    assert "latex/neurips_2026_vericode_workshop.tex" in names
    assert "latex/neurips_2026_vericode.sty" in names
    assert "latex/references.bib" in names
    with zipfile.ZipFile(OUT / "vericodegen_osds_supplement.zip") as archive:
        names = set(archive.namelist())
    assert "REPRODUCE.md" in names
    assert "ARTIFACT_INDEX.md" in names
    assert "analysis/prospective_task_compliance.csv" in names
    assert "SUPPLEMENT_DEPENDENCY_AUDIT.md" in names
    assert "experiments/agent_behavior_preservation/agent_bp/cases.py" in names
    assert "paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py" in names


def test_anonymity_scan_submission_tree():
    banned = ["Tak" + "noor", "Ta" + "ki", "da-" + "ta" + "ki", "singh" + "tak" + "noor", "As" + "us", "@gmail" + ".com", "@s" + "fu.ca", "C:" + "\\" + "Users"]
    roots = [OUT / "latex", OUT / "supplement", OUT / "SUBMISSION_COMPLIANCE.md"]
    offenders = []
    for root in roots:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() not in {".pdf", ".zip"}]
        for path in files:
            text = path.read_text(encoding="utf-8", errors="ignore")
            for needle in banned:
                if needle in text:
                    offenders.append((str(path.relative_to(ROOT)), needle))
    assert not offenders
