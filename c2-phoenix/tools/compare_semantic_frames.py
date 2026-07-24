#!/usr/bin/env python3
"""Compare two C2 semantic-frame exports in their recorded order."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CONTRACT = "org.hhi.phoenix.c2.semantic-frame/v1"


def load_document(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("schema") != CONTRACT:
        raise ValueError(f"{path}: unsupported semantic frame contract")
    return document


def objects_by_key(frame: dict) -> dict[str, dict]:
    return {object_["key"]: object_ for object_ in frame.get("objects", [])}


def frame_differences(reference: dict, port: dict) -> list[str]:
    differences = []
    if reference.get("game") != port.get("game"):
        differences.append(
            f"game reference={reference.get('game')} port={port.get('game')}"
        )
    if reference.get("events", []) != port.get("events", []):
        differences.append(
            f"events reference={reference.get('events', [])} "
            f"port={port.get('events', [])}"
        )
    reference_objects = objects_by_key(reference)
    port_objects = objects_by_key(port)
    for key in sorted(reference_objects.keys() - port_objects.keys()):
        differences.append(f"missing object in port: {key}")
    for key in sorted(port_objects.keys() - reference_objects.keys()):
        differences.append(f"extra object in port: {key}")
    for key in sorted(reference_objects.keys() & port_objects.keys()):
        if reference_objects[key] != port_objects[key]:
            differences.append(
                f"object {key} reference={reference_objects[key]} "
                f"port={port_objects[key]}"
            )
    return differences


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path, help="JPhoenix semantic JSON")
    parser.add_argument("port", type=Path, help="C-Phoenix semantic JSON")
    parser.add_argument("--max-differences", type=int, default=20,
                        help="maximum difference lines to print (default: 20)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reference, port = load_document(args.reference), load_document(args.port)
    reference_frames = reference.get("frames", [])
    port_frames = port.get("frames", [])
    shared = min(len(reference_frames), len(port_frames))
    print(
        "Semantic record alignment: "
        f"{shared} shared records; "
        f"reference-only={len(reference_frames) - shared}; "
        f"port-only={len(port_frames) - shared}"
    )

    mismatches = 0
    reported = 0
    for sequence in range(shared):
        reference_frame = reference_frames[sequence]
        port_frame = port_frames[sequence]
        differences = frame_differences(reference_frame, port_frame)
        if not differences:
            continue
        mismatches += 1
        if reported >= args.max_differences:
            continue
        print(
            f"\nRecord {sequence} "
            f"(reference frame {reference_frame.get('frame')}, "
            f"port frame {port_frame.get('frame')}; "
            f"{len(differences)} semantic differences)"
        )
        for difference in differences:
            if reported >= args.max_differences:
                break
            print(f"  {difference}")
            reported += 1
    if mismatches:
        print(f"\nSemantic mismatch records: {mismatches}")
        return 1
    print("No semantic differences on shared records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
