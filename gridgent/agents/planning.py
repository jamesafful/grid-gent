from __future__ import annotations
from typing import Dict, Any, List, Tuple

from gridgent.core.types import Step
from gridgent.tools.grid_stub import run_power_flow_scenario, get_feeder_summary


class PlanningAgent:
    def plan_and_analyze(self, query: str, intent_info: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Step]]:
        feeder = intent_info["feeder"]
        added_pv = float(intent_info.get("added_pv_mw", 0.0))
        added_load = float(intent_info.get("added_load_mw", 0.0))

        steps: List[Step] = []

        summary = (
            f"Analyzing feeder {feeder} with added PV={added_pv:.1f} MW, "
            f"added load={added_load:.1f} MW using a simplified power-flow stub."
        )
        steps.append(Step(role="planning_agent", content=summary, meta={"feeder": feeder}))

        pf_result = run_power_flow_scenario(feeder, added_pv_mw=added_pv, added_load_mw=added_load)
        pf_dict = pf_result.to_dict()
        steps.append(
            Step(
                role="tool",
                content="Ran simplified power-flow scenario (demo).",
                meta=pf_dict,
            )
        )

        feeder_meta = get_feeder_summary(feeder)
        steps.append(
            Step(
                role="tool",
                content="Retrieved static feeder metadata from config.",
                meta=feeder_meta,
            )
        )

        technical_summary: Dict[str, Any] = {
            "intent": intent_info["intent"],
            "feeder": feeder,
            "added_pv_mw": added_pv,
            "added_load_mw": added_load,
            "power_flow": pf_dict,
            "feeder_meta": feeder_meta,
        }

        rating_pct = pf_dict["peak_loading_pct"]
        technical_summary["loading_margin_pct"] = max(0.0, 100.0 - rating_pct)

        return "ok", technical_summary, steps
