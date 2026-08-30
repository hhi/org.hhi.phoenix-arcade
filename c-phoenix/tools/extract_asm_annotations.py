#!/usr/bin/env python3
"""One-time migration: extract labels and semantic notes from the legacy listing."""
import argparse
import json
import re
from pathlib import Path

LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*$")
RECORD = re.compile(r"^([0-9A-Fa-f]{4}):.*?(?:;\s*(.*))?$")
REFERENCE = re.compile(r"\{(\+?(?:code|ram)\.[^}]+)\}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("context/code-annotated.asm"))
    parser.add_argument("--output", type=Path, default=Path("context/asm-annotations.yaml"))
    args = parser.parse_args()
    pending, labels, notes = [], [], []
    for line in args.input.read_text(encoding="utf-8").splitlines():
        if match := LABEL.match(line):
            pending.append(match.group(1))
            continue
        if not (match := RECORD.match(line)):
            continue
        address, comment = match.group(1).lower(), (match.group(2) or "").strip()
        if pending:
            labels.append({"address": address, "names": pending})
            pending = []
        refs = sorted(set(REFERENCE.findall(comment)))
        if comment or refs:
            notes.append({"address": address, "comment": comment, "references": refs})
    data = {"version": 1, "source": "code-annotated.asm migration baseline", "labels": labels, "notes": notes}
    # JSON is valid YAML 1.2 and avoids an unreviewed YAML dependency during
    # migration.  The .yaml file remains hand-editable after this baseline.
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"ASM annotations extracted: {len(labels)} label groups, {len(notes)} notes")


if __name__ == "__main__":
    main()
