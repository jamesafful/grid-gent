import unittest
from gridgent.tools.grid_stub import (
    run_power_flow_scenario,
    get_feeder_summary,
    parse_uploaded_grid,
    save_uploaded_grid,
    reload_feeder_config,
    get_all_feeders,
)
from pathlib import Path
import json


class TestTools(unittest.TestCase):
    def test_feeder_summary_exists(self):
        meta = get_feeder_summary("F1")
        self.assertIn("peak_mw", meta)
        self.assertGreater(meta["peak_mw"], 0)

    def test_power_flow_baseline(self):
        result = run_power_flow_scenario("F1", added_pv_mw=0.0, added_load_mw=0.0)
        self.assertIsInstance(result.peak_loading_pct, float)
        self.assertGreater(result.peak_loading_pct, 0)
        self.assertGreaterEqual(result.min_voltage_pu, 0.9)
        self.assertLessEqual(result.max_voltage_pu, 1.1)

    def test_power_flow_high_load_flags_issue(self):
        result = run_power_flow_scenario("F1", added_pv_mw=0.0, added_load_mw=20.0)
        self.assertTrue(any("overloaded" in x.lower() for x in result.overload_elements))

    def test_parse_uploaded_json(self):
        raw = json.dumps({
            "feeders": {
                "X1": {"name": "Custom Feeder", "base_kv": 11.0, "num_customers": 100, "peak_mw": 5.0, "pv_mw": 0.5}
            }
        })
        cfg = parse_uploaded_grid(raw, "json")
        self.assertIn("feeders", cfg)
        self.assertIn("X1", cfg["feeders"])

    def test_parse_uploaded_csv(self):
        raw = "feeder_id,name,base_kv,num_customers,peak_mw,pv_mw\n"               "Y1,Feeder Y1,13.8,200,8.0,1.2\n"
        cfg = parse_uploaded_grid(raw, "csv")
        self.assertIn("Y1", cfg["feeders"])

    def test_save_uploaded_overrides(self):
        raw = json.dumps({
            "feeders": {
                "Z1": {"name": "Uploaded Feeder Z1", "base_kv": 13.8, "num_customers": 999, "peak_mw": 50.0, "pv_mw": 5.0}
            }
        })
        cfg = parse_uploaded_grid(raw, "json")
        save_uploaded_grid(cfg)
        reload_feeder_config()
        feeders = get_all_feeders()
        self.assertIn("Z1", feeders)
        meta = get_feeder_summary("Z1")
        self.assertEqual(meta["peak_mw"], 50.0)
        # Clean up uploaded file
        base_dir = Path(__file__).resolve().parents[1]
        up = base_dir / "config" / "uploaded_feedermodel.json"
        if up.exists():
            up.unlink()
        reload_feeder_config()


if __name__ == "__main__":
    unittest.main()
