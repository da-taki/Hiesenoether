from __future__ import annotations


def parse_preservation_claim(text: str) -> str:
    stripped = text.strip().lower()
    if not stripped:
        return "UNCLEAR"
    first = stripped.split(None, 1)[0].strip(".:;,-")
    if first in {"yes", "y"}:
        return "YES"
    if first in {"no", "n"}:
        return "NO"
    if first in {"unclear", "unsure", "maybe"}:
        return "UNCLEAR"
    if stripped.startswith("i believe yes") or stripped.startswith("the transformation preserves"):
        return "YES"
    if stripped.startswith("i do not") or stripped.startswith("it does not"):
        return "NO"
    return "UNCLEAR"
