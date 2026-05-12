from __future__ import annotations
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


OBSERVER_NAME_HINTS = {"observe", "inspect", "peek", "sample",
                       "watch", "snapshot"}
READER_NAME_HINTS   = {"read", "get", "__get__", "value", "current",
                       "__next__", "fetch"}


@dataclass
class ClassReport:
    name: str
    file: str
    line: int
    P1_evidence: List[str] = field(default_factory=list)
    P2_evidence: List[str] = field(default_factory=list)
    P3_evidence: List[str] = field(default_factory=list)
    counters_mutated: Set[str] = field(default_factory=set)

    def risk_score(self) -> int:
        """Per-CLASS risk based on intrinsic class properties (P1, P2).
        P3 is reported separately as a call-site finding because the
        nonlinear composition usually lives in user code, not in the
        class body itself."""
        p1 = bool(self.P1_evidence)
        p2 = bool(self.P2_evidence)
        if p1 and p2: return 3   # HIGH: class is a chaos source
        if p1:        return 2   # MEDIUM: drifty reader, no observer
        if p2:        return 1   # LOW: observer present but no drift
        return 0                 # SAFE

    def to_dict(self) -> dict:
        return {"class": self.name, "file": self.file, "line": self.line,
                "P1_access_sensitive":    bool(self.P1_evidence),
                "P2_observation_mutates": bool(self.P2_evidence),
                "P3_nonlinear_composition": bool(self.P3_evidence),
                "counters_mutated": sorted(self.counters_mutated),
                "evidence": {"P1": self.P1_evidence,
                             "P2": self.P2_evidence,
                             "P3": self.P3_evidence},
                "risk_score": self.risk_score(),
                "risk_label": ["SAFE", "LOW", "MEDIUM", "HIGH"][self.risk_score()]}


def _is_self_attr(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
       and node.value.id == "self":
        return node.attr
    return None


def _method_mutates_self_and_returns(method: ast.FunctionDef
                                     ) -> Tuple[bool, Set[str], bool]:
    """Returns (mutates_self, fields_mutated, has_return_value)."""
    fields: Set[str] = set()
    has_return = False
    for node in ast.walk(method):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            targets = (node.targets
                       if isinstance(node, ast.Assign) else [node.target])
            for t in targets:
                attr = _is_self_attr(t)
                if attr is not None:
                    fields.add(attr)
        if isinstance(node, ast.Return) and node.value is not None:
            has_return = True
    return (len(fields) > 0, fields, has_return)

def _method_uses_self_anywhere(method: ast.FunctionDef) -> bool:
    """Method body reads at least one self.<attr>."""
    for node in ast.walk(method):
        if _is_self_attr(node) is not None:
            return True
    return False

def _method_returns_self_attr_expr(method: ast.FunctionDef) -> bool:
    """Return is an expression involving self.<attr> reads (not constants)."""
    for node in ast.walk(method):
        if isinstance(node, ast.Return) and node.value is not None:
            for sub in ast.walk(node.value):
                if _is_self_attr(sub) is not None:
                    return True
    return False


class ClassAnalyzer(ast.NodeVisitor):
    def __init__(self, file: str):
        self.file = file
        self.reports: List[ClassReport] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        rep = ClassReport(name=node.name, file=self.file, line=node.lineno)
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

        for m in methods:
            mutates, fields, has_ret = _method_mutates_self_and_returns(m)
            uses_self_in_return = _method_returns_self_attr_expr(m)
            uses_self_anywhere = _method_uses_self_anywhere(m)

            looks_like_reader = (m.name in READER_NAME_HINTS
                                 or m.name.startswith("read")
                                 or m.name.startswith("get"))
            looks_like_observer = (m.name in OBSERVER_NAME_HINTS
                                   or m.name.startswith("observe")
                                   or m.name.startswith("inspect"))

            is_p1 = False
            if mutates and not looks_like_observer:
                if uses_self_in_return:
                    is_p1 = True
                elif has_ret and uses_self_anywhere:
                    is_p1 = True
                elif looks_like_reader and uses_self_anywhere:
                    is_p1 = True
            if is_p1:
                rep.P1_evidence.append(
                    f"method {m.name}() (line {m.lineno}): "
                    f"mutates self.{{{','.join(sorted(fields))}}} "
                    f"and returns a value derived from self state")
                rep.counters_mutated.update(fields)

            # P2: observation-sensitive method that mutates self.
            if looks_like_observer and mutates:
                rep.P2_evidence.append(
                    f"method {m.name}() (line {m.lineno}): "
                    f"mutates self.{{{','.join(sorted(fields))}}}")

        rep.P3_evidence.extend(self._find_nonlinear_uses_in(node))
        self.reports.append(rep)
        self.generic_visit(node)

    def _find_nonlinear_uses_in(self, classdef: ast.ClassDef) -> List[str]:
        """Look for multiplicative chains x.attr * x.attr or x.f() * x.f()
        IGNORING base == 'self' (those are class-internal arithmetic on
        scalar fields, not the multiplicative composition of repeated
        observable reads we are looking for)."""
        evidence = []
        for node in ast.walk(classdef):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
                names = self._extract_chain_names(node)
                counts: Dict[str, int] = {}
                for n in names:
                    if n == "self":
                        continue
                    counts[n] = counts.get(n, 0) + 1
                hot = {k: v for k, v in counts.items() if v >= 2}
                if hot:
                    evidence.append(
                        f"line {getattr(node, 'lineno', '?')}: "
                        f"multiplicative chain repeats base(s) {hot}")
        return evidence

    def _extract_chain_names(self, node: ast.BinOp) -> List[str]:
        names = []
        def walk(n):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mult):
                walk(n.left); walk(n.right); return
            base = self._base_name(n)
            if base: names.append(base)
        walk(node)
        return names

    def _base_name(self, n: ast.AST) -> Optional[str]:
        if isinstance(n, ast.Call):
            return self._base_name(n.func)
        if isinstance(n, ast.Attribute):
            v = n.value
            if isinstance(v, ast.Name): return v.id
            if isinstance(v, ast.Attribute): return self._base_name(v)
        if isinstance(n, ast.Name):
            return n.id
        return None


# ── module-level P3 scan (calls to method) ──

def find_module_level_nonlinear_uses(tree: ast.Module, file: str) -> List[dict]:
    """Catch usage patterns like  y = x.read() * x.read() * x.read()
    that occur outside a class definition. Skips bases that are inside
    function/class bodies; only top-level (module-scope) chains count,
    so internal class arithmetic doesn't dominate the report."""
    findings = []
    # Collect AST nodes that are NOT inside ClassDef or FunctionDef.
    def at_module_scope(target_node):
        # We re-walk and check ancestry by linking parents below.
        return True
    # Walk with parents.
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.__oc_parent__ = parent
    def is_module_scope(n):
        p = getattr(n, "__oc_parent__", None)
        while p is not None:
            if isinstance(p, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                return False
            p = getattr(p, "__oc_parent__", None)
        return True
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            if not is_module_scope(node):
                continue
            ca = ClassAnalyzer(file)
            names = ca._extract_chain_names(node)
            counts: Dict[str, int] = {}
            for n in names:
                if n == "self":
                    continue
                counts[n] = counts.get(n, 0) + 1
            hot = {k: v for k, v in counts.items() if v >= 2}
            if hot:
                findings.append({"file": file,
                                 "line": getattr(node, "lineno", -1),
                                 "repeated_bases": hot})
    return findings


def analyze_file(path: Path) -> dict:
    src = path.read_text()
    tree = ast.parse(src, filename=str(path))
    ca = ClassAnalyzer(str(path))
    ca.visit(tree)
    module_p3 = find_module_level_nonlinear_uses(tree, str(path))
    return {"file": str(path),
            "classes": [r.to_dict() for r in ca.reports],
            "module_level_nonlinear_uses": module_p3,
            "high_risk_classes":
                [r.name for r in ca.reports if r.risk_score() == 3]}


def analyze_path(path: Path) -> List[dict]:
    if path.is_file() and path.suffix == ".py":
        return [analyze_file(path)]
    results = []
    if path.is_dir():
        for f in sorted(path.rglob("*.py")):
            try:
                results.append(analyze_file(f))
            except SyntaxError as e:
                results.append({"file": str(f), "error": f"parse: {e}"})
    return results


def main(argv: List[str]) -> int:
    json_out = False
    args = argv[1:]
    if "--json" in args:
        json_out = True
        args.remove("--json")
    if not args:
        print("usage: python -m analysis.oc_static [--json] <path>")
        return 2
    target = Path(args[0])
    results = analyze_path(target)
    if json_out:
        print(json.dumps(results, indent=2))
        return 0

    print(f"Ordered-Chaos static analysis of {target}")
    print("=" * 60)
    any_high = False
    for r in results:
        if "error" in r:
            print(f"  [skip] {r['file']}: {r['error']}"); continue
        for c in r["classes"]:
            label = c["risk_label"]
            marker = "!!" if label == "HIGH" else "  "
            print(f"{marker} {label:<7} {c['class']:<24} "
                  f"{Path(c['file']).name}:{c['line']}")
            if label == "HIGH":
                any_high = True
            if label in ("HIGH", "MEDIUM"):
                for k, ev_list in c["evidence"].items():
                    for ev in ev_list:
                        print(f"      [{k}] {ev}")
        for mp in r["module_level_nonlinear_uses"]:
            print(f"   .. module-level nonlinear use at "
                  f"{Path(mp['file']).name}:{mp['line']} -> {mp['repeated_bases']}")
    return 1 if any_high else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))