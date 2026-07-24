import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "tools" / "extract_semantic_frames.py"
SPEC = importlib.util.spec_from_file_location("extract_semantic_frames", MODULE_PATH)
EXTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXTRACT)


class FakeTrace:
    @staticmethod
    def ram_byte(ram, address):
        return ram[address - 0x4000]


def game(score=0):
    return {
        "player": "player1", "level": 1, "round": 0,
        "state": "normal_gameplay",
        "scores": {"player1": score, "player2": 0},
        "lives": {"player1": 3, "player2": 3},
    }


class SemanticContractTests(unittest.TestCase):
    def test_game_context_decodes_level_and_round(self):
        context = EXTRACT.game_context({
            "level_and_round": 0x25,
            "player": "player2",
            "game_state": 0x03,
        }, bytes(0x0C00), FakeTrace())
        self.assertEqual(context, {
            "player": "player2",
            "level": 5,
            "round": 2,
            "state": "normal_gameplay",
            "scores": {"player1": 0, "player2": 0},
            "lives": {"player1": 0, "player2": 0},
        })

    def test_packed_bcd_decodes_score(self):
        ram = bytearray(0x0C00)
        ram[0x381:0x384] = bytes((0x01, 0x23, 0x40))
        self.assertEqual(EXTRACT.packed_bcd(ram, FakeTrace(), 0x4381), 12340)

    def test_score_event_reports_observed_change(self):
        previous = {"game": game(score=100), "objects": []}
        current = {"game": game(score=200), "objects": []}
        self.assertEqual(EXTRACT.semantic_events(previous, current), [{
            "type": "score_changed", "player": "player1", "from": 100, "to": 200,
        }])

    def test_semantic_object_has_no_raw_trace_fields(self):
        snapshot = {
            "player": "player1", "kind": "bird", "id": 3,
            "active": True, "type": "grown_bird", "phase": "descending",
            "state": 15, "shape": 15, "screen_addr": 0x4010,
        }
        result = EXTRACT.semantic_object(snapshot, {"visual_x": 64, "visual_y": 80})
        self.assertEqual(result["position"], {"x": 64, "y": 80})
        self.assertEqual(result["appearance"], {
            "family": "bird", "variant": "grown_bird", "motion": "descending",
        })
        self.assertNotIn("state", result)
        self.assertNotIn("screen_addr", result)

    def test_object_without_anchor_omits_position(self):
        snapshot = {
            "player": "player1", "kind": "alien", "id": 0,
            "active": False,
        }
        result = EXTRACT.semantic_object(snapshot, {"visual_x": None, "visual_y": None})
        self.assertNotIn("position", result)

    def test_projectile_is_hidden_outside_normal_gameplay(self):
        snapshot = {
            "player": "player1", "kind": "enemy_bullet", "id": 0,
            "active": True,
        }
        result = EXTRACT.semantic_object(
            snapshot, {"visual_x": 40, "visual_y": 80},
            {"state": "player_explosion"},
        )
        self.assertTrue(result["active"])
        self.assertFalse(result["visible"])

    def test_terminal_projectile_frame_is_hidden(self):
        frames = [
            {"objects": [{
                "key": "player1:player_bullet:0", "kind": "player_bullet",
                "visible": True,
            }]},
            {"objects": [{
                "key": "player1:player_bullet:0", "kind": "player_bullet",
                "visible": True,
            }]},
            {"objects": [{
                "key": "player1:player_bullet:0", "kind": "player_bullet",
                "visible": False,
            }]},
        ]
        EXTRACT.hide_terminal_projectile_frames(frames)
        self.assertFalse(frames[0]["objects"][0]["visible"])
        self.assertFalse(frames[1]["objects"][0]["visible"])

    def test_nearby_projectile_and_alien_deactivation_is_an_impact(self):
        previous = {"objects": [
            {"key": "player1:player_bullet:0", "kind": "player_bullet", "active": True,
             "position": {"x": 62, "y": 72}},
            {"key": "player1:alien:6", "kind": "alien", "active": True,
             "position": {"x": 56, "y": 72}},
        ]}
        current = {"objects": [
            {"key": "player1:player_bullet:0", "kind": "player_bullet", "active": False},
            {"key": "player1:alien:6", "kind": "alien", "active": False},
        ]}
        self.assertEqual(EXTRACT.observed_impacts(previous, current), [{
            "type": "impact_observed",
            "projectile": "player1:player_bullet:0",
            "target": "player1:alien:6",
            "position": {"x": 56, "y": 72},
        }])

    def test_effect_is_semantic_without_a_position(self):
        snapshot = {
            "player": "player1", "kind": "mothership", "id": 0,
            "active": True, "phase": "active",
        }
        result = EXTRACT.semantic_object(snapshot, {"visual_x": None, "visual_y": None})
        self.assertEqual(result["appearance"], {
            "family": "mothership", "variant": "standard", "motion": "active",
        })
        self.assertNotIn("position", result)


if __name__ == "__main__":
    unittest.main()
