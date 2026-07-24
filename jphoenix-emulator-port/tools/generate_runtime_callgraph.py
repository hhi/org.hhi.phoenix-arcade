#!/usr/bin/env python3
"""Render an aggregated JPhoenix runtime CALL trace as DOT, SVG, and Markdown."""
import argparse
import csv
import pathlib
import re
import subprocess


HEAT_COLORS = ("#dbe7f3", "#8fd3c7", "#b8de6f", "#ffd166", "#e76f51")


def read_labels(path):
    labels = {}
    pending = None
    source = pathlib.Path(path)
    for line in source.read_text(encoding="utf-8").splitlines():
        if source.suffix == ".asm":
            heading = re.match(r"^([A-Za-z][A-Za-z0-9_]*):$", line)
        else:
            heading = re.match(r"^### (.+):$", line)
        if heading:
            pending = heading.group(1)
            continue
        address = re.match(r"^([0-9A-F]{4}):", line)
        if pending and address:
            labels[address.group(1)] = pending
            pending = None
    return labels


def heat_bands(values):
    """Split positive incoming CALL counts into replay-specific quantile bands."""
    positive = sorted(value for value in values if value > 0)
    if not positive:
        return []
    bands = []
    lower = positive[0]
    for color, quantile in zip(HEAT_COLORS, (0.20, 0.40, 0.60, 0.80, 1.00)):
        upper = positive[round((len(positive) - 1) * quantile)]
        if upper >= lower:
            bands.append((color, lower, upper))
            lower = upper + 1
    return bands


def heat_color(value, bands):
    """Return the colour for a measured incoming CALL count."""
    if value <= 0:
        return "#eceff1"
    for color, _, upper in bands:
        if value <= upper:
            return color
    return bands[-1][0]


def write_legend(handle, bands):
    """Embed heatmap and edge-frequency meanings in the runtime graph."""
    handle.write('runtime_legend [shape=plain, label=<\n')
    handle.write('<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n')
    handle.write('<TR><TD COLSPAN="2"><B>Runtime legend</B></TD></TR>\n')
    for color, lower, upper in bands:
        handle.write(f'<TR><TD BGCOLOR="{color}"> </TD>'
                     f'<TD ALIGN="LEFT">incoming CALLs: {lower} - {upper}</TD></TR>\n')
    handle.write('<TR><TD ALIGN="LEFT" COLSPAN="2">edge label = calls; '
                 'edge width = relative call frequency</TD></TR>\n')
    handle.write('</TABLE>>];\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--title", default="JPhoenix runtime call graph")
    parser.add_argument("--labels", help="code-annotated.asm label source")
    args = parser.parse_args()
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    labels = read_labels(args.labels) if args.labels else {}
    with open(args.trace, newline="", encoding="utf-8") as handle:
        edges = [(row["caller"], row["callee"], int(row["count"]))
                 for row in csv.DictReader(handle)]
    incoming = {}
    for _, callee, count in edges:
        incoming[callee] = incoming.get(callee, 0) + count
    bands = heat_bands(incoming.values())
    dot = output_dir / "jphoenix_runtime_callgraph.dot"
    with dot.open("w", encoding="utf-8") as handle:
        handle.write("digraph RuntimeCallGraph {\nrankdir=LR;\n")
        handle.write('node [shape=box, style="filled", fontname="Helvetica"];\n')
        for address, count in incoming.items():
            label = "$" + address + ("\\n" + labels[address] if address in labels else "")
            handle.write(f'"{label}" [fillcolor="{heat_color(count, bands)}"];\n')
        for caller, callee, count in edges:
            caller_label = "$" + caller + ("\\n" + labels[caller] if caller in labels else "")
            callee_label = "$" + callee + ("\\n" + labels[callee] if callee in labels else "")
            width = 1 + 5 * (count / max(count for _, _, count in edges))
            handle.write(f'"{caller_label}" -> "{callee_label}" [label="{count}", penwidth="{width:.2f}"];\n')
        write_legend(handle, bands)
        handle.write("}\n")
    subprocess.run(["dot", "-Tsvg", str(dot), "-o",
                    str(output_dir / "jphoenix_runtime_callgraph.svg")], check=True)
    with (output_dir / "jphoenix_runtime_callgraph.md").open("w", encoding="utf-8") as handle:
        handle.write(f"# {args.title}\n\nExecuted CALL edges: **{len(edges)}**.\n\n")
        handle.write("The graph legend gives the replay-specific node heatmap ranges. "
                     "Edge thickness follows the edge call count.\n\n")
        handle.write("| Caller | Callee | Calls |\n| --- | --- | ---: |\n")
        for caller, callee, count in sorted(edges, key=lambda edge: -edge[2]):
            handle.write(f"| `${caller}` | `${callee}` | {count} |\n")
        handle.write("\n![Runtime call graph](jphoenix_runtime_callgraph.svg)\n")


if __name__ == "__main__":
    main()
