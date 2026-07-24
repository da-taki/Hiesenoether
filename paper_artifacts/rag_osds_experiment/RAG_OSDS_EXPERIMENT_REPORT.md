# RAG OSDS Experiment Report

## 1. Executive Summary

This deterministic synthetic RAG simulator ran 7 scenarios across pure and feedback variants. It found 4 answer divergences, 4 total top-k retrieval-order changes, 0 retrieval-order-only divergences, and 1 state-only divergence(s). Pure baseline scenarios stayed stable: True. Feedback-disabled ablations removed divergences: True. Replay was deterministic: True.

## 2. Why RAG/Agent Systems Are Relevant

RAG and agentic systems often expose operations that look observational: previewing retrieved context, logging retrieval, explaining a trace, or inspecting memory. In adaptive systems those reads can plausibly update access counts, recency memory, cache materialization, or focus terms used by later retrieval.

## 3. Simulator Design

The simulator uses a small synthetic corpus, lexical token-overlap scoring with deterministic tie-breaking, optional deterministic feedback terms, and an answer generator that returns the marked `answer_span` from the top retrieved document. No external API, network, paid model, or random component is used.

## 4. Variants

- `pure_baseline`: observation methods do not mutate retrieval state.
- `access_count_feedback`: retrieval/logging increments document access counts used in later ranking.
- `recency_memory_feedback`: preview/retrieval stores document IDs in session memory used as a later recency boost.
- `explanation_feedback`: explanations store focus terms used as a later retrieval feature.
- `cache_materialization_feedback`: preview/log/retrieval materializes cache state used as a later ranking feature.

## 5. Scenario Table

| Scenario | Variant | Observation | Classification | A top-k | B top-k | A answer | B answer |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1_baseline_preview_cache | pure_baseline | preview_context | no_divergence | cache_lru,cache_lri | cache_lru,cache_lri | LRU | LRU |
| S2_access_log_cache | access_count_feedback | log_retrieval | confirmed_answer_divergence | cache_lru,cache_lri | cache_lri,cache_lru | LRU | LRI |
| S3_recency_preview_city | recency_memory_feedback | preview_context | confirmed_answer_divergence | accessibility_berlin,accessibility_boston | accessibility_boston,accessibility_berlin | Berlin | Boston |
| S4_explain_markdown | explanation_feedback | explain_retrieval | confirmed_answer_divergence | markdown_reset,markdown_build | markdown_build,markdown_reset | reset | build_parser |
| S5_cache_materialization_stream | cache_materialization_feedback | preview_context | confirmed_answer_divergence | stream_reader,stream_logger | stream_logger,stream_reader | StreamReader | TraceLogger |
| S6_recency_inspect_state | recency_memory_feedback | preview_context | confirmed_state_only_divergence | memory_alpha,memory_beta | memory_alpha,memory_beta | Alpha Memory | Alpha Memory |
| S7_baseline_explain_markdown | pure_baseline | explain_retrieval | no_divergence | markdown_reset,markdown_build | markdown_reset,markdown_build | reset | reset |

## 6. Main Results Table

- `confirmed_answer_divergence`: 4
- scenarios with top-k order changed: 4
- `confirmed_retrieval_order_divergence`: 0
- `confirmed_state_only_divergence`: 1
- `no_divergence`: 2

## 7. Ablation Results

| Scenario | Mode | Weight | Classification | Answer changed |
| --- | --- | --- | --- | --- |
| S2_access_log_cache | disabled | 0.0 | no_divergence | False |
| S2_access_log_cache | default | 1.25 | confirmed_answer_divergence | True |
| S2_access_log_cache | strong | 3.0 | confirmed_answer_divergence | True |
| S3_recency_preview_city | disabled | 0.0 | no_divergence | False |
| S3_recency_preview_city | default | 1.75 | confirmed_answer_divergence | True |
| S3_recency_preview_city | strong | 3.0 | confirmed_answer_divergence | True |
| S4_explain_markdown | disabled | 0.0 | no_divergence | False |
| S4_explain_markdown | default | 1.5 | confirmed_answer_divergence | True |
| S4_explain_markdown | strong | 3.0 | confirmed_answer_divergence | True |
| S5_cache_materialization_stream | disabled | 0.0 | no_divergence | False |
| S5_cache_materialization_stream | default | 1.25 | confirmed_answer_divergence | True |
| S5_cache_materialization_stream | strong | 3.0 | confirmed_answer_divergence | True |
| S6_recency_inspect_state | disabled | 0.0 | no_divergence | False |
| S6_recency_inspect_state | default | 1.75 | confirmed_state_only_divergence | False |
| S6_recency_inspect_state | strong | 3.0 | confirmed_state_only_divergence | False |

## 8. Replay/Determinism Check

The full experiment and ablation were run twice and compared as JSON. Deterministic replay passed: True.

## 9. Interpretation

The experiment demonstrates mechanism plausibility: observation-shaped retrieval, logging, preview, and explanation operations can be modeled as access-observation feedback loops that alter later context or answers. The baseline and zero-weight ablations isolate feedback as the necessary mechanism in this simulator.

## 10. Limitations

This is a synthetic deterministic RAG simulator. It does not evaluate commercial RAG systems, does not show real-world prevalence, does not measure speed improvement, and does not show package bugs. Several positive cases are expected effects of explicitly stateful feedback policies.

## 11. Artifact Integration Recommendation

Use this as appendix or short discussion evidence for mechanism plausibility in RAG/agentic systems. It is strong enough to motivate a cautious paragraph, but not strong enough for a headline empirical claim about deployed systems.
