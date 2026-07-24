import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = ROOT / "tools" / "lockstep" / "semantic_delta.py"
RAM_SIZE = 0xC00
PLAYER_SHIP_X_OFFSET = 0x43C2 - 0x4000


def write_dump(path: Path, values: list[int]) -> None:
    records = bytearray()
    for frame, value in enumerate(values):
        ram = bytearray(RAM_SIZE)
        ram[PLAYER_SHIP_X_OFFSET] = value
        records.extend(struct.pack(">I", frame))
        records.extend(ram)
    path.write_bytes(records)


class SemanticDeltaTests(unittest.TestCase):
    def test_extracts_symbolised_transition_and_parity_diff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            reference = tmp_path / "reference.bin"
            port = tmp_path / "port.bin"
            output_json = tmp_path / "delta.json"
            output_md = tmp_path / "delta.md"
            write_dump(reference, [0, 0x4D, 0x4E])
            write_dump(port, [0, 0x4E, 0x4F])

            subprocess.run(
                [
                    sys.executable,
                    str(EXTRACTOR),
                    str(reference),
                    str(port),
                    "--record",
                    "1",
                    "--window",
                    "0",
                    "--regions",
                    "43C2-43C2",
                    f"--output-json={output_json}",
                    f"--output-md={output_md}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            report = json.loads(output_json.read_text(encoding="utf-8"))
            frame = report["frames"][0]
            self.assertEqual(frame["reference_changes"][0]["symbol"], "PlayerShipX")
            self.assertEqual(frame["reference_changes"][0]["before"], 0)
            self.assertEqual(frame["reference_changes"][0]["after"], 0x4D)
            self.assertEqual(frame["port_changes"][0]["after"], 0x4E)
            self.assertEqual(frame["parity_diffs"][0]["address"], "0x43C2")

            markdown = output_md.read_text(encoding="utf-8")
            self.assertIn("### Referentie-mutaties", markdown)
            self.assertIn("PlayerShipX", markdown)
            self.assertIn("### Parity-diffs", markdown)

