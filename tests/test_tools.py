import unittest
from gridgent.tools.grid_stub import run_power_flow_scenario, get_feeder_summary


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


if __name__ == "__main__":
    unittest.main()
