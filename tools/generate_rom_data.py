#!/usr/bin/env python3
"""Generate c-phoenix/rom_data.c from assembled program/graphics/proms ROM images.

Variant-independent: this script only knows about the three flat ROM images
(program.rom, graphics.rom, proms.rom, as produced by `make rombuild`) and the
fixed C array layout rom_data.c already uses. It has no knowledge of any
C2_VARIANT rendering variant.

Usage:
    python3 tools/generate_rom_data.py \
        --program roms/assembled/program.rom \
        --graphics roms/assembled/graphics.rom \
        --proms roms/assembled/proms.rom \
        --output c-phoenix/rom_data.c
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PROGRAM_SIZE = 0x4000
GRAPHICS_SIZE = 0x2000
PROMS_SIZE = 0x200
PROM_HALF = 0x100


def read_exact(path: Path, size: int, label: str) -> bytes:
    data = path.read_bytes()
    if len(data) != size:
        raise ValueError(f"{label}: {path} is {len(data)} bytes, expected {size}")
    return data


def format_array(name: str, size_literal: str, data: bytes) -> str:
    lines = [f"const uint8_t {name}[{size_literal}] = {{"]
    for offset in range(0, len(data), 16):
        row = ", ".join(f"0x{byte:02X}" for byte in data[offset:offset + 16])
        lines.append(f"    {row},")
    lines.append("};")
    return "\n".join(lines)


def generate(program: bytes, graphics: bytes, proms: bytes) -> str:
    # proms.rom layout (see roms/phoenix-amstar/rom-set.json): low colour
    # bits (mmi6301.ic40 / palette_prom_b) at offset 0, high colour bits
    # (mmi6301.ic41 / palette_prom_a) at offset 256. rom_data.c has always
    # declared palette_prom_a before palette_prom_b, so the emit order below
    # intentionally differs from the byte order in proms.rom.
    palette_low = proms[:PROM_HALF]
    palette_high = proms[PROM_HALF:]

    sections = [
        '#include "rom_data.h"',
        "",
        format_array("gfx_mem", "0x2000", graphics),
        "",
        format_array("palette_prom_a", "0x0100", palette_high),
        "",
        format_array("palette_prom_b", "0x0100", palette_low),
        "",
        format_array("prg_mem", "0x4000", program),
        "",
    ]
    return "\n".join(sections)


def parse_arrays(text: str) -> dict[str, bytes]:
    arrays: dict[str, bytes] = {}
    for match in re.finditer(r"const uint8_t (\w+)\[[^\]]*\] = \{(.*?)\};", text, re.DOTALL):
        values = [int(v, 16) for v in re.findall(r"0x[0-9A-Fa-f]+", match.group(2))]
        arrays[match.group(1)] = bytes(values)
    return arrays


def verify(existing_text: str, rebuilt_text: str) -> list[str]:
    existing = parse_arrays(existing_text)
    rebuilt = parse_arrays(rebuilt_text)
    problems = []
    for name in sorted(set(existing) | set(rebuilt)):
        if name not in rebuilt:
            problems.append(f"{name}: missing from regenerated output")
        elif name not in existing:
            problems.append(f"{name}: not present in existing file")
        elif existing[name] != rebuilt[name]:
            problems.append(f"{name}: byte mismatch ({len(existing[name])} vs {len(rebuilt[name])} bytes)")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--program", type=Path, required=True, help="Path to program.rom (16384 bytes)")
    parser.add_argument("--graphics", type=Path, required=True, help="Path to graphics.rom (8192 bytes)")
    parser.add_argument("--proms", type=Path, required=True, help="Path to proms.rom (512 bytes)")
    parser.add_argument("--output", type=Path, required=True, help="Path to write rom_data.c to")
    parser.add_argument(
        "--existing",
        type=Path,
        help="If given, verify the regenerated arrays byte-match this file before writing",
    )
    parser.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Write output even if it disagrees with --existing (default: abort on mismatch)",
    )
    args = parser.parse_args()

    program = read_exact(args.program, PROGRAM_SIZE, "program.rom")
    graphics = read_exact(args.graphics, GRAPHICS_SIZE, "graphics.rom")
    proms = read_exact(args.proms, PROMS_SIZE, "proms.rom")

    rebuilt_text = generate(program, graphics, proms)

    if args.existing:
        problems = verify(args.existing.read_text(encoding="ascii"), rebuilt_text)
        if problems:
            print(f"{len(problems)} problem(s) vs {args.existing}:")
            for problem in problems:
                print(f"  - {problem}")
            if not args.allow_mismatch:
                print("Aborting without writing output (pass --allow-mismatch to override).")
                return 1
        else:
            print(f"All 4 arrays byte-match the existing {args.existing}.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rebuilt_text, encoding="ascii")
    print(f"Wrote {args.output} ({args.output.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
