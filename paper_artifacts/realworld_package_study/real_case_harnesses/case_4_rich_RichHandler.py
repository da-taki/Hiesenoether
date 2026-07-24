from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

SNAPSHOT = Path(__file__).resolve().parents[1] / "source_snapshot" / "rich-15.0.0"
TEMP = Path.home() / "AppData" / "Local" / "Temp" / "hiesenoether_pypi_static_benchmark" / "sources" / "rich" / "rich-15.0.0"
if SNAPSHOT.exists():
    sys.path.insert(0, str(SNAPSHOT))
elif TEMP.exists():
    sys.path.insert(0, str(TEMP))

import rich
from rich.logging import RichHandler

OUT = Path(__file__).resolve().parents[1] / "real_case_outputs" / "case_4_rich_RichHandler.json"

def run_sequence(observe_first: bool) -> dict[str, object]:
    handler = RichHandler(markup=True, highlighter=None)
    record = logging.LogRecord("rich_case", logging.INFO, __file__, 1, "GET /index", (), None)
    before = {"keywords": handler.keywords}
    rendered = None
    if observe_first:
        rendered = str(handler.render_message(record, record.getMessage()))
    after = {"keywords": handler.keywords, "rendered": rendered}
    return {"before": before, "after": after}

def main() -> int:
    a = run_sequence(False)
    b = run_sequence(True)
    state_diff = a["after"]["keywords"] != b["after"]["keywords"]
    data = {
        "case_id": "case_4_rich_RichHandler",
        "package": "rich",
        "version": getattr(rich, "__version__", "15.0.0"),
        "class_name": "RichHandler",
        "file_path": "rich/logging.py",
        "operation_A": "construct handler; do not render message",
        "result_A": a,
        "operation_B": "construct handler; render_message() once",
        "result_B": b,
        "branch_flip": False,
        "output_diff": False,
        "state_diff": state_diff,
        "classification": "confirmed_state_divergence_only" if state_diff else "structural_only_no_runtime_difference",
        "read_or_observer_operation": "RichHandler.render_message()",
        "latent_state": "handler.keywords",
        "later_read_or_behavior": "later handler keyword-highlighting state",
        "notes": "Logging/rendering path mutates keyword-highlight configuration on first render.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
