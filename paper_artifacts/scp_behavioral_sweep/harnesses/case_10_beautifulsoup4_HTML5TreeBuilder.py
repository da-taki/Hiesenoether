from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SWEEP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SWEEP))
from harness_common import write_case

META = {
  "package": "beautifulsoup4",
  "version": "4.14.3",
  "file_path": "beautifulsoup4-4.14.3\\bs4\\builder\\_html5lib.py",
  "class_name": "HTML5TreeBuilder",
  "line_start": "59",
  "manual_review": "likely true positive",
  "risk_label": "MEDIUM",
  "mechanisms": "P1_access_sensitive",
  "manual_review_note": "source review found state mutation on a method/property/call path that returns a value or access handle",
  "score": 10,
  "source_path": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_realworld_revision\\source_snapshot\\beautifulsoup4-4.14.3\\bs4\\builder\\_html5lib.py",
  "source_root": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_realworld_revision\\source_snapshot\\beautifulsoup4-4.14.3",
  "constructor_feasibility": "simple",
  "import_feasibility": "source_file_available",
  "expected_observer_or_read_operation": "create_treebuilder",
  "expected_latent_state": "underlying_builder",
  "expected_later_behavior": "repeat the same read-shaped operation and compare result/state",
  "selection_reason": "+4 likely true positive; +2 read/getter-like mutation; +2 later/cache/branch/composition hint; +1 simple constructor; +1 source import path available",
  "sweep_rank": 10,
  "output_json": "<home>\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_behavioral_sweep\\outputs\\case_10_beautifulsoup4_HTML5TreeBuilder.json"
}

if __name__ == '__main__':
    raise SystemExit(write_case(META, META['output_json']))
