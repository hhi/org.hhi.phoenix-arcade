#!/usr/bin/env python3
"""Generate a compact boot-flow view from annotated 8080 code and runtime calls."""

import argparse
import csv
import pathlib
import subprocess


BOOT_CALLS = (
    ("000F", "0050", "InitSoundScreen"),
    ("0017", "01D0", "PrintTextLines"),
)
INIT_CLEAR_CALLS = (
    ("005C", "006B"),
    ("0063", "006B"),
)


def runtime_edges(csv_path):
    """Read JPhoenix's aggregated raw CALL-site counts."""
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        return {
            (row["caller"], row["callee"]): int(row["count"])
            for row in csv.DictReader(csv_file)
        }


def render(dot_path, png_path, svg_path):
    """Render the boot flow for quick view and detailed inspection."""
    for extension, output_path in (("png", png_path), ("svg", svg_path)):
        subprocess.run(["dot", f"-T{extension}", str(dot_path), "-o", str(output_path)],
                       check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime = runtime_edges(pathlib.Path(args.runtime))
    init_count = runtime.get(("000F", "0050"), 0)
    text_count = runtime.get(("0017", "01D0"), 0)
    clear_count = sum(runtime.get(edge, 0) for edge in INIT_CLEAR_CALLS)

    dot_path = output_dir / "jphoenix_boot_flow.dot"
    with dot_path.open("w", encoding="utf-8") as dot_file:
        dot_file.write("digraph JPhoenixBoot { rankdir=LR; "
                       "node [shape=box, style=filled, fontname=\"Helvetica\"];\n")
        dot_file.write('boot [label="$0008\\nBoot entry\\nSet stack and video bank", fillcolor="#dbe7f3"];\n')
        dot_file.write('init [label="$0050\\nInitSoundScreen", fillcolor="#8fd3c7"];\n')
        dot_file.write('clear [label="$006B\\nClearRAMBank", fillcolor="#8fd3c7"];\n')
        dot_file.write('text [label="$01D0\\nPrintTextLines", fillcolor="#8fd3c7"];\n')
        dot_file.write('main [label="$001A\\nMainLoop", fillcolor="#ffd166"];\n')
        dot_file.write(f'boot -> init [color="#2a9d8f", penwidth=2, '
                       f'label="CALL $000F: {init_count}x"];\n')
        dot_file.write(f'init -> clear [color="#2a9d8f", penwidth=2, '
                       f'label="CALL $005C/$0063: {clear_count}x"];\n')
        dot_file.write(f'boot -> text [color="#2a9d8f", penwidth=2, '
                       f'label="CALL $0017: {text_count}x"];\n')
        dot_file.write('text -> main [color="#457b9d", style=dashed, penwidth=2, '
                       'label="RET, then fall-through to $001A"];\n')
        dot_file.write('boot_legend [shape=plain, label=<\n')
        dot_file.write('<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n')
        dot_file.write('<TR><TD COLSPAN="2"><B>Boot-flow legend</B></TD></TR>\n')
        dot_file.write('<TR><TD BGCOLOR="#2a9d8f"> </TD>'
                       '<TD ALIGN="LEFT">solid green: measured runtime CALL</TD></TR>\n')
        dot_file.write('<TR><TD BGCOLOR="#457b9d"> </TD>'
                       '<TD ALIGN="LEFT">dashed blue: documented non-CALL control flow</TD></TR>\n')
        dot_file.write('</TABLE>>];\n')
        dot_file.write("}\n")
    render(dot_path,
           output_dir / "jphoenix_boot_flow.png",
           output_dir / "jphoenix_boot_flow.svg")

    with (output_dir / "jphoenix_boot_flow.md").open("w", encoding="utf-8") as report:
        report.write("# JPhoenix 8080 boot flow\n\n")
        report.write("The boot view combines measured CALL counts with one explicit "
                     "non-CALL control-flow transition. It is intentionally separate "
                     "from the runtime CALL graph.\n\n")
        report.write("1. `$0008`: set stack pointer and select video RAM bank 0.\n")
        report.write(f"2. `$000F`: call `InitSoundScreen` ({init_count}x).\n")
        report.write(f"3. `InitSoundScreen`: clear both RAM banks via `ClearRAMBank` ({clear_count}x).\n")
        report.write(f"4. `$0017`: call `PrintTextLines` ({text_count}x).\n")
        report.write("5. After `RET`, execution falls through to `$001A MainLoop`.\n\n")
        report.write("![Boot flow](jphoenix_boot_flow.svg)\n")

    print("JPhoenix boot flow: "
          f"InitSoundScreen {init_count}x, ClearRAMBank {clear_count}x, "
          f"PrintTextLines {text_count}x")


if __name__ == "__main__":
    main()
