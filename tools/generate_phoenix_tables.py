#!/usr/bin/env python3
"""Regenerate c-phoenix/phoenix_tables.c's byte contents from prg_mem.

Variant-independent: this script has no knowledge of any C2_VARIANT
rendering variant. It only knows two things: the `[ASM: XXXX-YYYY]` start
address documented next to each `extern const uint8_t NAME[SIZE];` (or, for
the one single-byte table, `extern const uint8_t NAME;`) declaration in
phoenix_tables.h, and the declared size. Every table is a verbatim,
contiguous slice of prg_mem starting at that address; this is verified
against the currently-committed phoenix_tables.c before writing anything.

phoenix_tables.h itself is never modified or generated -- it is the source
of truth this script reads. Comments, ordering, and every other line of
phoenix_tables.c are copied from the existing file; only the byte payload
inside each initializer is replaced.

Usage:
    python3 tools/generate_phoenix_tables.py \
        --header c-phoenix/phoenix_tables.h \
        --existing c-phoenix/phoenix_tables.c \
        --prg-mem roms/assembled/program.rom \
        --output c-phoenix/phoenix_tables.c
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

TAG_RE = re.compile(r"\[ASM:\s*([0-9A-Fa-f]{4})(?:-[0-9A-Fa-f]{4})?\]")
EXTERN_RE = re.compile(r"extern const uint8_t (\w+)(?:\[(0x[0-9A-Fa-f]+)\])?;")
# Matches both the array form `NAME[SIZE] = { ... };` and the one scalar
# table `NAME = 0xXX;`.
DEFINITION_RE = re.compile(
    r"const uint8_t (\w+)(?:\[[^\]]*\]\s*=\s*\{(.*?)\}|\s*=\s*(0x[0-9A-Fa-f]+))\s*;",
    re.DOTALL,
)


def parse_table_spec(header_text: str) -> dict[str, tuple[int, int]]:
    """Map array name -> (start_address, declared_size) from phoenix_tables.h."""
    specs: dict[str, tuple[int, int]] = {}
    cursor = 0
    for match in EXTERN_RE.finditer(header_text):
        name = match.group(1)
        size = int(match.group(2), 16) if match.group(2) else 1
        preceding = header_text[cursor:match.start()]
        tags = TAG_RE.findall(preceding)
        if not tags:
            raise ValueError(f"No [ASM: ...] tag found before extern declaration of {name}")
        start = int(tags[-1], 16)
        specs[name] = (start, size)
        cursor = match.end()
    return specs


def format_array_body(data: bytes) -> str:
    lines = []
    for offset in range(0, len(data), 16):
        row = ", ".join(f"0x{byte:02X}" for byte in data[offset:offset + 16])
        lines.append(f"    {row},")
    return "\n".join(lines)


def rebuild_source(existing_text: str, specs: dict[str, tuple[int, int]], prg_mem: bytes) -> str:
    def replace(match: re.Match) -> str:
        name = match.group(1)
        if name not in specs:
            raise ValueError(f"{name} has no [ASM: ...] entry in phoenix_tables.h")
        start, size = specs[name]
        if start + size > len(prg_mem):
            raise ValueError(f"{name}: range 0x{start:04X}+0x{size:X} exceeds prg_mem")
        data = prg_mem[start:start + size]
        is_scalar = match.group(3) is not None
        if is_scalar:
            return f"const uint8_t {name} = 0x{data[0]:02X};"
        header_line = match.group(0).split("{", 1)[0] + "{"
        return f"{header_line}\n{format_array_body(data)}\n}};"

    return DEFINITION_RE.sub(replace, existing_text)


def verify(existing_text: str, rebuilt_text: str) -> list[str]:
    def parse_definitions(text: str) -> dict[str, bytes]:
        values: dict[str, bytes] = {}
        for match in DEFINITION_RE.finditer(text):
            name = match.group(1)
            if match.group(3) is not None:
                values[name] = bytes([int(match.group(3), 16)])
            else:
                values[name] = bytes(int(v, 16) for v in re.findall(r"0x[0-9A-Fa-f]+", match.group(2)))
        return values

    existing = parse_definitions(existing_text)
    rebuilt = parse_definitions(rebuilt_text)
    problems = []
    for name in sorted(set(existing) | set(rebuilt)):
        if name not in rebuilt:
            problems.append(f"{name}: missing from regenerated output")
        elif name not in existing:
            problems.append(f"{name}: not present in existing file (new table?)")
        elif existing[name] != rebuilt[name]:
            problems.append(f"{name}: byte mismatch ({len(existing[name])} vs {len(rebuilt[name])} bytes)")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--header", type=Path, required=True, help="Path to phoenix_tables.h")
    parser.add_argument("--existing", type=Path, required=True, help="Path to the current phoenix_tables.c")
    parser.add_argument("--prg-mem", type=Path, required=True, help="Path to program.rom (16384 bytes)")
    parser.add_argument("--output", type=Path, required=True, help="Path to write the regenerated phoenix_tables.c to")
    parser.add_argument(
        "--allow-mismatch",
        action="store_true",
        help="Write output even if it disagrees with --existing (default: abort on mismatch)",
    )
    args = parser.parse_args()

    header_text = args.header.read_text(encoding="utf-8")
    existing_text = args.existing.read_text(encoding="utf-8")
    prg_mem = args.prg_mem.read_bytes()
    if len(prg_mem) != 0x4000:
        raise SystemExit(f"{args.prg_mem}: {len(prg_mem)} bytes, expected 0x4000")

    specs = parse_table_spec(header_text)
    rebuilt_text = rebuild_source(existing_text, specs, prg_mem)

    problems = verify(existing_text, rebuilt_text)
    if problems:
        print(f"{len(problems)} problem(s) vs {args.existing}:")
        for problem in problems:
            print(f"  - {problem}")
        if not args.allow_mismatch:
            print("Aborting without writing output (pass --allow-mismatch to override).")
            return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rebuilt_text, encoding="utf-8")
    print(f"Wrote {args.output} ({len(specs)} tables, {args.output.stat().st_size} bytes)")
    if not problems:
        print(f"All {len(specs)} tables byte-match the existing {args.existing}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
