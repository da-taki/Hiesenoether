from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SWEEP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SWEEP))
from harness_common import write_case

META = {
  "package": "more-itertools",
  "version": "11.0.2",
  "file_path": "more_itertools-11.0.2\\more_itertools\\more.py",
  "class_name": "seekable",
  "line_start": "2917",
  "manual_review": "likely true positive",
  "risk_label": "HIGH",
  "mechanisms": "P1_access_sensitive; P2_observation_mutates",
  "manual_review_note": "source review found state mutation on a method/property/call path that returns a value or access handle",
  "score": 12,
  "source_path": "C:\\Users\\Asus\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_realworld_revision\\source_snapshot\\more-itertools-11.0.2\\more_itertools\\more.py",
  "source_root": "C:\\Users\\Asus\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_realworld_revision\\source_snapshot\\more-itertools-11.0.2",
  "constructor_feasibility": "requires_args",
  "import_feasibility": "source_file_available",
  "expected_observer_or_read_operation": "__next__",
  "expected_latent_state": "_index",
  "expected_later_behavior": "repeat the same read-shaped operation and compare result/state",
  "selection_reason": "+4 likely true positive; +3 HIGH; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 source import path available",
  "sweep_rank": 2,
  "output_json": "C:\\Users\\Asus\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_behavioral_sweep\\outputs\\case_02_more_itertools_seekable.json"
}

if __name__ == '__main__':
    raise SystemExit(write_case(META, META['output_json']))
