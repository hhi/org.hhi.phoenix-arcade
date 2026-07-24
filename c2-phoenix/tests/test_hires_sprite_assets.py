"""Contracts for the generated C2 hi-res glyph atlas."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "c2-phoenix" / "tools" / "generate_hires_sprite_assets.py"
GRAPHICS_ROM = ROOT / "roms" / "assembled" / "graphics.rom"
PROMS_ROM = ROOT / "roms" / "assembled" / "proms.rom"


class HiresSpriteAssetTests(unittest.TestCase):
    def test_generator_exports_hires_glyphs_and_palette(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "c2_hires_sprite_assets.h"
            subprocess.run(
                [sys.executable, str(GENERATOR), "--graphics", str(GRAPHICS_ROM),
                 "--proms", str(PROMS_ROM),
                 "--output", str(output)],
                check=True,
            )
            header = output.read_text(encoding="ascii")

        self.assertIn("C2_HIRES_BACKGROUND_GLYPHS[256][256]", header)
        self.assertIn("C2_HIRES_FOREGROUND_GLYPHS[256][256]", header)
        self.assertIn("C2_HIRES_PROM_COLOURS[128]", header)
        self.assertIn("C2_HIRES_PIXEL_OPACITY", header)


if __name__ == "__main__":
    unittest.main()
