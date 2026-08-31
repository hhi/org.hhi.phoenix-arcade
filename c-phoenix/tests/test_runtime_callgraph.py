import importlib.util
import pathlib
import tempfile
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

    def test_finds_multiline_and_header_inline_runtime_functions(self):
        locations = RUNTIME_CALLGRAPH.source_function_locations(ROOT)
        expected_files = {
            "l2085_particles": "player_explosion.c",
            "astable_step": "sound_discrete.c",
            "mem_read": "z80_core.h",
            "mem_write": "z80_core.h",
            "phoenix_image_byte": "phoenix_tables.h",
        }
        for function, expected_file in expected_files.items():
            source_file, source_line = locations[function]
            self.assertEqual(source_file, expected_file)
            source_lines = (ROOT / source_file).read_text(encoding="utf-8").splitlines()
            signature = "\n".join(source_lines[source_line - 1:source_line + 3])
            self.assertRegex(signature, rf"\b{function}\s*\(")

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

    def test_explorer_links_known_functions_and_header_helpers_to_html_viewers(self):
        locations = RUNTIME_CALLGRAPH.source_function_locations(ROOT)
        counts = {
            ("add_galaxies_to_background", "mem_write"): 47,
            ("mem_write", "update_scroll_register_and_fill_background"): 47,
        }
        with tempfile.TemporaryDirectory() as temporary:
            output = pathlib.Path(temporary) / "index.html"
            RUNTIME_CALLGRAPH.write_runtime_explorer(
                output, counts, self.function_files, locations
            )
            page = output.read_text(encoding="utf-8")
        self.assertIn("const functionIds = new Map()", page)
        self.assertIn("functionIds.get(name)||'context:'+name", page)
        self.assertIn("function sourceViewerHref(file,line)", page)
        self.assertIn("context/source", page)
        self.assertNotIn("${node.source_file}#L${node.source_line}", page)


if __name__ == "__main__":
    unittest.main()
