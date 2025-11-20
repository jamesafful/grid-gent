
from __future__ import annotations
import uuid
from dataclasses import dataclass
from typing import List, Dict, Any

from .agents import IntentAgent, PlanningAgent, NarratorAgent, Step


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


class GridGentOrchestrator:
    def __init__(self) -> None:
        self.intent_agent = IntentAgent()
        self.planning_agent = PlanningAgent()
        self.narrator_agent = NarratorAgent()

    def run(self, query: str) -> OrchestratorResult:
        task_id = str(uuid.uuid4())
        steps: List[Step] = []

        intent_info = self.intent_agent.classify(query)
        steps.append(
            Step(
                role="intent_agent",
                content=f"Classified intent as '{intent_info['intent']}' and selected feeder {intent_info['feeder']}.",
                meta=intent_info,
            )
        )

        status, technical_summary, planning_steps = self.planning_agent.plan_and_analyze(query, intent_info)
        steps.extend(planning_steps)

        answer = self.narrator_agent.narrate(query, technical_summary)
        steps.append(
            Step(
                role="narrator_agent",
                content="Generated human-readable explanation for operator/planner.",
                meta={},
            )
        )

        return OrchestratorResult(task_id=task_id, answer=answer, steps=steps)
