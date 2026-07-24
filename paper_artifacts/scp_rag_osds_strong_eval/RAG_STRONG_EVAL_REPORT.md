# RAG Strong OSDS Evaluation Report

## 1. Executive Summary

This deterministic controlled RAG-shaped evaluation uses 120 synthetic documents and 48 scenarios. It found 31 answer divergences, 5 retrieval-order-only divergences, 4 state-only divergences, and 8 no-divergence cases. Pure baseline stability was 100.00%; negative-control stability was 100.00%; zero-feedback ablations removed answer divergences with rate 100.00%. Exact replay deterministic: True.

## 2. Why This Is A RAG/Agentic OSDS Evaluation

The pipeline retrieves documents, selects top-k context, and extracts an answer span from the top document. The tested operations look observational or diagnostic: previewing context, logging retrieval, explaining retrieval, inspecting memory, tracing tool calls, and materializing context cache. The OSDS question is whether those OBS-like operations can mutate latent retrieval/session state that is later consumed by a READ/ANSWER operation.

## 3. Corpus Design

The corpus is synthetic but controlled and realistic in shape: eight topic families with fifteen documents per family. Each family contains one intended target answer document, close distractors, one observation-boostable answer-changing document, one same-answer support document for retrieval-order-only cases, one unrelated state-only probe, and neutral distractors.

## 4. Pipeline Variants

- `pure_baseline`: observation methods are pure and do not mutate latent retrieval state.
- `access_count_feedback`: preview/log operations increment document access counts consumed by later ranking.
- `recency_memory_feedback`: preview/log operations append document IDs to session memory consumed by later ranking.
- `explanation_focus_feedback`: explanations store focus terms consumed by later ranking.
- `cache_materialization_feedback`: preview/log/materialization stores cached document IDs consumed by later ranking.
- `agent_trace_feedback`: tool-call tracing stores tool/document associations consumed by later ranking.

## 5. Scenario Suite

The suite contains eight pure-baseline negative controls and eight scenarios for each feedback variant. Within each feedback variant, six scenarios are designed for possible answer changes, one for retrieval-order-only change, and one for state-only change.

## 6. Main Results

| Variant | Scenarios | Answer div. | Retrieval-only | State-only | No div. |
| --- | --- | --- | --- | --- | --- |
| access_count_feedback | 8 | 6 | 1 | 1 | 0 |
| agent_trace_feedback | 8 | 6 | 1 | 1 | 0 |
| cache_materialization_feedback | 8 | 6 | 1 | 1 | 0 |
| explanation_focus_feedback | 8 | 7 | 1 | 0 | 0 |
| pure_baseline | 8 | 0 | 0 | 0 | 8 |
| recency_memory_feedback | 8 | 6 | 1 | 1 | 0 |

Overall top-1 changes: 36. Overall top-k order changes: 36.

## 7. Ablation Results

| Mode | Rows | Answer div. | Any div. |
| --- | --- | --- | --- |
| disabled | 40 | 0 | 0 |
| default | 40 | 31 | 40 |
| strong | 40 | 31 | 40 |

Disabled-feedback ablations remove answer divergences because the latent state updates are not applied when feedback weight is zero. Default and strong settings preserve mechanism-sensitive divergences in the feedback variants.

## 8. Negative Controls

Negative controls stable: 100.00%. See `rag_negative_controls.md` for scenario-level details.

## 9. Replay/Determinism

The full experiment and ablation were run twice and compared as normalized JSON. Deterministic replay passed: True. First hash: `2fe9b40271a8553cc0033c0fdb9fbf204cd8a83f093dab1d45f7291d6706526b`. Second hash: `2fe9b40271a8553cc0033c0fdb9fbf204cd8a83f093dab1d45f7291d6706526b`. Ignored fields: [].

## 10. Mechanism Necessity/Sufficiency

Each feedback variant has a direct mechanism chain from OBS-like operation to latent state field to later ranking feature to answer or context divergence. Zero-feedback ablations disable the ranking feature and remove answer divergences. See `rag_mechanism_checks.md`.

## 11. Relation To The Python Package Evidence

The Python package evidence studies access-induced semantic divergence in concrete library behavior. This RAG-shaped track is not additional real-world prevalence evidence; it is a controlled instantiation showing the same OSDS mechanism in retrieval/session-state form.

## 12. Limitations

This is a deterministic controlled RAG evaluation. It does not test commercial RAG systems, does not claim real-world prevalence, does not use an LLM generator, and does not show speed improvement. The answer extractor simply returns the marked span from the top retrieved document, which isolates retrieval/session-state effects but omits generative uncertainty.

## 13. Manuscript Integration Recommendation

The result is strong enough for a cautious abstract mention and a main-text subsection if framed as a controlled deterministic evaluation with ablation and replay. Detailed scenario tables and traces are better placed in the appendix or artifact supplement.

## 14. Suggested Abstract Sentence

We further instantiate OSDS in a deterministic retrieval-augmented pipeline: across 48 controlled scenarios, observation-shaped preview, logging, explanation, cache-materialization, and tool-trace operations changed later retrieved context or extracted answers in 36 cases, while pure baselines and zero-feedback ablations remained stable.

## 15. Exact Command Log

- `python paper_artifacts/scp_rag_osds_strong_eval/run_rag_strong_eval.py` failed because the workspace `python` launcher was unavailable.
- `python paper_artifacts\scp_rag_osds_strong_eval\run_rag_strong_eval.py` passed.
- `python run_tests.py` passed: 28 passed, 0 failed.
- `python -m pytest tests` passed: 44 passed in 3.29s.
