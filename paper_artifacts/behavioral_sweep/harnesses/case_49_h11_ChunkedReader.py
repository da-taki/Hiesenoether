from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SWEEP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SWEEP))
from harness_common import write_case

META = {
  "package": "h11",
  "version": "0.16.0",
  "file_path": "h11-0.16.0\\h11\\_readers.py",
  "class_name": "ChunkedReader",
  "line_start": "148",
  "manual_review": "likely true positive",
  "risk_label": "MEDIUM",
  "mechanisms": "P1_access_sensitive",
  "manual_review_note": "source review found state mutation on a method/property/call path that returns a value or access handle",
  "score": 10,
  "source_path": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\realworld_package_study\\source_snapshot\\h11-0.16.0\\h11\\_readers.py",
  "source_root": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\realworld_package_study\\source_snapshot\\h11-0.16.0",
  "constructor_feasibility": "simple",
  "import_feasibility": "source_file_available",
  "expected_observer_or_read_operation": "__call__",
  "expected_latent_state": "_bytes_in_chunk,_bytes_to_discard,_reading_trailer",
  "expected_later_behavior": "repeat the same read-shaped operation and compare result/state",
  "selection_reason": "+4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available",
  "sweep_rank": 49,
  "output_json": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\behavioral_sweep\\outputs\\case_49_h11_ChunkedReader.json"
}

if __name__ == '__main__':
    raise SystemExit(write_case(META, META['output_json']))
