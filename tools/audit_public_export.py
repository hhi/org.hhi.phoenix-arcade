#!/usr/bin/env python3
"""Report files that must not enter the planned byte-free public export."""

from __future__ import annotations

import argparse
from pathlib import Path


BLOCKED_PATHS = (
    "jphoenix-emulator-port/program.rom",
    "jphoenix-emulator-port/graphics.rom",
    "jphoenix-emulator-port/proms.rom",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail when private-only material is present",
    )
    args = parser.parse_args()

    found = [path for path in BLOCKED_PATHS if (args.root / path).exists()]
    print("Public export audit")
    for path in found:
        print(f"  private-only: {path}")
    if not found:
        print("  no known private-only paths found")

    if found and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
