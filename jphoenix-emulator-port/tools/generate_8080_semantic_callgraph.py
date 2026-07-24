#!/usr/bin/env python3
"""Render semantic 8080 routine graphs from raw JPhoenix CALL-site traces."""

import argparse
import bisect
import collections
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
    """Return annotated code labels, excluding table-only Txxxx labels."""
    labels = {}
    pending = None
    for line in asm_path.read_text(encoding="utf-8").splitlines():
        match = LABEL.match(line)
        if match:
            pending = match.group(1)
            continue
        match = ADDRESS.match(line)
        if pending and match:
            if not pending.startswith("T"):
                labels[match.group(1)] = pending
            pending = None
    return labels


def static_edges(asm_path):
    """Return direct and conditional static 8080 CALL instruction edges."""
    return {
        (match.group(1), match.group(2))
        for line in asm_path.read_text(encoding="utf-8").splitlines()
        if (match := CALL.match(line))
    }


def runtime_edges(csv_path):
    """Read aggregated raw CALL-site counts from JPhoenix."""
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        return {
            (row["caller"], row["callee"]): int(row["count"])
            for row in csv.DictReader(csv_file)
        }


def routine_lookup(labels):
    """Map an address to the nearest preceding annotated code-routine label."""
    entries = sorted((int(address, 16), address, label)
                     for address, label in labels.items())
    addresses = [entry[0] for entry in entries]

    def lookup(address):
        target = int(address, 16)
        index = bisect.bisect_right(addresses, target) - 1
        if index < 0:
            return address, labels.get(address, "L" + address)
        _, routine_address, routine_label = entries[index]
        return routine_address, routine_label

    return lookup


def semantic_edges(edges, lookup):
    """Aggregate raw callsites into caller-routine to callee-routine edges."""
    counts = collections.Counter()
    for (caller, callee), count in edges.items():
        caller_routine = lookup(caller)
        callee_routine = lookup(callee)
        counts[caller_routine, callee_routine] += count
    return counts


def node_id(routine):
    """Use routine address and label as a stable semantic graph node."""
    address, label = routine
    return "$" + address + "\\n" + label


def heat_bands(values):
    """Split positive incoming-call counts into replay-specific quantile bands."""
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
    """Return the colour for a measured incoming-call count."""
    if value <= 0:
        return ZERO_HEAT_COLOR
    for color, _, upper in bands:
        if value <= upper:
            return color
    return bands[-1][0]


def write_legend(dot_file, bands, comparison):
    """Embed the heatmap and optional comparison-edge legend in DOT."""
    dot_file.write('semantic_legend [shape=plain, label=<\n')
    dot_file.write('<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n')
    dot_file.write('<TR><TD COLSPAN="2"><B>Semantic routine graph legend</B></TD></TR>\n')
    dot_file.write(f'<TR><TD BGCOLOR="{ZERO_HEAT_COLOR}"> </TD>'
                   '<TD ALIGN="LEFT">no incoming runtime CALLs</TD></TR>\n')
    for color, lower, upper in bands:
        dot_file.write(f'<TR><TD BGCOLOR="{color}"> </TD>'
                       f'<TD ALIGN="LEFT">incoming CALLs: {lower} - {upper}</TD></TR>\n')
    if comparison:
        dot_file.write('<TR><TD BGCOLOR="#2a9d8f"> </TD>'
                       '<TD ALIGN="LEFT">solid green: static and executed</TD></TR>\n')
        dot_file.write('<TR><TD BGCOLOR="#9aa0a6"> </TD>'
                       '<TD ALIGN="LEFT">dashed grey: static, not executed</TD></TR>\n')
        dot_file.write('<TR><TD BGCOLOR="#e76f51"> </TD>'
                       '<TD ALIGN="LEFT">solid red: runtime-only</TD></TR>\n')
    else:
        dot_file.write('<TR><TD ALIGN="LEFT" COLSPAN="2">edge label = calls; '
                       'edge width = relative call frequency</TD></TR>\n')
    dot_file.write('</TABLE>>];\n')


def render(dot_path, png_path, svg_path):
    """Render a DOT graph in both quick-view and zoomable formats."""
    for extension, output_path in (("png", png_path), ("svg", svg_path)):
        subprocess.run(["dot", f"-T{extension}", str(dot_path), "-o", str(output_path)],
                       check=True)


def write_runtime_graph(output_dir, counts):
    """Write the semantic runtime routine graph and its aggregated CSV."""
    incoming = collections.Counter()
    for (_, callee), count in counts.items():
        incoming[callee] += count
    bands = heat_bands(incoming.values())
    nodes = sorted({routine for edge in counts for routine in edge})
    maximum = max(counts.values(), default=1)
    dot_path = output_dir / "jphoenix_semantic_runtime_callgraph.dot"
    with dot_path.open("w", encoding="utf-8") as dot_file:
        dot_file.write("digraph JPhoenixSemanticRuntime { rankdir=LR; "
                       "node [shape=box, style=filled];\n")
        for routine in nodes:
            dot_file.write(f'"{node_id(routine)}" '
                           f'[fillcolor="{heat_color(incoming[routine], bands)}"];\n')
        for (caller, callee), count in sorted(counts.items()):
            width = 1 + 5 * count / maximum
            dot_file.write(f'"{node_id(caller)}" -> "{node_id(callee)}" '
                           f'[label="{count}", penwidth="{width:.2f}"];\n')
        write_legend(dot_file, bands, comparison=False)
        dot_file.write("}\n")
    render(dot_path,
           output_dir / "jphoenix_semantic_runtime_callgraph.png",
           output_dir / "jphoenix_semantic_runtime_callgraph.svg")
    with (output_dir / "jphoenix_semantic_runtime_calls.csv").open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["caller_address", "caller_label", "callee_address", "callee_label", "count"])
        for (caller, callee), count in sorted(counts.items()):
            writer.writerow([caller[0], caller[1], callee[0], callee[1], count])


def write_comparison(output_dir, static, runtime):
    """Write semantic static-versus-runtime comparison artefacts."""
    static_edges_set = set(static)
    runtime_edges_set = set(runtime)
    hit = static_edges_set & runtime_edges_set
    static_only = static_edges_set - runtime_edges_set
    runtime_only = runtime_edges_set - static_edges_set
    incoming = collections.Counter()
    for (_, callee), count in runtime.items():
        incoming[callee] += count
    bands = heat_bands(incoming.values())
    nodes = sorted({routine for edge in static_edges_set | runtime_edges_set for routine in edge})
    dot_path = output_dir / "jphoenix_semantic_design_runtime_comparison.dot"
    with dot_path.open("w", encoding="utf-8") as dot_file:
        dot_file.write("digraph JPhoenixSemanticComparison { rankdir=LR; "
                       "node [shape=box, style=filled];\n")
        for routine in nodes:
            dot_file.write(f'"{node_id(routine)}" '
                           f'[fillcolor="{heat_color(incoming[routine], bands)}"];\n')
        for caller, callee in sorted(hit):
            dot_file.write(f'"{node_id(caller)}" -> "{node_id(callee)}" '
                           f'[color="#2a9d8f", penwidth=2, label="{runtime[(caller, callee)]}"];\n')
        for caller, callee in sorted(static_only):
            dot_file.write(f'"{node_id(caller)}" -> "{node_id(callee)}" '
                           '[color="#9aa0a6", style=dashed];\n')
        for caller, callee in sorted(runtime_only):
            dot_file.write(f'"{node_id(caller)}" -> "{node_id(callee)}" '
                           f'[color="#e76f51", penwidth=2, label="{runtime[(caller, callee)]}"];\n')
        write_legend(dot_file, bands, comparison=True)
        dot_file.write("}\n")
    render(dot_path,
           output_dir / "jphoenix_semantic_design_runtime_comparison.png",
           output_dir / "jphoenix_semantic_design_runtime_comparison.svg")
    with (output_dir / "jphoenix_semantic_design_runtime_report.md").open(
        "w", encoding="utf-8"
    ) as report:
        report.write("# JPhoenix: semantic 8080 routine design versus runtime\n\n")
        report.write("Raw CALL sites are grouped by their nearest preceding annotated "
                     "code label. Raw callsite CSV remains available for verification.\n\n")
        report.write("| Measure | Count |\n| --- | ---: |\n")
        report.write(f"| Static routine edges | {len(static_edges_set)} |\n")
        report.write(f"| Executed routine edges | {len(runtime_edges_set)} |\n")
        report.write(f"| Hit routine edges | {len(hit)} |\n")
        report.write(f"| Static-only routine edges | {len(static_only)} |\n")
        report.write(f"| Runtime-only routine edges | {len(runtime_only)} |\n\n")
        report.write("![Semantic comparison](jphoenix_semantic_design_runtime_comparison.svg)\n")
    return len(hit), len(static_only), len(runtime_only)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asm", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    asm_path = pathlib.Path(args.asm)
    output_dir = pathlib.Path(args.output_dir)
    labels = read_labels(asm_path)
    lookup = routine_lookup(labels)
    runtime = semantic_edges(runtime_edges(pathlib.Path(args.runtime)), lookup)
    static = semantic_edges({edge: 1 for edge in static_edges(asm_path)}, lookup)
    write_runtime_graph(output_dir, runtime)
    hit, static_only, runtime_only = write_comparison(output_dir, static, runtime)
    print("JPhoenix semantic 8080 design/runtime: "
          f"{hit} hit, {static_only} static-only, {runtime_only} runtime-only")


if __name__ == "__main__":
    main()
