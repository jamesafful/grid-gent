from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Literal

StepRole = Literal["user", "intent_agent", "planning_agent", "narrator_agent", "tool"]


@dataclass
class Step:
    role: StepRole
    content: str
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "meta": self.meta,
        }


@dataclass
class OrchestratorResult:
    task_id: str
    answer: str
    steps: List[Step]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "answer": self.answer,
            "steps": [s.to_dict() for s in self.steps],
        }
