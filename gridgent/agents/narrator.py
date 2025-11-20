from __future__ import annotations
from typing import Dict, Any, List


class NarratorAgent:
    def narrate(self, query: str, technical: Dict[str, Any]) -> str:
        pf = technical["power_flow"]
        meta = technical["feeder_meta"]
        intent = technical.get("intent", "simulation")
        loading_margin = float(technical.get("loading_margin_pct", 0.0))

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
        lines.append(f"- Loading margin to 100% (approx): {loading_margin:.1f}% points.")
        lines.append(f"- Minimum voltage: {pf['min_voltage_pu']:.3f} pu")
        lines.append(f"- Maximum voltage: {pf['max_voltage_pu']:.3f} pu")

        if pf["overload_elements"]:
            lines.append("")
            lines.append("Potential issues flagged in this simplified view:")
            for item in pf["overload_elements"]:
                lines.append(f"  • {item}")
        else:
            lines.append("")
            lines.append("No major issues were flagged in this simplified view.")

        if intent == "hosting_capacity":
            lines.append("")
            lines.append(
                "Hosting capacity interpretation (demo-only): In this toy model, we look at loading and "
                "voltage margins as a proxy for how much additional PV the feeder might host. "
                "Here, the approximate loading remains below 100% and voltages stay within about 0.95–1.05 pu, "
                "so the added PV appears acceptable in this simplified analysis. "
                "Real hosting capacity studies must use detailed feeder models, time-series behavior, and utility "
                "planning criteria, and are typically performed by power system engineers."
            )

        lines.append("")
        lines.append(pf["notes"])

        lines.append("")
        lines.append(
            "Important: This is a deliberately simplified demonstration model. A real deployment would "
            "use your actual network model, load/DER data, and planning criteria, and would treat all outputs "
            "as advisory, subject to engineer review and formal studies. Do not use this demo for operational "
            "or investment decisions."
        )

        return "\n".join(lines)
