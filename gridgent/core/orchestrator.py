from __future__ import annotations
import uuid
from typing import List

from gridgent.core.types import Step, OrchestratorResult
from gridgent.agents.intent import IntentAgent
from gridgent.agents.planning import PlanningAgent
from gridgent.agents.narrator import NarratorAgent


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
                content=(
                    f"Classified intent as '{intent_info['intent']}' and selected feeder "
                    f"{intent_info['feeder']}."
                ),
                meta=intent_info,
            )
        )

        status, technical_summary, planning_steps = self.planning_agent.plan_and_analyze(query, intent_info)
        steps.extend(planning_steps)

        answer = self.narrator_agent.narrate(query, technical_summary)
        steps.append(
            Step(
                role="narrator_agent",
                content="Generated human-readable explanation for planner/operator.",
                meta={},
            )
        )

        return OrchestratorResult(task_id=task_id, answer=answer, steps=steps)
