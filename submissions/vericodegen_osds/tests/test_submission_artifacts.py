import csv
import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "submissions" / "vericodegen_osds"
OFFICIAL_STYLE_SHA256 = "2944ec0d4f64dba353827e9ead104da1a9ac81b4057f4ff40969c693632a1e11"


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
    assert "LICENSES.md" in names
    assert "analysis/prospective_task_compliance.csv" in names
    assert "SUPPLEMENT_DEPENDENCY_AUDIT.md" in names
    assert "experiments/agent_behavior_preservation/agent_bp/cases.py" in names
    assert "paper_artifacts/scp_realcode_metamorphic_oracle/metamorphic_fixtures.py" in names


def test_official_style_is_pristine_and_packaged():
    style = OUT / "latex" / "neurips_2026_vericode.sty"
    digest = hashlib.sha256(style.read_bytes()).hexdigest()
    assert digest == OFFICIAL_STYLE_SHA256
    with zipfile.ZipFile(OUT / "vericodegen_osds_source_package.zip") as archive:
        packaged_digest = hashlib.sha256(archive.read("latex/neurips_2026_vericode.sty")).hexdigest()
    assert packaged_digest == OFFICIAL_STYLE_SHA256


def test_no_unresolved_checklist_placeholders_in_authored_sources():
    needles = ["answerTODO", "justificationTODO"]
    roots = [OUT / "latex", OUT / "supplement", OUT / "SUBMISSION_COMPLIANCE.md"]
    offenders = []
    for root in roots:
        files = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() not in {".pdf", ".zip"}]
        for path in files:
            if path.name == "neurips_2026_vericode.sty":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for needle in needles:
                if needle in text:
                    offenders.append(str(path.relative_to(ROOT)))
    assert not offenders


def test_supplement_license_entries_are_explicit():
    licenses = (OUT / "supplement" / "LICENSES.md").read_text(encoding="utf-8")
    for name in [
        "httpcore",
        "PyYAML",
        "pytest",
        "Python-Markdown",
        "more-itertools",
        "docutils",
        "beautifulsoup4",
        "boltons",
        "Cerberus",
        "dnspython",
        "h11",
        "anyio",
        "Codex task-model responses",
        "VeriCodeGen workshop style",
    ]:
        assert name in licenses
    assert "unresolved" not in licenses.lower()


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
