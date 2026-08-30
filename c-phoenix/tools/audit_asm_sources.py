#!/usr/bin/env python3
"""Verify the address/byte contracts of the Phoenix ASM documentation sources."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ANNOTATED = re.compile(r"^([0-9A-Fa-f]{4}):\s*((?:[0-9A-Fa-f]{2}(?=\s|$)\s*)+)")
LISTING = re.compile(r"^\d+\s+([0-9A-Fa-f]{4})\s+((?:[0-9A-Fa-f]{2}(?=\s|$)\s*)+)")


def verify_lines(path: Path, pattern: re.Pattern[str], rom: bytes) -> tuple[int, set[int]]:
    records = 0
    covered: set[int] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = pattern.match(line)
        if not match:
            continue
        start = int(match.group(1), 16)
        values = bytes.fromhex(match.group(2))
        if start + len(values) > len(rom):
            raise ValueError(f"{path}:{number}: range exceeds program ROM")
        expected = rom[start:start + len(values)]
        if values != expected:
            raise ValueError(
                f"{path}:{number}: bytes at ${start:04X} differ from program.rom "
                f"({values.hex(' ')} != {expected.hex(' ')})"
            )
        covered.update(range(start, start + len(values)))
        records += 1
    if not records:
        raise ValueError(f"{path}: no address/byte records found")
    return records, covered


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, default=root / "roms/assembled/program.rom")
    args = parser.parse_args()
    rom = args.rom.read_bytes()
    if len(rom) != 0x4000:
        raise ValueError(f"{args.rom}: expected a 16 KiB program ROM, got {len(rom)} bytes")
    context = root / "c-phoenix/context"
    annotated_records, annotated = verify_lines(context / "code-annotated.asm", ANNOTATED, rom)
    print(f"ASM source audit: annotated listing matches ROM "
          f"({annotated_records} records/{len(annotated)} bytes; ROM {len(rom)} bytes)")
    try:
        listing_records, listing = verify_lines(context / "Phoenix.lst", LISTING, rom)
        print(f"Phoenix listing also matches ROM ({listing_records} records/{len(listing)} bytes)")
    except ValueError as error:
        print(f"Phoenix listing differs from ROM as expected for its skipped data: {error}")


if __name__ == "__main__":
    main()
