# RAG Strong Evaluation Mechanism Checks

## access_count_feedback

- Latent state mutated: `access_counts`.
- Later ranking feature: `access_count_boost`.
- Positive scenario: `access_count_feedback_01_answer_flip` changed `LRU` to `LRI`.
- Zero-feedback ablation: `no_divergence` with `answer_changed=False`.
- OSDS chain: OBS-like operation updates latent state, then the later ANSWER read consumes that state through a ranking feature.
- Mechanism disabled removes answer divergence: True.

## recency_memory_feedback

- Latent state mutated: `session_memory`.
- Later ranking feature: `recency_memory_boost`.
- Positive scenario: `recency_memory_feedback_01_answer_flip` changed `LRU` to `LRI`.
- Zero-feedback ablation: `no_divergence` with `answer_changed=False`.
- OSDS chain: OBS-like operation updates latent state, then the later ANSWER read consumes that state through a ranking feature.
- Mechanism disabled removes answer divergence: True.

## explanation_focus_feedback

- Latent state mutated: `focus_terms`.
- Later ranking feature: `focus_term_boost`.
- Positive scenario: `explanation_focus_feedback_01_answer_flip` changed `LRU` to `LRI`.
- Zero-feedback ablation: `no_divergence` with `answer_changed=False`.
- OSDS chain: OBS-like operation updates latent state, then the later ANSWER read consumes that state through a ranking feature.
- Mechanism disabled removes answer divergence: True.

## cache_materialization_feedback

- Latent state mutated: `materialized_cache`.
- Later ranking feature: `cache_presence_boost`.
- Positive scenario: `cache_materialization_feedback_01_answer_flip` changed `LRU` to `LRI`.
- Zero-feedback ablation: `no_divergence` with `answer_changed=False`.
- OSDS chain: OBS-like operation updates latent state, then the later ANSWER read consumes that state through a ranking feature.
- Mechanism disabled removes answer divergence: True.

## agent_trace_feedback

- Latent state mutated: `tool_trace`.
- Later ranking feature: `tool_trace_boost`.
- Positive scenario: `agent_trace_feedback_01_answer_flip` changed `LRU` to `LRI`.
- Zero-feedback ablation: `no_divergence` with `answer_changed=False`.
- OSDS chain: OBS-like operation updates latent state, then the later ANSWER read consumes that state through a ranking feature.
- Mechanism disabled removes answer divergence: True.

