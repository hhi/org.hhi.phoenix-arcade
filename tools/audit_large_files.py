#!/usr/bin/env python3
"""Report large worktree files and reject unapproved files over a hard limit."""

from __future__ import annotations

import sys
from pathlib import Path


WARN_BYTES = 1 * 1024 * 1024
REVIEW_BYTES = 5 * 1024 * 1024
BLOCK_BYTES = 20 * 1024 * 1024
ALLOWED_OVER_BLOCK = frozenset()


def format_size(size: int) -> str:
    return f"{size / (1024 * 1024):.1f} MiB"


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) == 2 else ".").resolve()
    files = sorted(
        (path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts),
        key=lambda path: path.stat().st_size,
    )
    large = [path for path in files if path.stat().st_size >= WARN_BYTES]
    blocked = []
    for path in large:
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        level = "review" if size >= REVIEW_BYTES else "report"
        print(f"{format_size(size):>10}  {level:6}  {relative}")
        if size >= BLOCK_BYTES and relative not in ALLOWED_OVER_BLOCK:
            blocked.append(relative)
    if blocked:
        print("Files at or above 20 MiB require an explicit allowlist entry:")
        print("\n".join(f"- {path}" for path in blocked))
        return 1
    print(f"Large-file audit: OK ({len(large)} files reported)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
