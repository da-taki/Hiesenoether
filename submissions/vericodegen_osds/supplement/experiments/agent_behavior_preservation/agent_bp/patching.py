from __future__ import annotations

import re


class PatchExtractionError(ValueError):
    pass


PY_BLOCK = re.compile(r"```(?:python|py)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_python(raw_response: str) -> str:
    match = PY_BLOCK.search(raw_response)
    code = match.group(1) if match else raw_response
    code = code.strip()
    if not code:
        raise PatchExtractionError("empty candidate response")
    if "def subject" not in code:
        raise PatchExtractionError("candidate does not define subject()")
    return code + "\n"
