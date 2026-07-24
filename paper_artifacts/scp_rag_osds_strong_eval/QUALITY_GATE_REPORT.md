# RAG Strong Evaluation Quality Gate Report

Overall self-check status: True

| Check | Passed | Detail |
| --- | --- | --- |
| corpus has at least 120 documents | True | 120 |
| scenarios have at least 48 cases | True | 48 |
| at least 8 negative controls exist | True | 8 |
| JSON files parse | True | parsed |
| CSV headers exist | True | results and ablation CSV headers present |
| replay deterministic | True | True |
| pure baseline scenarios stable | True | 8/8 |
| negative controls mostly or fully stable | True | 8/8 |
| feedback-disabled ablations remove answer divergences | True | 0 disabled answer divergences |
| at least 3 non-baseline variants show default answer divergence | True | access_count_feedback, agent_trace_feedback, cache_materialization_feedback, explanation_focus_feedback, recency_memory_feedback |
| no placeholder markers remain in reports | True | scanned report markdown |

## Command Results

- `python paper_artifacts/scp_rag_osds_strong_eval/run_rag_strong_eval.py`: the workspace `python` launcher was unavailable (`python` was not recognized), so the same script was run with the bundled interpreter at `python`; PASS, generated corpus, scenarios, results, ablations, replay check, metrics, and reports.
- `python run_tests.py`: workspace `python` launcher unavailable; bundled interpreter equivalent PASS, 28 passed and 0 failed.
- `python -m pytest tests`: workspace `python` launcher unavailable; bundled interpreter equivalent PASS, 44 passed in 3.29s.
