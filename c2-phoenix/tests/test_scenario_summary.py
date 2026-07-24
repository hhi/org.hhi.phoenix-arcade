import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "tools" / "summarize_semantic_scenario.py"
SPEC = importlib.util.spec_from_file_location("summarize_semantic_scenario", MODULE_PATH)
SUMMARY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUMMARY)


class ScenarioSummaryTests(unittest.TestCase):
    def test_coverage_reports_active_kinds_and_events(self):
        result = SUMMARY.coverage({"frames": [{
            "game": {
                "player": "player1", "level": 5, "round": 0,
                "state": "normal_gameplay",
            },
            "objects": [
                {"kind": "bird", "active": True},
                {"kind": "mothership", "active": False},
            ],
            "events": [{"type": "impact_observed"}],
        }]})
        self.assertEqual(result["players"], ["player1"])
        self.assertEqual(result["level_rounds"], [(5, 0)])
        self.assertEqual(result["active_kinds"], ["bird"])
        self.assertEqual(result["event_types"], {"impact_observed": 1})
