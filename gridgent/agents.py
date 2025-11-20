
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Literal, Tuple
from . import tools

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


class IntentAgent:
    def classify(self, query: str) -> Dict[str, Any]:
        text = query.lower()
        if any(k in text for k in ["what if", "simulate", "scenario", "contingency", "impact of"]):
            intent = "simulation"
        elif any(k in text for k in ["host", "hosting capacity", "add pv", "add ev", "der"]):
            intent = "hosting_capacity"
        elif any(k in text for k in ["explain", "why", "how does"]):
            intent = "explanation"
        else:
            intent = "simulation"

        feeder = "F1"
        if "f2" in text or "feeder 2" in text:
            feeder = "F2"
        elif "f3" in text or "feeder 3" in text:
            feeder = "F3"

        added_pv = 0.0
        added_load = 0.0
        import re

        mw_matches = re.findall(r"(\d+(?:\.\d+)?)\s*mw", text)
        if mw_matches:
            value = float(mw_matches[0])
            if "pv" in text or "solar" in text:
                added_pv = value
            else:
                added_load = value

        return {
            "intent": intent,
            "feeder": feeder,
            "added_pv_mw": added_pv,
            "added_load_mw": added_load,
        }


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

        pf_result = tools.run_power_flow_scenario(feeder, added_pv_mw=added_pv, added_load_mw=added_load)
        steps.append(
            Step(
                role="tool",
                content="Ran simplified power-flow scenario.",
                meta=pf_result.to_dict(),
            )
        )

        feeder_meta = tools.get_feeder_summary(feeder)
        steps.append(
            Step(
                role="tool",
                content="Retrieved static feeder metadata.",
                meta=feeder_meta,
            )
        )

        technical_summary = {
            "intent": intent_info["intent"],
            "feeder": feeder,
            "added_pv_mw": added_pv,
            "added_load_mw": added_load,
            "power_flow": pf_result.to_dict(),
            "feeder_meta": feeder_meta,
        }

        return "ok", technical_summary, steps


class NarratorAgent:
    def narrate(self, query: str, technical: Dict[str, Any]) -> str:
        pf = technical["power_flow"]
        meta = technical["feeder_meta"]

        lines: List[str] = []
        lines.append(f"You asked: {query.strip()}")
        lines.append("")
        lines.append(f"Here's what Grid-Gent found for {meta['name']}:")
        lines.append(
            f"- Base peak demand (demo data): {meta['peak_mw']} MW with about {meta['num_customers']} customers."
        )
        lines.append(
            f"- In this scenario, we assumed +{technical['added_load_mw']:.1f} MW of extra load and "
            f"+{technical['added_pv_mw']:.1f} MW of additional PV."
        )
        lines.append("")
        lines.append("Simplified power-flow-style results (demo model):")
        lines.append(f"- Peak loading: {pf['peak_loading_pct']:.1f}% of an approximate rating.")
        lines.append(f"- Minimum voltage: {pf['min_voltage_pu']:.3f} pu")
        lines.append(f"- Maximum voltage: {pf['max_voltage_pu']:.3f} pu")

        if pf["overload_elements"]:
            lines.append("")
            lines.append("Potential issues flagged:")
            for item in pf["overload_elements"]:
                lines.append(f"  • {item}")
        else:
            lines.append("")
            lines.append("No major issues were flagged in this simplified view.")

        lines.append("")
        lines.append(pf["notes"])

        lines.append("")
        lines.append(
            "Note: this is a deliberately simplified demo model. A real deployment would "
            "use your actual network model, load/DER data, and planning criteria, and would "
            "treat these results as advisory, subject to engineer review."
        )

        return "\n".join(lines)
