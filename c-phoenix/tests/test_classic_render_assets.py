"""Contracts for the generated classic SDL renderer assets."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools" / "generate_classic_render_assets.py"
GRAPHICS_ROM = ROOT.parent / "roms" / "assembled" / "graphics.rom"
PROMS_ROM = ROOT.parent / "roms" / "assembled" / "proms.rom"
TRACKED_HEADER = ROOT / "phoenix_render_assets.h"


class ClassicRenderAssetTests(unittest.TestCase):
    def test_generator_reproduces_tracked_tiles_and_palette(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "phoenix_render_assets.h"
            subprocess.run(
                [sys.executable, str(GENERATOR), "--graphics", str(GRAPHICS_ROM),
                 "--proms", str(PROMS_ROM), "--output", str(output)],
                check=True,
            )
            self.assertEqual(output.read_bytes(), TRACKED_HEADER.read_bytes())


if __name__ == "__main__":
    unittest.main()
