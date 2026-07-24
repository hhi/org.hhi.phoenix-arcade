#!/usr/bin/env python3
"""Compare static 8080 CALL instructions with JPhoenix runtime CALL edges."""

import argparse
import csv
import pathlib
import re
import subprocess


LABEL = re.compile(r"^([A-Za-z][A-Za-z0-9_]*):$")
ADDRESS = re.compile(r"^([0-9A-F]{4}):")
CALL = re.compile(
    r"^([0-9A-F]{4}):.*\bCALL(?:\s+(?:NZ|Z|NC|C)\s*,)?\s*\$([0-9A-F]{4})"
)
HEAT_COLORS = ("#dbe7f3", "#8fd3c7", "#b8de6f", "#ffd166", "#e76f51")
ZERO_HEAT_COLOR = "#eceff1"


def read_labels(asm_path):
    """Map function-entry ROM addresses to annotated ASM labels."""
    labels = {}
    pending = None
    for line in asm_path.read_text(encoding="utf-8").splitlines():
        match = LABEL.match(line)
        if match:
            pending = match.group(1)
            continue
        match = ADDRESS.match(line)
        if pending and match:
            labels[match.group(1)] = pending
            pending = None
    return labels


def static_edges(asm_path):
    """Return all direct and conditional static CALL instruction edges."""
    return {
        (match.group(1), match.group(2))
        for line in asm_path.read_text(encoding="utf-8").splitlines()
        if (match := CALL.match(line))
    }


def runtime_edges(csv_path):
    """Read aggregated CALL counts emitted by the JPhoenix emulator."""
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        return {
            (row["caller"], row["callee"]): int(row["count"])
            for row in csv.DictReader(csv_file)
        }


def edge_label(edge, labels):
    """Format an edge endpoint without inventing labels for unknown addresses."""
    address = edge.upper()
    return "$" + address + ("\\n" + labels[address] if address in labels else "")


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
        return ZERO_HEAT_COLOR
    for color, _, upper in bands:
        if value <= upper:
            return color
    return bands[-1][0]


def write_legend(dot_file, bands):
    """Embed heatmap and design/runtime edge meanings in the graph."""
    dot_file.write('comparison_legend [shape=plain, label=<\n')
    dot_file.write('<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n')
    dot_file.write('<TR><TD COLSPAN="2"><B>Legend</B></TD></TR>\n')
    dot_file.write(f'<TR><TD BGCOLOR="{ZERO_HEAT_COLOR}"> </TD>'
                   '<TD ALIGN="LEFT">node: no incoming runtime CALLs</TD></TR>\n')
    for color, lower, upper in bands:
        dot_file.write(f'<TR><TD BGCOLOR="{color}"> </TD>'
                       f'<TD ALIGN="LEFT">node incoming CALLs: {lower} - {upper}</TD></TR>\n')
    dot_file.write('<TR><TD BGCOLOR="#2a9d8f"> </TD>'
                   '<TD ALIGN="LEFT">solid green: static and executed</TD></TR>\n')
    dot_file.write('<TR><TD BGCOLOR="#9aa0a6"> </TD>'
                   '<TD ALIGN="LEFT">dashed grey: static, not executed</TD></TR>\n')
    dot_file.write('<TR><TD BGCOLOR="#e76f51"> </TD>'
                   '<TD ALIGN="LEFT">solid red: runtime-only</TD></TR>\n')
    dot_file.write('</TABLE>>];\n')


def write_outputs(output_dir, labels, static, runtime):
    """Write CSV, report, and colour-coded design/runtime callgraph."""
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime_edge_set = set(runtime)
    hit = static & runtime_edge_set
    static_only = static - runtime_edge_set
    runtime_only = runtime_edge_set - static
    incoming = {}
    for (_, callee), count in runtime.items():
        incoming[callee] = incoming.get(callee, 0) + count
    bands = heat_bands(incoming.values())

    with (output_dir / "jphoenix_design_runtime_edges.csv").open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["caller", "callee", "status", "runtime_calls"])
        for edge in sorted(hit):
            writer.writerow([*edge, "hit", runtime[edge]])
        for edge in sorted(static_only):
            writer.writerow([*edge, "static_only", 0])
        for edge in sorted(runtime_only):
            writer.writerow([*edge, "runtime_only", runtime[edge]])

    dot_path = output_dir / "jphoenix_design_runtime_comparison.dot"
    with dot_path.open("w", encoding="utf-8") as dot_file:
        dot_file.write(
            "digraph JPhoenixDesignRuntime { rankdir=LR; "
            "node [shape=box, style=filled, fillcolor=\"#f4f4f4\"];\n"
        )
        nodes = sorted({address for edge in static | runtime_edge_set for address in edge})
        for address in nodes:
            dot_file.write(
                f'"{edge_label(address, labels)}" '
                f'[fillcolor="{heat_color(incoming.get(address, 0), bands)}"];\n'
            )
        for caller, callee in sorted(hit):
            dot_file.write(
                f'"{edge_label(caller, labels)}" -> "{edge_label(callee, labels)}" '
                f'[color="#2a9d8f", penwidth=2, label="{runtime[(caller, callee)]}"];\n'
            )
        for caller, callee in sorted(static_only):
            dot_file.write(
                f'"{edge_label(caller, labels)}" -> "{edge_label(callee, labels)}" '
                '[color="#9aa0a6", style=dashed];\n'
            )
        for caller, callee in sorted(runtime_only):
            dot_file.write(
                f'"{edge_label(caller, labels)}" -> "{edge_label(callee, labels)}" '
                f'[color="#e76f51", penwidth=2, label="{runtime[(caller, callee)]}"];\n'
            )
        write_legend(dot_file, bands)
        dot_file.write("}\n")
    for extension in ("svg", "png"):
        subprocess.run(
            ["dot", f"-T{extension}", str(dot_path), "-o",
             str(output_dir / f"jphoenix_design_runtime_comparison.{extension}")],
            check=True,
        )

    with (output_dir / "jphoenix_design_runtime_report.md").open(
        "w", encoding="utf-8"
    ) as report:
        report.write("# JPhoenix: static 8080 CALL versus runtime CALL\n\n")
        report.write("| Measure | Count |\n| --- | ---: |\n")
        report.write(f"| Static 8080 CALL instructions | {len(static)} |\n")
        report.write(f"| Executed runtime CALL edges | {len(runtime_edge_set)} |\n")
        report.write(f"| Hit static CALL edges | {len(hit)} |\n")
        report.write(f"| Static-only CALL edges | {len(static_only)} |\n")
        report.write(f"| Runtime-only CALL edges | {len(runtime_only)} |\n\n")
        report.write(
            "Nodes use replay-specific incoming-CALL heatmap bands shown in the "
            "graph legend. Green edges are static 8080 CALL instructions executed during this "
            "replay. Dashed grey CALLs exist in ROM but were not taken. Red "
            "runtime-only CALLs indicate an annotation/parser discrepancy and "
            "should be investigated.\n\n"
        )
        report.write("![Comparison graph](jphoenix_design_runtime_comparison.svg)\n")

    return len(hit), len(static_only), len(runtime_only)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asm", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    asm_path = pathlib.Path(args.asm)
    hit, static_only, runtime_only = write_outputs(
        pathlib.Path(args.output_dir),
        read_labels(asm_path),
        static_edges(asm_path),
        runtime_edges(pathlib.Path(args.runtime)),
    )
    print(
        "JPhoenix 8080 design/runtime: "
        f"{hit} hit, {static_only} static-only, {runtime_only} runtime-only"
    )


if __name__ == "__main__":
    main()
