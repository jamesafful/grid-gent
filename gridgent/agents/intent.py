from __future__ import annotations
from typing import Dict, Any
import re


class IntentAgent:
    """Deterministic intent classifier for demo."""

    def classify(self, query: str) -> Dict[str, Any]:
        text = (query or "").lower().strip()

        smalltalk_tokens = {
            "hi",
            "hello",
            "hey",
            "yo",
            "thanks",
            "thank you",
            "thx",
            "ok",
            "okay",
            "k",
        }
        if text in smalltalk_tokens or text in {"why", "?", "??"} or len(text) <= 2:
            return {
                "intent": "unknown",
                "feeder": None,
                "added_pv_mw": 0.0,
                "added_load_mw": 0.0,
                "has_mw": False,
                "has_feeder": False,
                "has_grid_keywords": False,
            }

        has_mw = bool(re.search(r"(\d+(?:\.\d+)?)\s*mw", text))
        mentions_feeder = any(
            tok in text for tok in ["feeder f1", "feeder f2", "feeder f3", "f1", "f2", "f3", "feeder"]
        )
        grid_keywords = any(
            k in text
            for k in [
                "load",
                "pv",
                "solar",
                "rooftop",
                "substation",
                "transformer",
                "grid",
                "voltage",
                "hosting capacity",
                "hosting",
                "scenario",
                "contingency",
            ]
        )

        if not (has_mw or mentions_feeder or grid_keywords):
            return {
                "intent": "unknown",
                "feeder": None,
                "added_pv_mw": 0.0,
                "added_load_mw": 0.0,
                "has_mw": False,
                "has_feeder": False,
                "has_grid_keywords": False,
            }

        if any(k in text for k in ["host", "hosting capacity", "add pv", "rooftop pv", "solar"]):
            intent = "hosting_capacity"
        elif any(k in text for k in ["explain", "how does"]):
            intent = "explanation"
        elif "why" in text:
            intent = "explanation"
        else:
            intent = "simulation"

        feeder = None
        if "feeder f2" in text or "feeder 2" in text or "f2" in text:
            feeder = "F2"
        elif "feeder f3" in text or "feeder 3" in text or "f3" in text:
            feeder = "F3"
        elif "feeder f1" in text or "feeder 1" in text or "f1" in text:
            feeder = "F1"

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
            "has_mw": has_mw,
            "has_feeder": feeder is not None,
            "has_grid_keywords": grid_keywords,
        }
