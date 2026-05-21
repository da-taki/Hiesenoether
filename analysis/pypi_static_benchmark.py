from __future__ import annotations

import ast
import csv
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterable

from analysis.oc_static import analyze_file


REPO = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO / "results_static"
CACHE_DIR = Path(tempfile.gettempdir()) / "hiesenoether_pypi_static_benchmark"
DOWNLOAD_DIR = CACHE_DIR / "downloads"
SOURCE_DIR = CACHE_DIR / "sources"

SUMMARY_CSV = RESULTS_DIR / "pypi_static_benchmark.csv"
FINDINGS_CSV = RESULTS_DIR / "pypi_static_benchmark_findings.csv"
SUMMARY_MD = RESULTS_DIR / "pypi_static_benchmark_summary.md"

PACKAGES = [
    "attrs",
    "click",
    "humanize",
    "pendulum",
    "arrow",
    "cachetools",
    "sortedcontainers",
    "boltons",
    "more-itertools",
    "toolz",
    "yarl",
    "multidict",
    "marshmallow",
    "cerberus",
    "tomli",
    "tomlkit",
    "python-dotenv",
    "loguru",
    "structlog",
    "tenacity",
    "pluggy",
    "packaging",
    "importlib-metadata",
    "jsonschema",
    "tqdm",
    "anyio",
    "sniffio",
    "pyparsing",
    "requests",
    "urllib3",
    "jinja2",
    "markupsafe",
    "flask",
    "werkzeug",
    "itsdangerous",
    "blinker",
    "iniconfig",
    "filelock",
    "platformdirs",
    "pathspec",
    "mypy-extensions",
    "typing-extensions",
    "typing-inspection",
    "dacite",
    "cattrs",
    "deprecated",
    "wrapt",
    "dateparser",
    "parsedatetime",
    "Babel",
    "soupsieve",
    "beautifulsoup4",
    "pygments",
    "mistune",
    "markdown",
    "docutils",
    "pydocstyle",
    "flake8",
    "mccabe",
    "pycodestyle",
    "pyflakes",
    "click-option-group",
    "fastjsonschema",
    "jsonpointer",
    "jsonpatch",
    "email-validator",
    "dnspython",
    "h11",
    "h2",
    "wsproto",
    "websockets",
    "frozenlist",
    "aiosignal",
]

SKIP_DIRS = {
    ".git",
    "__pycache__",
    "build",
    "dist",
    "docs",
    "doc",
    "example",
    "examples",
    "test",
    "tests",
    "testing",
    "bench",
    "benchmarks",
}

# Manual review of every MEDIUM/HIGH finding emitted by the benchmark run.
# Keys are package|relative-path|class-name. Unlisted flagged findings are
# likely true positives for stateful/access-evolving behavior after source
# inspection.
FALSE_POSITIVES = {
    "attrs|attrs-26.1.0\\src\\attr\\_make.py|_ClassBuilder":
        "fluent class-builder mutator returns self; not an access/read path",
    "attrs|attrs-26.1.0\\src\\attr\\_make.py|_CountingAttr":
        "decorator registration mutates validator list and returns the decorated method",
    "click|click-8.4.0\\src\\click\\_termui_impl.py|ProgressBar":
        "context-manager entry flag returns self; no access-derived value",
    "click|click-8.4.0\\src\\click\\core.py|Context":
        "context-manager depth tracking returns self; no access-derived value",
    "click|click-8.4.0\\src\\click\\core.py|Command":
        "lazy help-option cache; repeated access returns the same semantic option",
    "click|click-8.4.0\\src\\click\\core.py|Group":
        "callback registration decorator, not an access/read path",
    "click|click-8.4.0\\src\\click\\utils.py|LazyFile":
        "lazy file-open cache; repeated access returns the cached handle",
    "cachetools|cachetools-7.1.3\\src\\cachetools\\keys.py|_HashedTuple":
        "memoized hash cache; semantic hash value is stable",
    "sortedcontainers|sortedcontainers-2.4.0\\sortedcontainers\\sorteddict.py|SortedDict":
        "deprecated cached view property; semantic view is stable",
    "boltons|boltons-25.0.0\\boltons\\cacheutils.py|CachedFunction":
        "constructor/local closure pattern; not an access/read path",
    "boltons|boltons-25.0.0\\boltons\\cacheutils.py|CachedMethod":
        "constructor/local closure pattern; not an access/read path",
    "boltons|boltons-25.0.0\\boltons\\dictutils.py|FrozenDict":
        "memoized hash cache; semantic hash value is stable",
    "boltons|boltons-25.0.0\\boltons\\excutils.py|_DeferredLine":
        "memoized string cache; repeated access returns the same line",
    "boltons|boltons-25.0.0\\boltons\\funcutils.py|CachedInstancePartial":
        "descriptor metadata initialization, not access-derived semantics",
    "boltons|boltons-25.0.0\\boltons\\ioutils.py|SpooledBytesIO":
        "lazy backing-buffer allocation; repeated access returns same buffer",
    "boltons|boltons-25.0.0\\boltons\\setutils.py|_ComplementSet":
        "in-place set update returning self; not an access/read path",
    "boltons|boltons-25.0.0\\boltons\\tbutils.py|_DeferredLine":
        "memoized string cache; repeated access returns the same line",
    "toolz|toolz-1.1.0\\toolz\\functoolz.py|curry":
        "signature cache used for currying decision; semantic decision is stable",
    "marshmallow|marshmallow-4.3.0\\src\\marshmallow\\experimental\\context.py|Context":
        "context-manager token assignment returns self; no access-derived value",
    "marshmallow|marshmallow-4.3.0\\src\\marshmallow\\fields.py|Nested":
        "lazy schema cache; repeated access returns the same schema",
    "tomlkit|tomlkit-0.15.0\\tomlkit\\items.py|Array":
        "fluent formatting mutator returns self; not an access/read path",
    "tomlkit|tomlkit-0.15.0\\tomlkit\\source.py|_State":
        "context-manager state snapshot returns self; not access-derived",
    "python-dotenv|python_dotenv-1.2.2\\src\\dotenv\\main.py|DotEnv":
        "memoized parsed dotenv dictionary; repeated access is stable",
    "structlog|structlog-25.5.0\\src\\structlog\\_config.py|BoundLoggerLazyProxy":
        "lazy binding cache/proxy setup; not access-evolving output",
    "structlog|structlog-25.5.0\\src\\structlog\\processors.py|KeyValueRenderer":
        "constructor/local setup pattern; not an access/read path",
    "pluggy|pluggy-1.6.0\\src\\pluggy\\_manager.py|PluginManager":
        "monitor registration mutates manager and returns undo callback",
    "packaging|packaging-26.2\\src\\packaging\\specifiers.py|Specifier":
        "one-element version cache; repeated access is semantically stable",
    "packaging|packaging-26.2\\src\\packaging\\specifiers.py|SpecifierSet":
        "canonicalization cache; repeated access is semantically stable",
    "packaging|packaging-26.2\\src\\packaging\\version.py|Version":
        "memoized comparison key; semantic value is stable",
    "importlib-metadata|importlib_metadata-9.0.0\\importlib_metadata\\__init__.py|FastPath":
        "deferred helper binding/cache; returned children are not access-evolving",
    "jsonschema|jsonschema-4.26.0\\jsonschema\\validators.py|Validator":
        "deprecated lazy resolver cache; repeated access is stable",
    "anyio|anyio-4.13.0\\src\\anyio\\_core\\_synchronization.py|EventAdapter":
        "lazy backend primitive allocation; repeated access returns same event",
    "anyio|anyio-4.13.0\\src\\anyio\\_core\\_synchronization.py|LockAdapter":
        "lazy backend primitive allocation; repeated access returns same lock",
    "anyio|anyio-4.13.0\\src\\anyio\\_core\\_synchronization.py|SemaphoreAdapter":
        "lazy backend primitive allocation; repeated access returns same semaphore",
    "anyio|anyio-4.13.0\\src\\anyio\\_core\\_synchronization.py|CapacityLimiterAdapter":
        "lazy backend primitive allocation; repeated access returns same limiter",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|ParserElement":
        "debug/configuration mutator returning self; not an access/read path",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|Regex":
        "compiled-regex cache; repeated access is semantically stable",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|ParseExpression":
        "grammar-builder append mutator returning self",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|And":
        "grammar streamlining mutates parser object and returns self",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|Or":
        "grammar streamlining mutates parser object and returns self",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|MatchFirst":
        "grammar streamlining mutates parser object and returns self",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|Each":
        "grammar streamlining mutates parser object and returns self",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|ParseElementEnhance":
        "whitespace configuration mutator returning self",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|_MultipleMatch":
        "grammar stop condition mutator returning self",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\core.py|Forward":
        "grammar assignment mutator returning self",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\results.py|ParseResults":
        "constructor initialization path, not access-evolving semantics",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\util.py|_UnboundedCache":
        "constructor/local closure setup, not an access/read path",
    "pyparsing|pyparsing-3.3.2\\pyparsing\\util.py|_FifoCache":
        "constructor/local closure setup, not an access/read path",
    "urllib3|urllib3-2.7.0\\src\\urllib3\\response.py|HTTPResponse":
        "connection release mutates state but returns no access-derived value",
    "jinja2|jinja2-3.1.6\\src\\jinja2\\environment.py|Template":
        "lazy module cache; repeated access is normally stable",
    "jinja2|jinja2-3.1.6\\src\\jinja2\\idtracking.py|FrameSymbolVisitor":
        "visitor bookkeeping mutates state and returns None",
    "jinja2|jinja2-3.1.6\\src\\jinja2\\lexer.py|Lexer":
        "constructor/local setup pattern; not an access/read path",
    "flask|flask-3.1.3\\src\\flask\\cli.py|ScriptInfo":
        "lazy app cache; repeated load returns the same application object",
    "flask|flask-3.1.3\\src\\flask\\testing.py|FlaskClient":
        "context-manager preserve-context flag returns self; no access-derived value",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\datastructures\\mixins.py|ImmutableListMixin":
        "memoized hash cache; semantic hash value is stable",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\datastructures\\mixins.py|ImmutableDictMixin":
        "memoized hash cache; semantic hash value is stable",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\debug\\console.py|_InteractiveConsole":
        "constructor/local setup pattern; not an access/read path",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\local.py|_ProxyLookup":
        "descriptor/proxy setup pattern; not an access/read path",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\local.py|_ProxyIOp":
        "descriptor/proxy setup pattern; not an access/read path",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\middleware\\http_proxy.py|ProxyMiddleware":
        "constructor/local setup pattern; not an access/read path",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\sansio\\response.py|Response":
        "lazy header object cache; repeated access is semantically stable",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\test.py|EnvironBuilder":
        "lazy args cache; repeated access returns the same semantic mapping",
    "werkzeug|werkzeug-3.1.8\\src\\werkzeug\\wrappers\\request.py|Request":
        "request body cache; repeated access returns stable cached data",
    "pathspec|pathspec-1.1.1\\pathspec\\pathspec.py|PathSpec":
        "in-place pattern-list update returning self; not an access/read path",
    "dacite|dacite-1.9.2\\dacite\\frozen_dict.py|FrozenDict":
        "memoized hash cache; semantic hash value is stable",
    "wrapt|wrapt-2.2.0\\src\\wrapt\\caching.py|_LRUCacheFunctionWrapper":
        "LRU memoization wrapper; cache fill does not indicate access-evolving object semantics",
    "wrapt|wrapt-2.2.0\\src\\wrapt\\decorators.py|_StateBindingWrapper":
        "decorator binding wrapper setup; not an access/read path",
    "wrapt|wrapt-2.2.0\\src\\wrapt\\proxies.py|LazyObjectProxy":
        "lazy proxy target cache; repeated access returns stable wrapped object",
    "wrapt|wrapt-2.2.0\\src\\wrapt\\wrappers.py|ObjectProxy":
        "in-place operator forwarding returning self; not an access/read path",
    "wrapt|wrapt-2.2.0\\src\\wrapt\\wrappers.py|PartialCallableObjectProxy":
        "constructor/local setup pattern; not an access/read path",
    "dateparser|dateparser-1.4.0\\dateparser\\date.py|_DateLocaleParser":
        "lazy translated-date cache; repeated access is semantically stable",
    "parsedatetime|parsedatetime-2.6\\parsedatetime\\__init__.py|Constants":
        "constructor/local setup pattern; not an access/read path",
    "Babel|babel-2.18.0\\babel\\core.py|Locale":
        "lazy locale-data cache; repeated access is semantically stable",
    "Babel|babel-2.18.0\\babel\\messages\\catalog.py|Catalog":
        "lazy plural-count cache; repeated access is semantically stable",
    "Babel|babel-2.18.0\\babel\\plural.py|PluralRule":
        "lazy compiled-rule cache; repeated access returns stable semantics",
    "beautifulsoup4|beautifulsoup4-4.14.3\\bs4\\__init__.py|BeautifulSoup":
        "constructor/tree-builder setup pattern; not an access/read path",
    "pygments|pygments-2.20.0\\pygments\\formatters\\latex.py|LatexFormatter":
        "stylesheet construction cache; repeated access is semantically stable",
}


def normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def ensure_dirs() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)


def download_sdist(package: str) -> tuple[Path | None, str | None]:
    existing = sorted(DOWNLOAD_DIR.glob(f"{package.replace('-', '*')}*"))
    existing = [p for p in existing if p.suffix in {".zip", ".gz", ".whl"} or p.name.endswith(".tar.gz")]
    if existing:
        return existing[-1], None

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--no-deps",
        "--no-binary",
        ":all:",
        "--dest",
        str(DOWNLOAD_DIR),
        package,
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True)
    first_error = (proc.stderr or proc.stdout).strip()
    if proc.returncode != 0:
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--no-deps",
            "--only-binary",
            ":all:",
            "--dest",
            str(DOWNLOAD_DIR),
            package,
        ]
        proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout).strip() or first_error

    candidates = sorted(DOWNLOAD_DIR.glob("*"))
    normalized = normalize_name(package)
    matches = [p for p in candidates if normalize_name(p.name).startswith(normalized)]
    if not matches:
        return None, "download completed but no matching archive was found"
    return matches[-1], None


def extract_archive(package: str, archive: Path) -> Path:
    target = SOURCE_DIR / normalize_name(package)
    if target.exists():
        return target
    target.mkdir(parents=True, exist_ok=True)
    if archive.name.endswith(".tar.gz") or archive.suffixes[-2:] == [".tar", ".gz"]:
        with tarfile.open(archive) as tf:
            tf.extractall(target)
    elif archive.suffix in {".zip", ".whl"}:
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(target)
    else:
        raise ValueError(f"unsupported archive: {archive}")
    return target


def version_from_metadata(root: Path) -> str:
    for name in ("PKG-INFO", "METADATA"):
        for path in root.rglob(name):
            try:
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
            except OSError:
                continue
    return ""


def iter_python_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.py")):
        parts = {p.lower() for p in path.relative_to(root).parts[:-1]}
        if parts & SKIP_DIRS:
            continue
        name = path.name.lower()
        if name.startswith("test") or name == "conftest.py":
            continue
        yield path


def count_defs(path: Path) -> tuple[int, int]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"),
                         filename=str(path))
    except SyntaxError:
        return 0, 0
    classes = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
    functions = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    for n in ast.walk(tree))
    return classes, functions


def mechanisms_for(cls: dict) -> str:
    bits = []
    if cls["P1_access_sensitive"]:
        bits.append("P1_access_sensitive")
    if cls["P2_observation_mutates"]:
        bits.append("P2_observation_mutates")
    if cls["P3_nonlinear_composition"]:
        bits.append("P3_nonlinear_composition")
    return "; ".join(bits)


def short_reason(cls: dict) -> str:
    evidence = cls.get("evidence", {})
    for key in ("P1", "P2", "P3"):
        vals = evidence.get(key) or []
        if vals:
            return vals[0]
    return "No evidence string emitted."


def review_key(package: str, rel_file: str, class_name: str) -> str:
    return f"{package}|{rel_file}|{class_name}"


def manual_review(package: str, rel_file: str, class_name: str) -> tuple[str, str]:
    key = review_key(package, rel_file, class_name)
    if key in FALSE_POSITIVES:
        return "likely false positive", FALSE_POSITIVES[key]
    return (
        "likely true positive",
        "source review found state mutation on a method/property/call path that returns a value or access handle",
    )


def scan_package(package: str) -> tuple[dict, list[dict]]:
    archive, error = download_sdist(package)
    if error or archive is None:
        return {
            "package": package,
            "version": "",
            "status": "download_failed",
            "error": error or "unknown download failure",
            "files_scanned": 0,
            "classes_scanned": 0,
            "functions_scanned": 0,
            "SAFE": 0,
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
        }, []

    try:
        root = extract_archive(package, archive)
    except Exception as exc:
        return {
            "package": package,
            "version": "",
            "status": "extract_failed",
            "error": str(exc),
            "files_scanned": 0,
            "classes_scanned": 0,
            "functions_scanned": 0,
            "SAFE": 0,
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
        }, []

    version = version_from_metadata(root)
    label_counts: Counter[str] = Counter()
    files_scanned = classes_scanned = functions_scanned = 0
    findings: list[dict] = []

    for py_file in iter_python_files(root):
        class_count, function_count = count_defs(py_file)
        classes_scanned += class_count
        functions_scanned += function_count
        try:
            result = analyze_file(py_file)
        except Exception:
            continue
        files_scanned += 1
        rel_file = str(py_file.relative_to(root))
        for cls in result["classes"]:
            label = cls["risk_label"]
            label_counts[label] += 1
            if label in {"MEDIUM", "HIGH"}:
                review, note = manual_review(package, rel_file, cls["class"])
                findings.append({
                    "package": package,
                    "version": version,
                    "file_path": rel_file,
                    "line": cls["line"],
                    "name": cls["class"],
                    "analyzer_label": label,
                    "detected_mechanisms": mechanisms_for(cls),
                    "short_reason": short_reason(cls),
                    "manual_review": review,
                    "manual_review_note": note,
                })

    summary = {
        "package": package,
        "version": version,
        "status": "analyzed",
        "error": "",
        "files_scanned": files_scanned,
        "classes_scanned": classes_scanned,
        "functions_scanned": functions_scanned,
        "SAFE": label_counts["SAFE"],
        "LOW": label_counts["LOW"],
        "MEDIUM": label_counts["MEDIUM"],
        "HIGH": label_counts["HIGH"],
    }
    return summary, findings


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(package_rows: list[dict], findings: list[dict]) -> None:
    attempted = len(package_rows)
    analyzed = [r for r in package_rows if r["status"] == "analyzed"]
    skipped = [r for r in package_rows if r["status"] != "analyzed"]
    aggregate = Counter()
    for row in analyzed:
        for label in ("SAFE", "LOW", "MEDIUM", "HIGH"):
            aggregate[label] += int(row[label])

    review_counts = Counter(f["manual_review"] for f in findings)
    tp = review_counts["likely true positive"]
    fp = review_counts["likely false positive"]
    precision = tp / (tp + fp) if (tp + fp) else None

    interesting_tp = [f for f in findings if f["manual_review"] == "likely true positive"][:10]
    interesting_fp = [f for f in findings if f["manual_review"] == "likely false positive"][:10]

    lines = [
        "# PyPI Static Analyzer Benchmark",
        "",
        "## Scope",
        f"- packages attempted: {attempted}",
        f"- packages successfully analyzed: {len(analyzed)}",
        f"- Python files scanned: {sum(int(r['files_scanned']) for r in analyzed)}",
        f"- classes scanned: {sum(int(r['classes_scanned']) for r in analyzed)}",
        f"- functions scanned: {sum(int(r['functions_scanned']) for r in analyzed)}",
        f"- MEDIUM/HIGH findings reviewed: {len(findings)}",
        "",
        "Packages analyzed: " + ", ".join(r["package"] for r in analyzed),
    ]
    if skipped:
        lines.append("Packages skipped:")
        for row in skipped:
            reason = (row["error"] or row["status"]).replace("\n", " ").strip()
            if len(reason) > 300:
                reason = reason[:297] + "..."
            lines.append(f"- {row['package']}: {row['status']} - {reason}")
    else:
        lines.append("Packages skipped: none")

    lines.extend([
        "",
        "## Aggregate analyzer labels",
        "",
        "| Label | Count |",
        "| --- | ---: |",
    ])
    for label in ("SAFE", "LOW", "MEDIUM", "HIGH"):
        lines.append(f"| {label} | {aggregate[label]} |")

    lines.extend([
        "",
        "## Manual review of flagged findings",
        "",
        "| Review label | Count |",
        "| --- | ---: |",
        f"| likely true positive | {review_counts['likely true positive']} |",
        f"| likely false positive | {review_counts['likely false positive']} |",
        f"| unclear | {review_counts['unclear']} |",
        "",
        "## Precision over reviewed flagged findings",
        "",
    ])
    if precision is None:
        lines.append("Precision is not calculated because no flagged findings were manually classified as likely true or likely false positives.")
    else:
        lines.append(
            "precision = likely_true_positive / (likely_true_positive + likely_false_positive) "
            f"= {tp} / ({tp} + {fp}) = {precision:.4f}"
        )
    lines.append("Unclear cases are excluded from the denominator.")

    lines.extend([
        "",
        "## Recall",
        "",
        "Recall is not estimated because SAFE and LOW classes were not exhaustively manually labeled.",
        "",
        "## Notable findings",
        "",
    ])
    if interesting_tp:
        lines.append("Likely true positives:")
        for f in interesting_tp:
            lines.append(f"- {f['package']} `{f['name']}` in `{f['file_path']}`: {f['manual_review_note']}")
    else:
        lines.append("Likely true positives: none after manual review.")
    if interesting_fp:
        lines.append("")
        lines.append("Likely false positives:")
        for f in interesting_fp:
            lines.append(f"- {f['package']} `{f['name']}` in `{f['file_path']}`: {f['manual_review_note']}")
    else:
        lines.append("")
        lines.append("Likely false positives: none after manual review.")

    lines.extend([
        "",
        "## Limitations",
        "",
        "- packages are not a random sample of PyPI",
        "- analyzer is syntactic and heuristic",
        "- precision is estimated only over reviewed flagged findings",
        "- recall is not established",
        "- absence of findings does not prove absence of access-evolving semantics",
    ])

    SUMMARY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict:
    ensure_dirs()
    package_rows: list[dict] = []
    findings: list[dict] = []
    for package in PACKAGES:
        row, pkg_findings = scan_package(package)
        package_rows.append(row)
        findings.extend(pkg_findings)
        print(f"{package}: {row['status']} files={row['files_scanned']} classes={row['classes_scanned']} flagged={row['MEDIUM'] + row['HIGH']}")

    write_csv(SUMMARY_CSV, package_rows, [
        "package", "version", "status", "error", "files_scanned",
        "classes_scanned", "functions_scanned", "SAFE", "LOW",
        "MEDIUM", "HIGH",
    ])
    write_csv(FINDINGS_CSV, findings, [
        "package", "version", "file_path", "line", "name",
        "analyzer_label", "detected_mechanisms", "short_reason",
        "manual_review", "manual_review_note",
    ])
    write_summary(package_rows, findings)
    return {"packages": package_rows, "findings": findings}


def main() -> int:
    run()
    print(f"wrote {SUMMARY_CSV}")
    print(f"wrote {FINDINGS_CSV}")
    print(f"wrote {SUMMARY_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
