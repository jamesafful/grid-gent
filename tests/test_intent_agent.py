import unittest
from gridgent.agents.intent import IntentAgent


class TestIntentAgent(unittest.TestCase):
    def setUp(self):
        self.agent = IntentAgent()

    def test_hosting_capacity_intent(self):
        info = self.agent.classify("What happens on feeder F2 if we add 5 MW of rooftop PV?")
        self.assertEqual(info["intent"], "hosting_capacity")
        self.assertEqual(info["feeder"], "F2")
        self.assertAlmostEqual(info["added_pv_mw"], 5.0, places=3)

    def test_simulation_intent_load_growth(self):
        info = self.agent.classify("Simulate load growth of 3 MW on feeder F1")
        self.assertEqual(info["intent"], "simulation")
        self.assertEqual(info["feeder"], "F1")
        self.assertAlmostEqual(info["added_load_mw"], 3.0, places=3)


if __name__ == "__main__":
    unittest.main()
