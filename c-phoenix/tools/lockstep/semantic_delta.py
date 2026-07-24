#!/usr/bin/env python3
"""Extract a small, symbolised RAM-transition window from a lockstep dump pair."""

import argparse
import json
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

from compare_ram_dumps import BASE, read_frames, symbol  # noqa: E402


def parse_regions(spec: str) -> list[tuple[int, int]]:
    regions = []
    for part in spec.split(","):
        lo, hi = part.split("-", 1)
        regions.append((int(lo, 16), int(hi, 16)))
    return regions


def changed_bytes(before: bytes, after: bytes, regions: list[tuple[int, int]]) -> list[dict]:
    changes = []
    for lo, hi in regions:
        for address in range(lo, hi + 1):
            offset = address - BASE
            if before[offset] != after[offset]:
                changes.append({
                    "address": f"0x{address:04X}",
                    "symbol": symbol(address),
                    "before": before[offset],
                    "after": after[offset],
                })
    return changes


def parity_diffs(reference: bytes, port: bytes, regions: list[tuple[int, int]]) -> list[dict]:
    diffs = []
    for lo, hi in regions:
        for address in range(lo, hi + 1):
            offset = address - BASE
            if reference[offset] != port[offset]:
                diffs.append({
                    "address": f"0x{address:04X}",
                    "symbol": symbol(address),
                    "reference": reference[offset],
                    "port": port[offset],
                })
    return diffs


def to_hex(value: int) -> str:
    return f"0x{value:02X}"


def write_markdown(path: Path, report: dict) -> None:
    lines = [
        "# Semantisch RAM-deltavenster",
        "",
        f"- Records: `{report['window'][0]}..{report['window'][1]}`",
        f"- Regio's: `{report['regions']}`",
        "",
    ]
    for frame in report["frames"]:
        lines.extend([
            f"## Record {frame['record_index']}",
            "",
            f"Referentieframe `{frame['reference_frame']}`, portframe `{frame['port_frame']}`.",
            "",
        ])
        for title, changes, value_names in (
            ("Referentie-mutaties", frame["reference_changes"], ("before", "after")),
            ("Port-mutaties", frame["port_changes"], ("before", "after")),
            ("Parity-diffs", frame["parity_diffs"], ("reference", "port")),
        ):
            lines.extend([f"### {title}", ""])
            if not changes:
                lines.extend(["Geen.", ""])
                continue
            lines.extend(["| Adres | Veld | Van | Naar |", "| --- | --- | --- | --- |"])
            for change in changes:
                lines.append(
                    f"| `{change['address']}` | {change['symbol']} | "
                    f"`{to_hex(change[value_names[0]])}` | `{to_hex(change[value_names[1]])}` |"
                )
            lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", help="jphoenix RAM-dump")
    parser.add_argument("port", help="c-phoenix RAM-dump")
    parser.add_argument("--record", type=int, required=True,
                        help="centrale record-index, na eventuele offsets")
    parser.add_argument("--window", type=int, default=1,
                        help="aantal records voor en na --record (standaard 1)")
    parser.add_argument("--offset-ref", type=int, default=0)
    parser.add_argument("--offset-port", type=int, default=0)
    parser.add_argument("--regions", default="4340-43FF,4B40-4BE5",
                        help="komma-gescheiden hexbereiken, bijvoorbeeld 43A0-43C7")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    reference = read_frames(args.reference, args.offset_ref)
    port = read_frames(args.port, args.offset_port)
    regions = parse_regions(args.regions)
    if args.record <= 0:
        parser.error("--record moet ten minste 1 zijn, omdat record N-1 nodig is")
    start = max(1, args.record - args.window)
    end = min(len(reference), len(port)) - 1
    end = min(end, args.record + args.window)
    if start > end:
        parser.error("het gekozen record ligt buiten de gemeenschappelijke dumps")

    frames = []
    for record_index in range(start, end + 1):
        ref_frame, ref_ram = reference[record_index]
        port_frame, port_ram = port[record_index]
        _, ref_before = reference[record_index - 1]
        _, port_before = port[record_index - 1]
        frames.append({
            "record_index": record_index,
            "reference_frame": ref_frame,
            "port_frame": port_frame,
            "reference_changes": changed_bytes(ref_before, ref_ram, regions),
            "port_changes": changed_bytes(port_before, port_ram, regions),
            "parity_diffs": parity_diffs(ref_ram, port_ram, regions),
        })

    report = {
        "reference": str(Path(args.reference)),
        "port": str(Path(args.port)),
        "window": [start, end],
        "regions": args.regions,
        "frames": frames,
    }
    json_path = Path(args.output_json)
    md_path = Path(args.output_md)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_markdown(md_path, report)
    print(f"geschreven: {json_path}")
    print(f"geschreven: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
