import unittest
from gridgent.core.orchestrator import GridGentOrchestrator


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.orch = GridGentOrchestrator()

    def test_run_basic_query(self):
        result = self.orch.run("What happens on feeder F2 if we add 5 MW of rooftop PV?")
        self.assertTrue(result.task_id)
        self.assertIn("You asked:", result.answer)
        roles = [s.role for s in result.steps]
        self.assertEqual(roles[0], "intent_agent")
        self.assertIn("planning_agent", roles)
        self.assertIn("narrator_agent", roles)

    def test_run_unknown_query(self):
        result = self.orch.run("hi")
        self.assertIn("didn't see enough detail", result.answer.lower())


if __name__ == "__main__":
    unittest.main()
