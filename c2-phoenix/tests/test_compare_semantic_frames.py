import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "tools" / "compare_semantic_frames.py"
SPEC = importlib.util.spec_from_file_location("compare_semantic_frames", MODULE_PATH)
COMPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARE)


def frame(active=True):
    return {
        "game": {"player": "player1", "level": 5, "round": 0, "state": "normal_gameplay"},
        "objects": [{
            "key": "player1:bird:0", "kind": "bird", "slot": 0,
            "active": active,
            "appearance": {"family": "bird", "variant": "grown_bird", "motion": "descending"},
            "position": {"x": 32, "y": 64},
        }],
    }


class SemanticComparisonTests(unittest.TestCase):
    def test_identical_frames_have_no_differences(self):
        self.assertEqual(COMPARE.frame_differences(frame(), frame()), [])

    def test_object_state_difference_is_reported(self):
        differences = COMPARE.frame_differences(frame(), frame(active=False))
        self.assertEqual(len(differences), 1)
        self.assertIn("player1:bird:0", differences[0])

    def test_same_tick_does_not_hide_a_frame_difference(self):
        reference = frame()
        port = frame(active=False)
        reference["timeline"] = {"tick": 4}
        port["timeline"] = {"tick": 4}
        self.assertTrue(COMPARE.frame_differences(reference, port))


if __name__ == "__main__":
    unittest.main()
