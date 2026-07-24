import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VIEW_TOOL = ROOT / "tools" / "view_sprite_trace.py"
RAM_SIZE = 0x0C00
sys.path.insert(0, str(ROOT / "tools"))
import view_sprite_trace


def make_alien_frame(x=0x10, frame=1):
    ram = bytearray(RAM_SIZE)
    ram[0x3A3] = 0  # $43A3: player 1 bank
    ram[0x3A4] = 3  # $43A4: normal gameplay
    ram[0x3B8] = 1
    ram[0xB70:0xB74] = bytes((0x08, 0x34, x, 0x20))
    return struct.pack(">I", frame) + ram


def make_bird_frame(x=0x10, y=0xB8, frame=1):
    ram = bytearray(RAM_SIZE)
    ram[0x3A3] = 0  # $43A3: player 1 bank
    ram[0x3A4] = 3  # $43A4: normal gameplay
    ram[0x3B8] = 5  # $43B8: bird level
    ram[0x3C0:0x3C4] = bytes((0x0C, 0x10, 0x64, 0xD8))
    ram[0xBA8:0xBB0] = bytes((0x0F, 0x49, 0x0C, 0x10, 0x00, x, 0x00, y))
    return struct.pack(">I", frame) + ram


class ViewSpriteTraceTest(unittest.TestCase):
    def test_auto_kind_follows_alien_and_bird_ram_overlays(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            dump_path = temp_path / "trace.bin"
            output_path = temp_path / "viewer.html"
            dump_path.write_bytes(
                make_alien_frame(frame=1) + make_bird_frame(frame=2)
            )
            subprocess.run(
                [sys.executable, str(VIEW_TOOL), str(dump_path),
                 "--output", str(output_path)],
                check=True,
            )
            document = output_path.read_text(encoding="utf-8")

        self.assertIn('"kind":"alien"', document)
        self.assertIn('"kind":"bird"', document)
        self.assertIn('"kind":"player_ship"', document)

    def test_alien_overlay_is_not_decoded_during_spiral_transition(self):
        ram = bytearray(RAM_SIZE)
        ram[0x3B8] = 4  # $43B8: bird spiral-fill transition

        self.assertEqual(
            list(view_sprite_trace.trace_sprites.alien_snapshots(1, ram)), []
        )

    def test_plain_bird_label_does_not_claim_a_visual_size(self):
        self.assertEqual(view_sprite_trace.trace_sprites.bird_variant(0x04), "plain_bird")

    def test_writes_standalone_alien_viewer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            dump_path = temp_path / "trace.bin"
            output_path = temp_path / "viewer.html"
            dump_path.write_bytes(make_alien_frame())
            subprocess.run(
                [
                    sys.executable, str(VIEW_TOOL), str(dump_path),
                    "--kind", "aliens", "--output", str(output_path),
                ],
                check=True,
            )
            document = output_path.read_text(encoding="utf-8")

        self.assertIn('id="frame" type="range"', document)
        self.assertIn('id="play"', document)
        self.assertIn('id="previousFrame"', document)
        self.assertIn('id="nextFrame"', document)
        self.assertIn('id="frameOverview"', document)
        self.assertIn('function startStepping(direction)', document)
        self.assertIn('const playbackFrameMs = 1000 / 60;', document)
        self.assertIn('frameInput.value = (Number(frameInput.value) + 1) % frames.length;', document)
        self.assertIn('const samplesByKey = new Map();', document)
        self.assertIn('while (low <= high)', document)
        self.assertIn('timer = requestAnimationFrame(playTick);', document)
        self.assertIn('setInterval(() => moveFrame(direction), 120)', document)
        self.assertIn('"metadata":[{"frame":1,"counter98":0,"level_and_round":1,"game_state":3,"scroll":0,"bird_formation_scroll":0}]', document)
        self.assertIn('"x":16', document)
        self.assertIn('"y":32', document)

    def test_writes_compared_alien_viewer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            reference_path = temp_path / "reference.bin"
            port_path = temp_path / "port.bin"
            output_path = temp_path / "viewer.html"
            reference_path.write_bytes(make_alien_frame(x=0x10))
            port_path.write_bytes(make_alien_frame(x=0x11, frame=99))
            subprocess.run(
                [
                    sys.executable, str(VIEW_TOOL), str(reference_path),
                    "--compare", str(port_path),
                    "--kind", "aliens", "--output", str(output_path),
                    "--reference-label", "jphoenix",
                    "--port-label", "c-phoenix",
                ],
                check=True,
            )
            document = output_path.read_text(encoding="utf-8")

        self.assertIn('"compare":true', document)
        self.assertIn('"jphoenix"', document)
        self.assertIn('"c-phoenix"', document)
        self.assertIn('id="nextDiff"', document)
        self.assertIn('id="prevLevel"', document)
        self.assertIn('id="nextLevel"', document)
        self.assertIn('id="unmatchedCount"', document)
        self.assertIn('function isUnmatchedReferenceSample(sample)', document)
        self.assertIn('function isDiff(sample, other = compareSample(sample))', document)
        self.assertIn('payload.labels[0] + " tail records"', document)
        self.assertIn('"x":17', document)

    def test_writes_bird_grid_coordinates_for_canvas_rendering(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = pathlib.Path(temp_dir)
            dump_path = temp_path / "trace.bin"
            output_path = temp_path / "viewer.html"
            dump_path.write_bytes(make_bird_frame())
            subprocess.run(
                [
                    sys.executable, str(VIEW_TOOL), str(dump_path),
                    "--kind", "birds", "--include-kind", "player_ship",
                    "--output", str(output_path),
                ],
                check=True,
            )
            document = output_path.read_text(encoding="utf-8")

        self.assertIn('"x":16', document)
        self.assertIn('"y":184', document)
        self.assertIn('"visual_y":100', document)
        self.assertIn('"kind":"player_ship"', document)
        self.assertIn('"level_and_round":5', document)
        self.assertIn('id="allObjects" type="checkbox"', document)
        self.assertIn('id="showCoordinatesOnGrid" type="checkbox"', document)
        self.assertIn('id="showGridTrace" type="checkbox">', document)
        self.assertIn('id="showInactiveTraces" type="checkbox">', document)
        self.assertIn('id="showPreviousLevelTraces" type="checkbox">', document)
        self.assertIn('function slotColor(key)', document)
        self.assertIn('function drawOffPulse(sample)', document)
        self.assertIn('function offTransition(key, frame)', document)
        self.assertIn('if (deathPosition) drawOffPulse(deathPosition)', document)
        self.assertIn('className = "object-swatch"', document)
        self.assertIn('row.style.setProperty("--slot-color", slotColor(key))', document)
        self.assertIn('row.dataset.slotKey = key;', document)
        self.assertIn('card.dataset.slotKey = key;', document)
        self.assertIn('row.setAttribute("role", "button")', document)
        self.assertIn('card.setAttribute("role", "button")', document)
        self.assertIn('function bindSlotSelection(element, key)', document)
        self.assertIn('if (key === hoveredKey) row.classList.add("hovered")', document)
        self.assertNotIn('row.addEventListener("mouseenter"', document)
        self.assertIn('let hasExplicitSelection = false;', document)
        self.assertIn('hasExplicitSelection = true;', document)
        self.assertIn('id="showSelectedObjectLabel" type="checkbox"', document)
        self.assertIn('showSelectedObjectLabel.checked && hasExplicitSelection', document)
        self.assertIn('objects.addEventListener("pointerdown", () => setPlaying(false))', document)
        self.assertIn('slotData.addEventListener("pointerdown", () => setPlaying(false))', document)
        self.assertIn('function sampleAtFrame(key, frame)', document)
        self.assertIn('"#" + displayKind(sample, sample.frame) + "-" + sample.id', document)
        self.assertIn('id="slotData"', document)
        self.assertIn('const trailLength = 90', document)
        self.assertIn('const levelSegments = [];', document)
        self.assertIn('function jumpLevel(direction)', document)
        self.assertIn('point.record_index >= traceStartIndex', document)
        self.assertIn('function levelDescription(level)', document)
        self.assertIn('function isBirdLayer(frame)', document)
        self.assertIn('const frameMetadata = frameMetadataByFrame.get(frame) || current;', document)

    def test_maps_screen_addresses_to_rotated_physical_screen(self):
        self.assertEqual(view_sprite_trace.screen_coordinate(0x4000), (204, 4))
        self.assertEqual(view_sprite_trace.screen_coordinate(0x4001), (204, 12))
        self.assertEqual(view_sprite_trace.screen_coordinate(0x4020), (196, 4))

    def test_bird_prefers_draw_routine_screen_anchor_to_grid_coordinates(self):
        before = view_sprite_trace.viewer_sample({
            "kind": "bird", "screen_addr": 0x490C, "x": 175, "y": 176,
        })
        after = view_sprite_trace.viewer_sample({
            "kind": "bird", "screen_addr": 0x48EC, "x": 176, "y": 56,
        })

        self.assertEqual((before["visual_x"], before["visual_y"]), (140, 100))
        self.assertEqual((after["visual_x"], after["visual_y"]), (148, 100))

    def test_bird_visual_y_includes_background_scroll(self):
        sample = view_sprite_trace.viewer_sample({
            "kind": "bird", "screen_addr": 0x490C, "x": 175, "y": 176,
        }, scroll=0x10)

        self.assertEqual((sample["visual_x"], sample["visual_y"]), (140, 84))
        self.assertEqual((sample["screen_x"], sample["screen_y"]), (140, 100))

    def test_bird_outside_draw_screen_is_not_repositioned_from_grid_bytes(self):
        sample = view_sprite_trace.viewer_sample({
            "kind": "bird", "screen_addr": 0x4B4E, "x": 30, "y": 8,
        })

        self.assertIsNone(sample["visual_x"])
        self.assertIsNone(sample["visual_y"])


if __name__ == "__main__":
    unittest.main()
