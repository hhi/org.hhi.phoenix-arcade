#!/usr/bin/env python3
"""Fail when a local Markdown link does not resolve inside this checkout."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


LINK_RE = re.compile(r"!?(?:\[[^\]]*\])\(([^)\s]+)(?:\s+[^)]*)?\)")
IGNORED_SCHEMES = {"http", "https", "mailto", "data"}


def local_target(raw_target: str) -> str | None:
    target = raw_target.strip("<>")
    parsed = urlparse(target)
    if parsed.scheme in IGNORED_SCHEMES or target.startswith("#"):
        return None
    if parsed.scheme:
        return None
    return unquote(parsed.path)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) == 2 else ".").resolve()
    failures: list[str] = []
    for document in sorted(root.rglob("*.md")):
        if ".git" in document.parts:
            continue
        text = document.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = local_target(match.group(1))
            if target is None:
                continue
            resolved = (document.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                failures.append(f"{document.relative_to(root)}: escapes repository: {target}")
                continue
            if not resolved.exists():
                failures.append(f"{document.relative_to(root)}: missing: {target}")
    if failures:
        print("Broken local Markdown links:")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("Markdown links: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
