from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SWEEP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SWEEP))
from harness_common import write_case

META = {
  "package": "anyio",
  "version": "4.13.0",
  "file_path": "anyio-4.13.0\\src\\anyio\\from_thread.py",
  "class_name": "BlockingPortalProvider",
  "line_start": "443",
  "manual_review": "likely true positive",
  "risk_label": "MEDIUM",
  "mechanisms": "P1_access_sensitive",
  "manual_review_note": "source review found state mutation on a method/property/call path that returns a value or access handle",
  "score": 10,
  "source_path": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_realworld_revision\\source_snapshot\\anyio-4.13.0\\anyio\\from_thread.py",
  "source_root": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_realworld_revision\\source_snapshot\\anyio-4.13.0",
  "constructor_feasibility": "simple",
  "import_feasibility": "source_file_available",
  "expected_observer_or_read_operation": "__enter__",
  "expected_latent_state": "_leases,_portal,_portal_cm",
  "expected_later_behavior": "repeat the same read-shaped operation and compare result/state",
  "selection_reason": "+4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available",
  "sweep_rank": 9,
  "output_json": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_behavioral_sweep\\outputs\\case_09_anyio_BlockingPortalProvider.json"
}

if __name__ == '__main__':
    raise SystemExit(write_case(META, META['output_json']))
