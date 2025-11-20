from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path
import json

_CONFIG_CACHE: Dict[str, Any] | None = None


def _load_feeder_config() -> Dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    base_dir = Path(__file__).resolve().parents[2]
    cfg_path = base_dir / "config" / "feeders.json"
    default = {
        "feeders": {
            "F1": {
                "name": "Feeder F1 - Downtown Core",
                "base_kv": 13.8,
                "num_customers": 4200,
                "peak_mw": 18.5,
                "pv_mw": 3.2
            },
            "F2": {
                "name": "Feeder F2 - Residential West",
                "base_kv": 13.8,
                "num_customers": 5100,
                "peak_mw": 14.3,
                "pv_mw": 4.7
            },
            "F3": {
                "name": "Feeder F3 - Industrial Park",
                "base_kv": 13.8,
                "num_customers": 830,
                "peak_mw": 22.1,
                "pv_mw": 0.8
            }
        }
    }

    if not cfg_path.exists():
        _CONFIG_CACHE = default
        return _CONFIG_CACHE

    try:
        with cfg_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict) or "feeders" not in data:
                _CONFIG_CACHE = default
            else:
                _CONFIG_CACHE = data
    except Exception:
        _CONFIG_CACHE = default

    return _CONFIG_CACHE


def get_feeder_summary(feeder: str) -> Dict[str, Any]:
    feeder_key = feeder.upper().strip()
    cfg = _load_feeder_config()
    feeders = cfg.get("feeders", {})
    if feeder_key in feeders:
        return feeders[feeder_key]

    return {
        "name": f"Feeder {feeder_key} (demo placeholder)",
        "base_kv": 13.8,
        "num_customers": 3000,
        "peak_mw": 10.0,
        "pv_mw": 1.0,
    }


@dataclass
class PowerFlowResult:
    feeder: str
    peak_loading_pct: float
    min_voltage_pu: float
    max_voltage_pu: float
    overload_elements: List[str]
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feeder": self.feeder,
            "peak_loading_pct": round(self.peak_loading_pct, 1),
            "min_voltage_pu": round(self.min_voltage_pu, 3),
            "max_voltage_pu": round(self.max_voltage_pu, 3),
            "overload_elements": self.overload_elements,
            "notes": self.notes,
        }


def run_power_flow_scenario(
    feeder: str,
    added_pv_mw: float = 0.0,
    added_load_mw: float = 0.0,
) -> PowerFlowResult:
    meta = get_feeder_summary(feeder)
    base_peak = float(meta.get("peak_mw", 10.0))
    base_pv = float(meta.get("pv_mw", 1.0))

    new_peak = base_peak + added_load_mw - 0.5 * added_pv_mw
    if new_peak < 0:
        new_peak = 0.0

    rating_mva = base_peak * 1.2 if base_peak > 0 else 12.0
    peak_loading_pct = 100.0 * (new_peak / rating_mva) if rating_mva > 0 else 0.0

    min_voltage = 0.97 - 0.01 * (added_load_mw / max(base_peak, 1.0))
    max_voltage = 1.03 + 0.01 * (added_pv_mw / max(base_pv, 0.5))

    min_voltage = max(min_voltage, 0.9)
    max_voltage = min(max_voltage, 1.10)

    overload_elements: List[str] = []
    if peak_loading_pct > 100.0:
        overload_elements.append("Main transformer overloaded (demo flag)")
    if peak_loading_pct > 95.0:
        overload_elements.append("Line segments near thermal limit (demo flag)")
    if min_voltage < 0.95:
        overload_elements.append("Low voltage at end-of-line customers (demo flag)")
    if max_voltage > 1.05:
        overload_elements.append("Risk of over-voltage near PV clusters (demo flag)")

    if overload_elements:
        notes = "Potential issues detected; a detailed engineering study is recommended."
    else:
        notes = "Scenario appears within normal operating limits in this simplified model."

    return PowerFlowResult(
        feeder=feeder.upper().strip(),
        peak_loading_pct=peak_loading_pct,
        min_voltage_pu=min_voltage,
        max_voltage_pu=max_voltage,
        overload_elements=overload_elements,
        notes=notes,
    )
