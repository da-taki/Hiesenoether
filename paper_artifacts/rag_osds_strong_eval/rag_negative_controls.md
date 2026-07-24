# RAG Strong Evaluation Negative Controls

Negative controls: 8

Stable controls: 8

Unexpected divergences: 0

Interpretation: these pure-baseline controls exercise observation-shaped operations without enabling latent feedback. They bound the positive cases by showing that the scenario design alone does not force answer changes.

| Scenario | Operation | Classification | A answer | B answer |
| --- | --- | --- | --- | --- |
| B01_pure_baseline_negative_control | preview_context | no_divergence | LRU | LRU |
| B02_pure_baseline_negative_control | log_retrieval | no_divergence | reader | reader |
| B03_pure_baseline_negative_control | explain_retrieval | no_divergence | Denver | Denver |
| B04_pure_baseline_negative_control | materialize_context_cache | no_divergence | reset | reset |
| B05_pure_baseline_negative_control | trace_tool_call | no_divergence | alpha memory | alpha memory |
| B06_pure_baseline_negative_control | inspect_memory | no_divergence | pure inspection | pure inspection |
| B07_pure_baseline_negative_control | preview_context | no_divergence | calculator | calculator |
| B08_pure_baseline_negative_control | log_retrieval | no_divergence | final policy | final policy |
