from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    body: str
    answer_span: str
    tags: tuple[str, ...]

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
            title=item["title"],
            body=item["body"],
            answer_span=item["answer_span"],
            tags=tuple(item["tags"]),
        )
        for item in raw
    ]


class RagSimulator:
    """Small deterministic RAG simulator for observation-shaped state tests."""

    def __init__(
        self,
        corpus: Iterable[Document],
        variant: str,
        *,
        feedback_weight: float | None = None,
        top_k: int = 2,
    ) -> None:
        self.corpus = list(corpus)
        self.variant = variant
        self.top_k = top_k
        self.doc_tokens = {doc.doc_id: set(tokenize(doc.text)) for doc in self.corpus}
        default_weights = {
            "pure_baseline": 0.0,
            "access_count_feedback": 1.25,
            "recency_memory_feedback": 1.75,
            "explanation_feedback": 1.5,
            "cache_materialization_feedback": 1.25,
        }
        self.feedback_weight = default_weights[variant] if feedback_weight is None else feedback_weight
        self.access_counts = {doc.doc_id: 0 for doc in self.corpus}
        self.session_memory: list[str] = []
        self.focus_terms: list[str] = []
        self.materialized_cache: set[str] = set()
        self.query_history: list[str] = []
        self.event_log: list[dict[str, Any]] = []

    def _lexical_score(self, query: str, doc: Document) -> float:
        q_tokens = set(tokenize(query))
        if not q_tokens:
            return 0.0
        overlap = q_tokens & self.doc_tokens[doc.doc_id]
        title_tokens = set(tokenize(doc.title))
        title_bonus = 0.15 * len(overlap & title_tokens)
        return float(len(overlap)) + title_bonus

    def _feedback_score(self, query: str, doc: Document) -> float:
        if self.feedback_weight == 0:
            return 0.0
        if self.variant == "access_count_feedback":
            return self.feedback_weight * self.access_counts[doc.doc_id]
        if self.variant == "recency_memory_feedback":
            if doc.doc_id in self.session_memory:
                recency_index = len(self.session_memory) - 1 - self.session_memory[::-1].index(doc.doc_id)
                return self.feedback_weight * (1.0 + recency_index / 10.0)
            return 0.0
        if self.variant == "explanation_feedback":
            focus = set(self.focus_terms)
            return self.feedback_weight * len(focus & self.doc_tokens[doc.doc_id])
        if self.variant == "cache_materialization_feedback":
            return self.feedback_weight if doc.doc_id in self.materialized_cache else 0.0
        return 0.0

    def _score(self, query: str, doc: Document) -> dict[str, float]:
        lexical = self._lexical_score(query, doc)
        feedback = self._feedback_score(query, doc)
        return {"lexical": lexical, "feedback": feedback, "total": lexical + feedback}

    def retrieve(self, query: str, *, mutate: bool = True) -> list[dict[str, Any]]:
        scored = []
        for doc in self.corpus:
            parts = self._score(query, doc)
            scored.append((-(parts["total"]), -parts["lexical"], doc.doc_id, doc, parts))
        scored.sort()
        results = [
            {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "score": round(parts["total"], 4),
                "lexical_score": round(parts["lexical"], 4),
                "feedback_score": round(parts["feedback"], 4),
                "answer_span": doc.answer_span,
            }
            for _, _, _, doc, parts in scored[: self.top_k]
        ]
        if mutate:
            self._after_retrieval(query, results, source="retrieve")
        return results

    def answer(self, query: str) -> dict[str, Any]:
        topk = self.retrieve(query, mutate=True)
        answer = topk[0]["answer_span"] if topk else ""
        result = {"query": query, "topk": topk, "answer": answer}
        self.event_log.append({"event": "answer", "query": query, "answer": answer})
        return result

    def preview_context(self, query: str) -> list[dict[str, Any]]:
        topk = self.retrieve(query, mutate=False)
        if self.feedback_weight != 0:
            observed = topk[:1]
            if self.variant == "access_count_feedback":
                self._increment_access(observed)
            elif self.variant == "recency_memory_feedback":
                self._remember(observed)
            elif self.variant == "cache_materialization_feedback":
                self.materialized_cache.update(item["doc_id"] for item in observed)
            if self.variant != "pure_baseline":
                self.query_history.append(query)
        if self.variant != "pure_baseline":
            self.event_log.append({"event": "preview_context", "query": query, "topk": [item["doc_id"] for item in topk]})
        return copy.deepcopy(topk)

    def log_retrieval(self, query: str) -> dict[str, Any]:
        topk = self.retrieve(query, mutate=False)
        if self.feedback_weight != 0:
            observed = topk[:1]
            if self.variant == "access_count_feedback":
                self._increment_access(observed)
            elif self.variant == "cache_materialization_feedback":
                self.materialized_cache.update(item["doc_id"] for item in observed)
        record = {"query": query, "topk": [item["doc_id"] for item in topk]}
        if self.feedback_weight != 0 and self.variant != "pure_baseline":
            self.query_history.append(query)
            self.event_log.append({"event": "log_retrieval", **record})
        return record

    def explain_retrieval(self, query: str) -> dict[str, Any]:
        topk = self.retrieve(query, mutate=False)
        q_tokens = tokenize(query)
        if self.feedback_weight != 0 and self.variant == "explanation_feedback":
            for token in q_tokens:
                if token not in self.focus_terms:
                    self.focus_terms.append(token)
            for item in topk[:1]:
                doc = self._doc(item["doc_id"])
                for tag in doc.tags:
                    if tag not in self.focus_terms:
                        self.focus_terms.append(tag)
        explanation = {
            "query": query,
            "topk": [item["doc_id"] for item in topk],
            "focus_terms": list(self.focus_terms),
        }
        if self.feedback_weight != 0 and self.variant != "pure_baseline":
            self.query_history.append(query)
            self.event_log.append({"event": "explain_retrieval", **explanation})
        return explanation

    def inspect_memory(self) -> dict[str, Any]:
        if self.feedback_weight != 0 and self.variant == "recency_memory_feedback" and self.session_memory:
            # Inspection is observational-looking but refreshes recency.
            last = self.session_memory[-1]
            self.session_memory.append(last)
        snapshot = self.state_snapshot()
        if self.feedback_weight != 0 and self.variant != "pure_baseline":
            self.event_log.append({"event": "inspect_memory"})
        return snapshot

    def state_snapshot(self) -> dict[str, Any]:
        return {
            "variant": self.variant,
            "feedback_weight": self.feedback_weight,
            "access_counts": dict(self.access_counts),
            "session_memory": list(self.session_memory),
            "focus_terms": list(self.focus_terms),
            "materialized_cache": sorted(self.materialized_cache),
            "query_history": list(self.query_history),
        }

    def _after_retrieval(self, query: str, topk: list[dict[str, Any]], *, source: str) -> None:
        if self.feedback_weight == 0:
            self.query_history.append(query)
            self.event_log.append({"event": source, "query": query, "topk": [item["doc_id"] for item in topk]})
            return
        if self.variant == "access_count_feedback":
            self._increment_access(topk)
        elif self.variant == "recency_memory_feedback":
            self._remember(topk)
        elif self.variant == "cache_materialization_feedback" and source == "retrieve":
            self.materialized_cache.update(item["doc_id"] for item in topk)
        self.query_history.append(query)
        self.event_log.append({"event": source, "query": query, "topk": [item["doc_id"] for item in topk]})

    def _increment_access(self, topk: list[dict[str, Any]]) -> None:
        for item in topk:
            self.access_counts[item["doc_id"]] += 1

    def _remember(self, topk: list[dict[str, Any]]) -> None:
        for item in topk:
            self.session_memory.append(item["doc_id"])

    def _doc(self, doc_id: str) -> Document:
        for doc in self.corpus:
            if doc.doc_id == doc_id:
                return doc
        raise KeyError(doc_id)


def run_order(
    corpus: list[Document],
    scenario: dict[str, Any],
    *,
    feedback_weight: float | None = None,
    order: str,
) -> dict[str, Any]:
    simulator = RagSimulator(corpus, scenario["variant"], feedback_weight=feedback_weight)
    steps: list[dict[str, Any]] = []
    if order == "B":
        op = scenario["observation_operation"]
        q1 = scenario["q1"]
        observation = getattr(simulator, op)(q1)
        steps.append({"operation": op, "query": q1, "result": observation})
    result = simulator.answer(scenario["q2"])
    steps.append({"operation": "answer", "query": scenario["q2"], "result": result})
    return {
        "steps": steps,
        "topk": [item["doc_id"] for item in result["topk"]],
        "answer": result["answer"],
        "state": simulator.state_snapshot(),
    }


def compare_orders(order_a: dict[str, Any], order_b: dict[str, Any]) -> dict[str, Any]:
    top1_changed = (order_a["topk"][0] if order_a["topk"] else None) != (order_b["topk"][0] if order_b["topk"] else None)
    topk_order_changed = order_a["topk"] != order_b["topk"]
    answer_changed = order_a["answer"] != order_b["answer"]
    state_changed = order_a["state"] != order_b["state"]
    if answer_changed:
        classification = "confirmed_answer_divergence"
    elif top1_changed or topk_order_changed:
        classification = "confirmed_retrieval_order_divergence"
    elif state_changed:
        classification = "confirmed_state_only_divergence"
    else:
        classification = "no_divergence"
    return {
        "top1_changed": top1_changed,
        "topk_order_changed": topk_order_changed,
        "answer_changed": answer_changed,
        "state_changed": state_changed,
        "classification": classification,
    }


def run_scenario(corpus: list[Document], scenario: dict[str, Any], *, feedback_weight: float | None = None) -> dict[str, Any]:
    order_a = run_order(corpus, scenario, feedback_weight=feedback_weight, order="A")
    order_b = run_order(corpus, scenario, feedback_weight=feedback_weight, order="B")
    comparison = compare_orders(order_a, order_b)
    return {
        "scenario_id": scenario["scenario_id"],
        "variant": scenario["variant"],
        "observation_operation": scenario["observation_operation"],
        "q1": scenario["q1"],
        "q2": scenario["q2"],
        "order_A_steps": ["answer(Q2)"],
        "order_B_steps": [f"{scenario['observation_operation']}(Q1)", "answer(Q2)"],
        "expected_possible_flip_reason": scenario["expected_possible_flip_reason"],
        "order_A_topk": order_a["topk"],
        "order_B_topk": order_b["topk"],
        "order_A_answer": order_a["answer"],
        "order_B_answer": order_b["answer"],
        "state_A": order_a["state"],
        "state_B": order_b["state"],
        **comparison,
    }
