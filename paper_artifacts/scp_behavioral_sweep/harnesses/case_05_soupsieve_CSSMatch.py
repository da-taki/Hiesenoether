from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SWEEP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SWEEP))
from harness_common import write_case

META = {
  "package": "soupsieve",
  "version": "2.8.3",
  "file_path": "soupsieve-2.8.3\\soupsieve\\css_match.py",
  "class_name": "CSSMatch",
  "line_start": "544",
  "manual_review": "likely true positive",
  "risk_label": "MEDIUM",
  "mechanisms": "P1_access_sensitive",
  "manual_review_note": "source review found state mutation on a method/property/call path that returns a value or access handle",
  "score": 11,
  "source_path": "C:\\Users\\Asus\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_realworld_revision\\source_snapshot\\soupsieve-2.8.3\\soupsieve\\css_match.py",
  "source_root": "C:\\Users\\Asus\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_realworld_revision\\source_snapshot\\soupsieve-2.8.3",
  "constructor_feasibility": "requires_args",
  "import_feasibility": "source_file_available",
  "expected_observer_or_read_operation": "match_selectors",
  "expected_latent_state": "iframe_restrict,namespaces",
  "expected_later_behavior": "repeat the same read-shaped operation and compare result/state",
  "selection_reason": "+4 likely true positive; +2 read/getter-like mutation; +2 observer/repr/logging/debug-like mutation; +2 later/cache/branch/composition hint; +1 source import path available",
  "sweep_rank": 5,
  "output_json": "C:\\Users\\Asus\\Desktop\\Profitlo Projects\\Hiesenoether\\paper_artifacts\\scp_behavioral_sweep\\outputs\\case_05_soupsieve_CSSMatch.json"
}

if __name__ == '__main__':
    raise SystemExit(write_case(META, META['output_json']))
