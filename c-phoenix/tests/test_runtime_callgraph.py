import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "generate_c_runtime_callgraph.py"
SPEC = importlib.util.spec_from_file_location("runtime_callgraph", TOOL)
RUNTIME_CALLGRAPH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME_CALLGRAPH)


class FunctionalRuntimeCallgraphTest(unittest.TestCase):
    def setUp(self):
        self.function_files = RUNTIME_CALLGRAPH.source_function_files(ROOT)

    def test_groups_known_gameplay_functions_by_source_module(self):
        self.assertEqual(
            RUNTIME_CALLGRAPH.functional_area("update_bird_behavior", self.function_files),
            "birds",
        )
        self.assertEqual(
            RUNTIME_CALLGRAPH.functional_area("player_update", self.function_files),
            "player",
        )
        self.assertEqual(
            RUNTIME_CALLGRAPH.functional_area("sound_render_frame", self.function_files),
            "audio",
        )

    def test_formats_large_call_counts_compactly(self):
        self.assertEqual(RUNTIME_CALLGRAPH.compact_count(42), "42")
        self.assertEqual(RUNTIME_CALLGRAPH.compact_count(1234), "1.2k")
        self.assertEqual(RUNTIME_CALLGRAPH.compact_count(1_855_600_052), "1.9B")

    def test_explorer_data_preserves_functional_module_and_function_levels(self):
        locations = RUNTIME_CALLGRAPH.source_function_locations(ROOT)
        data = RUNTIME_CALLGRAPH.runtime_explorer_data(
            {
                ("player_update", "update_bird_behavior"): 7,
                ("update_bird_behavior", "sound_render_frame"): 3,
            },
            self.function_files,
            locations,
        )
        root = data["root"]
        player = next(node for node in root["children"] if node["id"] == "area:player")
        module = player["children"][0]
        self.assertEqual(root["kind"], "domain")
        self.assertEqual(player["kind"], "subsystem")
        self.assertEqual(module["kind"], "module")
        self.assertEqual(module["children"][0]["kind"], "function")
        self.assertEqual(module["children"][0]["source_file"], "player_logic.c")
        self.assertIsInstance(module["children"][0]["source_line"], int)
        self.assertEqual(data["edges"][0]["count"], 7)


if __name__ == "__main__":
    unittest.main()
