#!/usr/bin/env python3
"""Generate a C function call graph from an aggregated runtime trace."""

import argparse
import bisect
import collections
import csv
import pathlib
import struct
import subprocess


TRACE_MAGIC = b"CPHXCG01"
HEADER = struct.Struct("=8sQQII")
EDGE = struct.Struct("=QQQ")
HEAT_COLORS = ("#dbe7f3", "#8fd3c7", "#b8de6f", "#ffd166", "#e76f51")
ZERO_HEAT_COLOR = "#eceff1"


def read_symbols(binary_path):
    """Return sorted executable symbol addresses and their C names."""
    output = subprocess.check_output(["nm", "-n", binary_path], text=True)
    rows = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            rows.append((int(parts[0], 16), parts[2].lstrip("_")))
        except ValueError:
            continue
    return rows, [address for address, _ in rows]


def symbol_name(rows, addresses, address):
    """Resolve an in-process address to the closest preceding symbol."""
    index = bisect.bisect_right(addresses, address) - 1
    return rows[index][1] if index >= 0 else None


def read_trace(trace_path):
    """Read the compact edge records emitted by runtime_call_trace.c."""
    with trace_path.open("rb") as trace_file:
        raw_header = trace_file.read(HEADER.size)
        if len(raw_header) != HEADER.size:
            raise ValueError("runtime trace has no complete header")
        magic, runtime_start, dropped_edges, edge_count, _ = HEADER.unpack(raw_header)
        if magic != TRACE_MAGIC:
            raise ValueError("unsupported runtime trace format")
        edges = []
        for _ in range(edge_count):
            raw_edge = trace_file.read(EDGE.size)
            if len(raw_edge) != EDGE.size:
                raise ValueError("runtime trace ends before all edge records")
            edges.append(EDGE.unpack(raw_edge))
    return runtime_start, dropped_edges, edges


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


def write_legend(dot_file, bands):
    """Embed a self-contained heatmap and edge-frequency legend in DOT."""
    dot_file.write('runtime_legend [shape=plain, label=<\n')
    dot_file.write('<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n')
    dot_file.write('<TR><TD COLSPAN="2"><B>Runtime legend</B></TD></TR>\n')
    dot_file.write(
        f'<TR><TD BGCOLOR="{ZERO_HEAT_COLOR}"> </TD>'
        '<TD ALIGN="LEFT">no incoming runtime calls</TD></TR>\n'
    )
    for color, lower, upper in bands:
        dot_file.write(
            f'<TR><TD BGCOLOR="{color}"> </TD>'
            f'<TD ALIGN="LEFT">incoming calls: {lower} - {upper}</TD></TR>\n'
        )
    dot_file.write(
        '<TR><TD ALIGN="LEFT" COLSPAN="2">edge label = calls; '
        'edge width = relative call frequency</TD></TR>\n'
    )
    dot_file.write('</TABLE>>];\n')


def write_graph(output_dir, counts):
    """Write DOT, SVG, and PNG call graph files."""
    dot_path = output_dir / "c_phoenix_runtime_callgraph.dot"
    max_count = max(counts.values(), default=1)
    incoming = collections.Counter()
    for (_, callee), count in counts.items():
        incoming[callee] += count
    nodes = sorted({function for edge in counts for function in edge})
    bands = heat_bands(incoming.values())
    with dot_path.open("w") as dot_file:
        dot_file.write(
            "digraph C { rankdir=LR; "
            "node [shape=box, style=filled, fillcolor=\"#dbe7f3\"];\n"
        )
        for node in nodes:
            dot_file.write(
                f'"{node}" [fillcolor="{heat_color(incoming[node], bands)}"];\n'
            )
        for (caller, callee), count in sorted(counts.items()):
            width = 1.0 + (5.0 * count / max_count)
            dot_file.write(
                f'"{caller}" -> "{callee}" '
                f'[label="{count}", penwidth="{width:.2f}"];\n'
            )
        write_legend(dot_file, bands)
        dot_file.write("}\n")
    subprocess.run(
        ["dot", "-Tsvg", str(dot_path), "-o", str(output_dir / "c_phoenix_runtime_callgraph.svg")],
        check=True,
    )
    subprocess.run(
        ["dot", "-Tpng", str(dot_path), "-o", str(output_dir / "c_phoenix_runtime_callgraph.png")],
        check=True,
    )


def write_csv(output_dir, counts):
    """Write resolved runtime edges for further design/runtime analysis."""
    with (output_dir / "c_phoenix_runtime_calls.csv").open(
        "w", newline="", encoding="utf-8"
    ) as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["caller", "callee", "count"])
        for (caller, callee), count in sorted(counts.items()):
            writer.writerow([caller, callee, count])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace")
    parser.add_argument("--binary", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    trace_path = pathlib.Path(args.trace)
    output_dir = pathlib.Path(args.output_dir)
    rows, addresses = read_symbols(args.binary)
    runtime_start, dropped_edges, edges = read_trace(trace_path)
    static_start = next(
        address for address, name in rows if name == "runtime_call_trace_start"
    )
    address_slide = runtime_start - static_start
    counts = collections.Counter()
    for caller, callee, count in edges:
        caller_name = symbol_name(rows, addresses, caller - address_slide)
        callee_name = symbol_name(rows, addresses, callee - address_slide)
        if caller_name and callee_name:
            counts[caller_name, callee_name] += count

    output_dir.mkdir(parents=True, exist_ok=True)
    write_graph(output_dir, counts)
    write_csv(output_dir, counts)
    print(f"Executed C call edges: {len(counts)}")
    if dropped_edges:
        print(f"Dropped unique edges: {dropped_edges}")


if __name__ == "__main__":
    main()
