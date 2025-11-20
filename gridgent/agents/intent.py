from __future__ import annotations
from typing import Dict, Any
import re


class IntentAgent:
    def classify(self, query: str) -> Dict[str, Any]:
        text = query.lower()

        if any(k in text for k in ["what if", "simulate", "scenario", "contingency", "impact of"]):
            intent = "simulation"
        elif any(k in text for k in ["host", "hosting capacity", "add pv", "rooftop pv", "solar"]):
            intent = "hosting_capacity"
        elif any(k in text for k in ["explain", "why", "how does"]):
            intent = "explanation"
        else:
            intent = "simulation"

        feeder = "F1"
        if "feeder f2" in text or "feeder 2" in text or "f2" in text:
            feeder = "F2"
        elif "feeder f3" in text or "feeder 3" in text or "f3" in text:
            feeder = "F3"

        added_pv = 0.0
        added_load = 0.0

        mw_matches = re.findall(r"(\d+(?:\.\d+)?)\s*mw", text)
        if mw_matches:
            value = float(mw_matches[0])
            if "pv" in text or "solar" in text or "rooftop" in text:
                added_pv = value
            else:
                added_load = value

        return {
            "intent": intent,
            "feeder": feeder,
            "added_pv_mw": added_pv,
            "added_load_mw": added_load,
        }
