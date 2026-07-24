import csv
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
TRACE_TOOL = ROOT / "tools" / "trace_sprites.py"
RAM_SIZE = 0x0C00


def make_frame(frame, control_a, x, level=1):
    ram = bytearray(RAM_SIZE)
    ram[0x3A3] = 1  # $43A3: player 2 bank
    ram[0x3A4] = 3  # $43A4: normal gameplay
    ram[0x3B8] = level
    ram[0xB50] = 0x2E
    ram[0xB51] = 0x40
    ram[0xB70] = control_a
    ram[0xB71] = 0x34
    ram[0xB72] = x
    ram[0xB73] = 0x20
    ram[0xBB0:0xBB4] = bytes((0x41, 0x00, 0x41, 0x20))
    return struct.pack(">I", frame) + ram


class TraceSpritesTest(unittest.TestCase):
    def test_changed_active_alien_snapshots(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dump_path = pathlib.Path(temp_dir) / "trace.bin"
            dump_path.write_bytes(
                make_frame(1, 0x08, 0x10)
                + make_frame(2, 0x08, 0x10)
                + make_frame(3, 0x08, 0x11)
                + make_frame(4, 0x00, 0x11)
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(TRACE_TOOL),
                    str(dump_path),
                    "--kind",
                    "aliens",
                    "--slot",
                    "0",
                    "--only-active",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        rows = list(csv.DictReader(completed.stdout.splitlines()))
        self.assertEqual([row["frame"] for row in rows], ["1", "3"])
        self.assertEqual([row["player"] for row in rows], ["player2", "player2"])
        self.assertEqual([row["x"] for row in rows], ["16", "17"])
        self.assertEqual(rows[0]["movement_pattern"], "11840")
        self.assertEqual(rows[0]["screen_addr"], "16672")

    def test_bird_level_uses_bird_layout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dump_path = pathlib.Path(temp_dir) / "birds.bin"
            dump_path.write_bytes(make_frame(1, 0x0B, 0x10, level=5))
            completed = subprocess.run(
                [
                    sys.executable,
                    str(TRACE_TOOL),
                    str(dump_path),
                    "--kind",
                    "birds",
                    "--slot",
                    "0",
                    "--only-active",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        rows = list(csv.DictReader(completed.stdout.splitlines()))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "bird")
        self.assertEqual(rows[0]["type"], "egg")
        self.assertEqual(rows[0]["screen_addr"], "13328")


if __name__ == "__main__":
    unittest.main()
