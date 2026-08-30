#!/usr/bin/env python3
"""Generate the byte-complete technical listing from Phoenix.lst and annotations."""
import argparse, json, re, sys
from pathlib import Path

LISTING = re.compile(r"^(\d+)\s+([0-9A-Fa-f]{4})\s+((?:[0-9A-Fa-f]{2}\s*)+)\s+(.*)$")


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--listing", type=Path, default=root / "context/Phoenix.lst")
    parser.add_argument("--rom", type=Path, default=root.parent / "roms/assembled/program.rom")
    parser.add_argument("--annotations", type=Path, default=root / "context/asm-annotations.yaml")
    parser.add_argument("--output", type=Path, default=root / "context/code-annotated.asm")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.annotations.read_text(encoding="utf-8"))
    labels = {item["address"]: item["names"] for item in data["labels"]}
    notes = {item["address"]: item for item in data["notes"]}
    rom = args.rom.read_bytes()
    records, covered = {}, set()
    previous_line = previous_address = None
    for line in args.listing.read_text(encoding="utf-8").splitlines():
        if not (match := LISTING.match(line)):
            continue
        line_number, address = int(match.group(1)), int(match.group(2), 16)
        bytes_text, instruction = match.group(3).split(), match.group(4).partition(";")[0].rstrip()
        if line_number == previous_line and re.fullmatch(r"[0-9A-Fa-f ]+", instruction):
            bytes_text.extend(instruction.split())
            records[previous_address][0].extend(bytes_text)
            covered.update(range(address, address + len(bytes_text)))
            continue
        records[address] = (bytes_text, instruction)
        covered.update(range(address, address + len(bytes_text)))
        previous_line, previous_address = line_number, address
    output = ["; Generated from Phoenix.lst, program.rom, and asm-annotations.yaml.", ""]
    address = 0
    while address < len(rom):
        for name in labels.get(f"{address:04x}", []):
            output.append(name + ":")
        if address in records:
            values, instruction = records[address]
            size = len(values)
        else:
            values, instruction, size = [f"{rom[address]:02X}"], ".DB $" + f"{rom[address]:02X}", 1
        comment = notes.get(f"{address:04x}", {}).get("comment", "")
        output.append((f"{address:04X}: {' '.join(values):<15} {instruction}" + (f" ; {comment}" if comment else "")).rstrip())
        address += size
    rendered = "\n".join(output) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"{args.output} is stale; run tools/generate_code_annotated_asm.py", file=sys.stderr)
            return 1
    else:
        args.output.write_text(rendered, encoding="utf-8")
    print(f"Generated {args.output}: {len(records)} Phoenix listing records, {len(rom)-len(covered)} ROM fallback bytes")


if __name__ == "__main__":
    main()
