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

def test_checked_affine_adjacent_swap_assumptions_match_exact_semantics():
    from fractions import Fraction

    from validation.exact_semantics import Params, Value, do_obs, do_read

    p = Params(de_access=Fraction(1, 10), de_obs=Fraction(3, 5))
    x = Value(b=Fraction(10), n=2, e=Fraction(7, 3))

    read_value, after_read = do_read(x, p)
    after_read_obs = do_obs(after_read, p)
    after_obs = do_obs(x, p)
    obs_read_value, after_obs_read = do_read(after_obs, p)

    assert after_read.e == x.e + p.de_access
    assert after_obs.e == x.e + p.de_obs
    assert after_read_obs.e == after_obs_read.e == x.e + p.de_access + p.de_obs
    assert obs_read_value - read_value == Fraction(x.n) * p.de_obs
    assert obs_read_value >= read_value


def test_local_commutation_formulas_match_general_paper_transition():
    from fractions import Fraction

    b = Fraction(10)
    a = 2
    d = Fraction(7, 3)
    y = Fraction(5)
    delta = Fraction(1, 10)
    eta = Fraction(3, 5)

    def r(_, drift):
        return drift + delta

    def g(drift):
        return drift + eta

    def f(base, count, drift):
        return base + count * drift

    read_obs = (b, a + 1, g(r(a, d)), y + f(b, a, d))
    obs_read = (b, a + 1, r(a, g(d)), y + f(b, a, g(d)))

    assert read_obs[2] == obs_read[2]
    assert obs_read[3] - read_obs[3] == Fraction(a) * eta


def test_checked_affine_boundary_orders_match_enumerated_small_cases():
    from itertools import permutations
    from fractions import Fraction

    from validation.exact_semantics import Params, evaluate

    p = Params(de_access=Fraction(1, 10), de_obs=Fraction(3, 5))
    for reads in range(1, 5):
        for observations in range(1, 4):
            bodies = set(permutations(("READ",) * reads + ("OBS",) * observations))
            values = {body: evaluate(body, degree=1, p=p) for body in bodies}
            min_body = ("READ",) * reads + ("OBS",) * observations
            max_body = ("OBS",) * observations + ("READ",) * reads
            assert values[min_body] == min(values.values())
            assert values[max_body] == max(values.values())
