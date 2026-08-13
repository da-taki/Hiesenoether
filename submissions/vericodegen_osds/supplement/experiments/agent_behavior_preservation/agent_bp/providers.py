from __future__ import annotations

import json
from pathlib import Path

from .cases import render_static_candidate
from .self_assessment import parse_preservation_claim


class ProviderError(RuntimeError):
    pass


class BaseProvider:
    provider = "local"
    model = "base"
    temperature = None
    seed = None
    is_control_provider = False

    def generate(self, task: dict[str, object], prompt: str) -> dict[str, object]:
        raise NotImplementedError


class NoopProvider(BaseProvider):
    model = "noop-preserving"
    is_control_provider = True

    def generate(self, task: dict[str, object], prompt: str) -> dict[str, object]:
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "seed": self.seed,
            "raw_response": "```python\n" + str(task["source_context"]) + "```",
            "agent_claimed_preservation": True,
            "self_assessment": "The code is unchanged, so behavior is preserved.",
            "is_control_provider": True,
        }


class StaticSemanticsBlindProvider(BaseProvider):
    model = "static-semantics-blind-transformer"
    temperature = 0
    seed = 0
    is_control_provider = True

    def generate(self, task: dict[str, object], prompt: str) -> dict[str, object]:
        code = render_static_candidate(task)
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "seed": self.seed,
            "raw_response": "```python\n" + code + "```",
            "agent_claimed_preservation": True,
            "self_assessment": (
                "Yes. The change only simplifies or materializes the nearby operation and keeps the same return shape."
            ),
            "is_control_provider": True,
        }


class JsonlReplayProvider(BaseProvider):
    provider = "jsonl_replay"
    model = "external-replay"

    def __init__(self, path: Path):
        self.path = path
        self.responses = {}
        with path.open(encoding="utf-8-sig") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                self.responses[row["task_id"]] = row

    def generate(self, task: dict[str, object], prompt: str) -> dict[str, object]:
        row = self.responses.get(task["task_id"])
        if row is None:
            raise ProviderError(f"no replay response for {task['task_id']}")
        return {
            "provider": row.get("provider", self.provider),
            "model": row.get("model", self.model),
            "temperature": row.get("temperature"),
            "seed": row.get("seed"),
            "raw_response": row["raw_response"],
            "agent_claimed_preservation": bool(row.get("agent_claimed_preservation", parse_preservation_claim(str(row.get("self_assessment", ""))) == "YES")),
            "self_assessment": row.get("self_assessment", ""),
            "parsed_self_assessment": parse_preservation_claim(str(row.get("self_assessment", ""))),
            "is_control_provider": False,
        }


def make_provider(name: str, replay_path: str | None = None) -> BaseProvider:
    if name == "noop":
        return NoopProvider()
    if name == "static":
        return StaticSemanticsBlindProvider()
    if name == "jsonl":
        if not replay_path:
            raise ProviderError("--replay-path is required for jsonl provider")
        return JsonlReplayProvider(Path(replay_path))
    raise ProviderError(f"unknown provider {name!r}")


