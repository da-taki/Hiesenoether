from __future__ import annotations

import copy
import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+")

@dataclass(frozen=True)
class Document:
    doc_id: str
    topic_family: str
    title: str
    body: str
    answer_span: str
    tags: tuple[str, ...]
    is_target: bool
    is_close_distractor: bool
    is_observation_boostable: bool

    @property
    def text(self) -> str:
        return f"{self.title} {self.body} {' '.join(self.tags)}"

def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

def load_corpus(path: str | Path) -> list[Document]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [
        Document(
            doc_id=item["doc_id"],
            topic_family=item["topic_family"],
            title=item["title"],
            body=item["body"],
            answer_span=item["answer_span"],
            tags=tuple(item["tags"]),
            is_target=bool(item["is_target"]),
            is_close_distractor=bool(item["is_close_distractor"]),
            is_observation_boostable=bool(item["is_observation_boostable"]),
        )
        for item in raw
    ]

DEFAULT_WEIGHTS = {
    "pure_baseline": 0.0,
    "access_count_feedback": 1.65,
    "recency_memory_feedback": 1.8,
    "explanation_focus_feedback": 0.72,
    "cache_materialization_feedback": 1.65,
    "agent_trace_feedback": 1.75,
    "hybrid_feedback": 0.95,
}

STRONG_WEIGHTS = {
    "pure_baseline": 0.0,
    "access_count_feedback": 3.0,
    "recency_memory_feedback": 3.2,
    "explanation_focus_feedback": 1.25,
    "cache_materialization_feedback": 3.0,
    "agent_trace_feedback": 3.2,
    "hybrid_feedback": 1.75,
}

class RagStrongSimulator:

    def __init__(
        self,
        corpus: Iterable[Document],
        variant: str,
        *,
        feedback_weight: float | None = None,
        top_k: int = 4,
    ) -> None:
        if variant not in DEFAULT_WEIGHTS:
            raise ValueError(f"unknown variant: {variant}")
        self.corpus = list(corpus)
        self.variant = variant
        self.feedback_weight = DEFAULT_WEIGHTS[variant] if feedback_weight is None else feedback_weight
        self.top_k = top_k
        self.doc_tokens = {doc.doc_id: tokenize(doc.text) for doc in self.corpus}
        self.doc_token_counts = {doc_id: Counter(tokens) for doc_id, tokens in self.doc_tokens.items()}
        self.doc_token_sets = {doc_id: set(tokens) for doc_id, tokens in self.doc_tokens.items()}
        self.idf = self._build_idf()
        self.access_counts: dict[str, int] = {doc.doc_id: 0 for doc in self.corpus}
        self.session_memory: list[str] = []
        self.focus_terms: list[str] = []
        self.materialized_cache: set[str] = set()
        self.tool_trace: dict[str, list[str]] = {}
        self.trace_queries: list[str] = []
        self.memory_inspections = 0
        self.event_log: list[dict[str, Any]] = []

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        topk = self._rank(query)
        touched = self._apply_retrieval_feedback(topk)
        self._emit_event(
            "retrieve",
            "read",
            query=query,
            topk=topk,
            answer_span=None,
            touched=touched,
        )
        return copy.deepcopy(topk)

    def answer(self, query: str) -> dict[str, Any]:
        topk = self._rank(query)
        answer_span = topk[0]["answer_span"] if topk else ""
        touched = self._apply_retrieval_feedback(topk)
        self._emit_event(
            "answer",
            "answer",
            query=query,
            topk=topk,
            answer_span=answer_span,
            touched=touched,
        )
        return {"query": query, "topk": copy.deepcopy(topk), "answer": answer_span}

    def preview_context(self, query: str) -> list[dict[str, Any]]:
        topk = self._rank(query)
        touched = self._apply_observation_feedback("preview_context", query, topk)
        self._emit_event(
            "preview_context",
            "observation",
            query=query,
            topk=topk,
            answer_span=None,
            touched=touched,
        )
        return copy.deepcopy(topk)

    def log_retrieval(self, query: str) -> dict[str, Any]:
        topk = self._rank(query)
        touched = self._apply_observation_feedback("log_retrieval", query, topk)
        self._emit_event(
            "log_retrieval",
            "diagnostic",
            query=query,
            topk=topk,
            answer_span=None,
            touched=touched,
        )
        return {"query": query, "topk": [item["doc_id"] for item in topk]}

    def explain_retrieval(self, query: str) -> dict[str, Any]:
        topk = self._rank(query)
        touched = self._apply_observation_feedback("explain_retrieval", query, topk)
        explanation = {
            "query_terms": sorted(set(tokenize(query))),
            "retrieved_doc_ids": [item["doc_id"] for item in topk],
            "stored_focus_terms": list(self.focus_terms),
        }
        self._emit_event(
            "explain_retrieval",
            "explanation",
            query=query,
            topk=topk,
            answer_span=None,
            touched=touched,
        )
        return explanation

    def inspect_memory(self) -> dict[str, Any]:
        touched: list[str] = []
        if self.feedback_weight != 0 and self.variant in {"recency_memory_feedback", "hybrid_feedback"}:
            self.memory_inspections += 1
            touched.append("memory_inspections")
        self._emit_event(
            "inspect_memory",
            "diagnostic",
            query=None,
            topk=[],
            answer_span=None,
            touched=touched,
        )
        return self.state_snapshot()

    def trace_tool_call(self, tool_name: str, query: str) -> dict[str, Any]:
        topk = self._rank(query)
        touched = self._apply_tool_trace_feedback(tool_name, query, topk)
        self._emit_event(
            "trace_tool_call",
            "tool_trace",
            query=query,
            topk=topk,
            answer_span=None,
            touched=touched,
            extra={"tool_name": tool_name},
        )
        return {"tool_name": tool_name, "query": query, "topk": [item["doc_id"] for item in topk]}

    def materialize_context_cache(self, query: str) -> dict[str, Any]:
        topk = self._rank(query)
        touched = self._apply_observation_feedback("materialize_context_cache", query, topk)
        self._emit_event(
            "materialize_context_cache",
            "diagnostic",
            query=query,
            topk=topk,
            answer_span=None,
            touched=touched,
        )
        return {"query": query, "cached_doc_ids": sorted(self.materialized_cache)}

    def state_snapshot(self) -> dict[str, Any]:
        nonzero_access = {key: value for key, value in sorted(self.access_counts.items()) if value}
        nonempty_trace = {key: list(value) for key, value in sorted(self.tool_trace.items()) if value}
        return {
            "variant": self.variant,
            "feedback_weight": self.feedback_weight,
            "access_counts": nonzero_access,
            "session_memory": list(self.session_memory),
            "focus_terms": list(self.focus_terms),
            "materialized_cache": sorted(self.materialized_cache),
            "tool_trace": nonempty_trace,
            "trace_queries": list(self.trace_queries),
            "memory_inspections": self.memory_inspections,
        }

    def trace(self) -> list[dict[str, Any]]:
        return copy.deepcopy(self.event_log)

    def _build_idf(self) -> dict[str, float]:
        df: Counter[str] = Counter()
        for tokens in self.doc_tokens.values():
            df.update(set(tokens))
        total = len(self.corpus)
        return {term: math.log((total + 1) / (count + 0.5)) + 1.0 for term, count in df.items()}

    def _rank(self, query: str) -> list[dict[str, Any]]:
        rows = []
        for doc in self.corpus:
            lexical = self._lexical_score(query, doc)
            feedback_parts = self._feedback_score(query, doc)
            total_feedback = sum(feedback_parts.values())
            total = lexical + total_feedback
            rows.append((-total, -lexical, doc.doc_id, doc, lexical, feedback_parts))
        rows.sort()
        return [
            {
                "doc_id": doc.doc_id,
                "topic_family": doc.topic_family,
                "title": doc.title,
                "score": round(lexical + sum(feedback_parts.values()), 6),
                "lexical_score": round(lexical, 6),
                "feedback_score": round(sum(feedback_parts.values()), 6),
                "feedback_parts": {key: round(value, 6) for key, value in feedback_parts.items() if value},
                "answer_span": doc.answer_span,
                "tags": list(doc.tags),
            }
            for _, _, _, doc, lexical, feedback_parts in rows[: self.top_k]
        ]

    def _lexical_score(self, query: str, doc: Document) -> float:
        q_counts = Counter(tokenize(query))
        if not q_counts:
            return 0.0
        d_counts = self.doc_token_counts[doc.doc_id]
        title_tokens = set(tokenize(doc.title))
        score = 0.0
        for term, q_count in q_counts.items():
            tf = min(d_counts.get(term, 0), 3)
            if tf == 0:
                continue
            score += min(q_count, 2) * tf * self.idf.get(term, 1.0)
            if term in title_tokens:
                score += 0.18
        return score

    def _feedback_score(self, query: str, doc: Document) -> dict[str, float]:
        if self.feedback_weight == 0 or self.variant == "pure_baseline":
            return {}
        scores: dict[str, float] = {}
        doc_id = doc.doc_id
        tokens = self.doc_token_sets[doc_id]
        if self.variant in {"access_count_feedback", "hybrid_feedback"}:
            if self.access_counts[doc_id]:
                weight = self.feedback_weight if self.variant == "access_count_feedback" else self.feedback_weight * 0.65
                scores["access_count_boost"] = weight * self.access_counts[doc_id]
        if self.variant in {"recency_memory_feedback", "hybrid_feedback"}:
            if doc_id in self.session_memory:
                newest_position = len(self.session_memory) - 1 - self.session_memory[::-1].index(doc_id)
                recency_boost = 1.0 + newest_position / max(len(self.session_memory), 1)
                weight = self.feedback_weight if self.variant == "recency_memory_feedback" else self.feedback_weight * 0.55
                scores["recency_memory_boost"] = weight * recency_boost
        if self.variant in {"explanation_focus_feedback", "hybrid_feedback"}:
            overlap = set(self.focus_terms) & tokens
            if overlap:
                weight = self.feedback_weight if self.variant == "explanation_focus_feedback" else self.feedback_weight * 0.45
                scores["focus_term_boost"] = weight * len(overlap)
        if self.variant in {"cache_materialization_feedback", "hybrid_feedback"}:
            if doc_id in self.materialized_cache:
                weight = self.feedback_weight if self.variant == "cache_materialization_feedback" else self.feedback_weight * 0.55
                scores["cache_presence_boost"] = weight
        if self.variant in {"agent_trace_feedback", "hybrid_feedback"}:
            traced_docs = {item for values in self.tool_trace.values() for item in values}
            if doc_id in traced_docs:
                weight = self.feedback_weight if self.variant == "agent_trace_feedback" else self.feedback_weight * 0.5
                scores["tool_trace_boost"] = weight
        return scores

    def _apply_retrieval_feedback(self, topk: list[dict[str, Any]]) -> list[str]:
        if self.feedback_weight == 0 or self.variant == "pure_baseline":
            return []
        top_doc_ids = [item["doc_id"] for item in topk[:1]]
        touched: list[str] = []
        if self.variant in {"access_count_feedback", "hybrid_feedback"}:
            for doc_id in top_doc_ids:
                self.access_counts[doc_id] += 1
            touched.append("access_counts")
        if self.variant in {"recency_memory_feedback", "hybrid_feedback"}:
            self.session_memory.extend(top_doc_ids)
            touched.append("session_memory")
        if self.variant in {"cache_materialization_feedback", "hybrid_feedback"}:
            self.materialized_cache.update(top_doc_ids)
            touched.append("materialized_cache")
        return touched

    def _apply_observation_feedback(self, operation: str, query: str, topk: list[dict[str, Any]]) -> list[str]:
        if self.feedback_weight == 0 or self.variant == "pure_baseline":
            return []
        top_doc_ids = [item["doc_id"] for item in topk[:1]]
        touched: list[str] = []
        if self.variant in {"access_count_feedback", "hybrid_feedback"} and operation in {
            "preview_context",
            "log_retrieval",
        }:
            for doc_id in top_doc_ids:
                self.access_counts[doc_id] += 1
            touched.append("access_counts")
        if self.variant in {"recency_memory_feedback", "hybrid_feedback"} and operation in {
            "preview_context",
            "log_retrieval",
        }:
            self.session_memory.extend(top_doc_ids)
            touched.append("session_memory")
        if self.variant in {"explanation_focus_feedback", "hybrid_feedback"} and operation == "explain_retrieval":
            focus = set(tokenize(query))
            for item in topk[:1]:
                doc = self._doc(item["doc_id"])
                focus.update(doc.tags)
                focus.update(tokenize(doc.title))
            for term in sorted(focus):
                if term not in self.focus_terms:
                    self.focus_terms.append(term)
            touched.append("focus_terms")
        if self.variant in {"cache_materialization_feedback", "hybrid_feedback"} and operation in {
            "preview_context",
            "log_retrieval",
            "materialize_context_cache",
        }:
            self.materialized_cache.update(top_doc_ids)
            touched.append("materialized_cache")
        return touched

    def _apply_tool_trace_feedback(self, tool_name: str, query: str, topk: list[dict[str, Any]]) -> list[str]:
        if self.feedback_weight == 0 or self.variant not in {"agent_trace_feedback", "hybrid_feedback"}:
            return []
        top_doc_ids = [item["doc_id"] for item in topk[:1]]
        self.tool_trace.setdefault(tool_name, []).extend(top_doc_ids)
        self.trace_queries.append(query)
        return ["tool_trace", "trace_queries"]

    def _emit_event(
        self,
        operation: str,
        apparent_role: str,
        *,
        query: str | None,
        topk: list[dict[str, Any]],
        answer_span: str | None,
        touched: list[str],
        extra: dict[str, Any] | None = None,
    ) -> None:
        event = {
            "sequence": len(self.event_log) + 1,
            "operation": operation,
            "apparent_role": apparent_role,
            "query": query,
            "mutates_latent_state": bool(touched),
            "latent_state_fields_touched": touched,
            "later_ranking_features_affected": self._ranking_features_for_state(touched),
            "retrieved_doc_ids": [item["doc_id"] for item in topk],
            "answer_span": answer_span,
        }
        if extra:
            event.update(extra)
        self.event_log.append(event)

    def _ranking_features_for_state(self, touched: list[str]) -> list[str]:
        mapping = {
            "access_counts": "access_count_boost",
            "session_memory": "recency_memory_boost",
            "focus_terms": "focus_term_boost",
            "materialized_cache": "cache_presence_boost",
            "tool_trace": "tool_trace_boost",
            "trace_queries": "tool_trace_boost",
            "memory_inspections": "none_for_answer_query",
        }
        features = []
        for field in touched:
            feature = mapping.get(field, "unknown")
            if feature not in features:
                features.append(feature)
        return features

    def _doc(self, doc_id: str) -> Document:
        for doc in self.corpus:
            if doc.doc_id == doc_id:
                return doc
        raise KeyError(doc_id)

def run_order(
    corpus: list[Document],
    scenario: dict[str, Any],
    *,
    feedback_weight: float | None,
    order: str,
) -> dict[str, Any]:
    simulator = RagStrongSimulator(corpus, scenario["variant"], feedback_weight=feedback_weight)
    steps: list[dict[str, Any]] = []
    if order == "B":
        for step in scenario["order_B_steps"]:
            if step["operation"] == "answer":
                continue
            result = _run_step(simulator, step)
            steps.append({"operation": step["operation"], "result": result})
    answer_step = {"operation": "answer", "query": scenario["q2_answer_query"]}
    result = _run_step(simulator, answer_step)
    steps.append({"operation": "answer", "result": result})
    return {
        "steps": steps,
        "topk": [item["doc_id"] for item in result["topk"]],
        "topk_details": result["topk"],
        "answer": result["answer"],
        "state": simulator.state_snapshot(),
        "osds_trace": simulator.trace(),
    }

def run_scenario(
    corpus: list[Document],
    scenario: dict[str, Any],
    *,
    feedback_weight: float | None = None,
) -> dict[str, Any]:
    order_a = run_order(corpus, scenario, feedback_weight=feedback_weight, order="A")
    order_b = run_order(corpus, scenario, feedback_weight=feedback_weight, order="B")
    top1_changed = order_a["topk"][:1] != order_b["topk"][:1]
    topk_order_changed = order_a["topk"] != order_b["topk"]
    answer_changed = order_a["answer"] != order_b["answer"]
    state_changed = order_a["state"] != order_b["state"]
    if answer_changed:
        classification = "confirmed_answer_divergence"
    elif topk_order_changed:
        classification = "confirmed_retrieval_order_divergence"
    elif state_changed:
        classification = "confirmed_state_only_divergence"
    else:
        classification = "no_divergence"
    return {
        "scenario_id": scenario["scenario_id"],
        "topic_family": scenario["topic_family"],
        "variant": scenario["variant"],
        "observation_operation": scenario["observation_operation"],
        "q1": scenario["q1_observation_query"],
        "q2": scenario["q2_answer_query"],
        "order_A_top1": order_a["topk"][0] if order_a["topk"] else "",
        "order_B_top1": order_b["topk"][0] if order_b["topk"] else "",
        "order_A_topk": order_a["topk"],
        "order_B_topk": order_b["topk"],
        "order_A_topk_details": order_a["topk_details"],
        "order_B_topk_details": order_b["topk_details"],
        "order_A_answer": order_a["answer"],
        "order_B_answer": order_b["answer"],
        "top1_changed": top1_changed,
        "topk_order_changed": topk_order_changed,
        "answer_changed": answer_changed,
        "state_changed": state_changed,
        "osds_trace_A": order_a["osds_trace"],
        "osds_trace_B": order_b["osds_trace"],
        "state_A": order_a["state"],
        "state_B": order_b["state"],
        "classification": classification,
        "expected_mechanism": scenario["expected_mechanism"],
        "negative_control": scenario["negative_control"],
        "intended_target_doc": scenario["intended_target_doc"],
        "possible_flipped_doc": scenario["possible_flipped_doc"],
    }

def _run_step(simulator: RagStrongSimulator, step: dict[str, Any]) -> Any:
    operation = step["operation"]
    if operation == "trace_tool_call":
        return simulator.trace_tool_call(step.get("tool_name", "retriever"), step["query"])
    if operation == "inspect_memory":
        return simulator.inspect_memory()
    method = getattr(simulator, operation)
    return method(step["query"])
