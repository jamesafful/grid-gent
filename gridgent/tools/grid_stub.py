from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List
from pathlib import Path
import json
import csv
import io

_CONFIG_CACHE: Dict[str, Any] | None = None
_BASE_DIR = Path(__file__).resolve().parents[2]


def _default_feeder_config() -> Dict[str, Any]:
    return {
        "feeders": {
            "F1": {
                "name": "Feeder F1 - Downtown Core",
                "base_kv": 13.8,
                "num_customers": 4200,
                "peak_mw": 18.5,
                "pv_mw": 3.2,
            },
            "F2": {
                "name": "Feeder F2 - Residential West",
                "base_kv": 13.8,
                "num_customers": 5100,
                "peak_mw": 14.3,
                "pv_mw": 4.7,
            },
            "F3": {
                "name": "Feeder F3 - Industrial Park",
                "base_kv": 13.8,
                "num_customers": 830,
                "peak_mw": 22.1,
                "pv_mw": 0.8,
            },
        }
    }


def _load_feeder_config() -> Dict[str, Any]:
    """Load feeder configuration with upload override."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    uploaded_path = _BASE_DIR / "config" / "uploaded_feedermodel.json"
    base_path = _BASE_DIR / "config" / "feeders.json"

    if uploaded_path.exists():
        try:
            with uploaded_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "feeders" in data:
                _CONFIG_CACHE = data
                return _CONFIG_CACHE
        except Exception:
            pass

    if base_path.exists():
        try:
            with base_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "feeders" in data:
                _CONFIG_CACHE = data
                return _CONFIG_CACHE
        except Exception:
            pass

    _CONFIG_CACHE = _default_feeder_config()
    return _CONFIG_CACHE


def reload_feeder_config() -> None:
    global _CONFIG_CACHE
    _CONFIG_CACHE = None


def get_feeder_summary(feeder: str) -> Dict[str, Any]:
    feeder_key = (feeder or "").upper().strip()
    cfg = _load_feeder_config()
    feeders = cfg.get("feeders", {})
    if feeder_key and feeder_key in feeders:
        return feeders[feeder_key]
    return {
        "name": f"Feeder {feeder_key or 'F?'} (demo placeholder)",
        "base_kv": 13.8,
        "num_customers": 3000,
        "peak_mw": 10.0,
        "pv_mw": 1.0,
    }


def get_all_feeders() -> Dict[str, Dict[str, Any]]:
    cfg = _load_feeder_config()
    feeders = cfg.get("feeders", {})
    out: Dict[str, Dict[str, Any]] = {}
    for k, v in feeders.items():
        out[str(k).upper()] = v
    return out


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
        feeder=(feeder or "").upper().strip() or "F?",
        peak_loading_pct=peak_loading_pct,
        min_voltage_pu=min_voltage,
        max_voltage_pu=max_voltage,
        overload_elements=overload_elements,
        notes=notes,
    )


def parse_uploaded_grid(raw: str, fmt: str) -> Dict[str, Any]:
    fmt = (fmt or "").lower().strip()
    if fmt not in {"json", "csv"}:
        raise ValueError("Unsupported format; expected 'json' or 'csv'.")

    if fmt == "json":
        try:
            data = json.loads(raw)
        except Exception as exc:
            raise ValueError(f"Invalid JSON: {exc}") from exc

        if isinstance(data, dict) and "feeders" in data and isinstance(data["feeders"], dict):
            feeders_in = data["feeders"]
        elif isinstance(data, list):
            feeders_in = {}
            for row in data:
                if not isinstance(row, dict):
                    raise ValueError("JSON list must contain objects with feeder fields.")
                fid = row.get("feeder_id") or row.get("id") or row.get("name")
                if not fid:
                    raise ValueError("Each feeder row must contain a 'feeder_id' or 'id' or 'name'.")
                feeders_in[str(fid).upper()] = {
                    "name": row.get("name", str(fid)),
                    "base_kv": float(row.get("base_kv", 13.8)),
                    "num_customers": int(row.get("num_customers", 1000)),
                    "peak_mw": float(row.get("peak_mw", 10.0)),
                    "pv_mw": float(row.get("pv_mw", 1.0)),
                }
        else:
            raise ValueError("JSON must be an object with 'feeders' or a list of feeders.")

        feeders_out: Dict[str, Any] = {}
        for k, v in feeders_in.items():
            fid = str(k).upper()
            if not isinstance(v, dict):
                raise ValueError("Each feeder entry must be an object.")
            feeders_out[fid] = {
                "name": v.get("name", fid),
                "base_kv": float(v.get("base_kv", 13.8)),
                "num_customers": int(v.get("num_customers", 1000)),
                "peak_mw": float(v.get("peak_mw", 10.0)),
                "pv_mw": float(v.get("pv_mw", 1.0)),
            }
        if not feeders_out:
            raise ValueError("No feeders found in uploaded JSON.")
        return {"feeders": feeders_out}

    # CSV
    f = io.StringIO(raw)
    reader = csv.DictReader(f)
    required = ["feeder_id", "name", "base_kv", "num_customers", "peak_mw", "pv_mw"]
    if reader.fieldnames is None:
        raise ValueError("CSV appears to have no header.")
    for r in required:
        if r not in reader.fieldnames:
            raise ValueError(f"CSV missing required column '{r}'")

    feeders_out: Dict[str, Any] = {}
    for row in reader:
        fid = row.get("feeder_id")
        if not fid:
            raise ValueError("CSV row missing feeder_id.")
        fid_u = str(fid).upper()
        feeders_out[fid_u] = {
            "name": row.get("name") or fid_u,
            "base_kv": float(row.get("base_kv") or 13.8),
            "num_customers": int(row.get("num_customers") or 1000),
            "peak_mw": float(row.get("peak_mw") or 10.0),
            "pv_mw": float(row.get("pv_mw") or 1.0),
        }

    if not feeders_out:
        raise ValueError("No feeders found in uploaded CSV.")
    return {"feeders": feeders_out}


def save_uploaded_grid(config: Dict[str, Any]) -> None:
    if not isinstance(config, dict) or "feeders" not in config:
        raise ValueError("Uploaded config must be a dict with 'feeders'.")
    path = _BASE_DIR / "config" / "uploaded_feedermodel.json"
    path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    reload_feeder_config()
