#!/usr/bin/env python3
"""Compare C source call candidates against an executed C call trace."""

import argparse
import collections
import csv
import pathlib
import re
import subprocess


FUNCTION_DEFINITION = re.compile(
    r"(?m)^(?:static\s+)?(?:[A-Za-z_]\w*\s*\**\s+)+"
    r"(?P<name>[A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{"
)
CALL = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
COMMENT_OR_STRING = re.compile(
    r"//[^\n]*|/\*.*?\*/|\"(?:\\.|[^\"\\])*\"", re.DOTALL
)
HEAT_COLORS = ("#dbe7f3", "#8fd3c7", "#b8de6f", "#ffd166", "#e76f51")
ZERO_HEAT_COLOR = "#eceff1"


def function_bodies(source):
    """Yield function names and their braced bodies from a C source string."""
    for match in FUNCTION_DEFINITION.finditer(source):
        depth = 1
        index = match.end()
        while index < len(source) and depth:
            if source[index] == "{":
                depth += 1
            elif source[index] == "}":
                depth -= 1
            index += 1
        if depth == 0:
            yield match.group("name"), source[match.end():index - 1]


def static_edges(source_dir):
    """Extract direct calls between locally defined functions."""
    bodies = []
    functions = set()
    for source_path in sorted(source_dir.glob("*.c")):
        source = source_path.read_text(encoding="utf-8")
        for name, body in function_bodies(source):
            functions.add(name)
            bodies.append((name, body))

    edges = set()
    for caller, body in bodies:
        clean_body = COMMENT_OR_STRING.sub("", body)
        for callee in CALL.findall(clean_body):
            if callee in functions:
                edges.add((caller, callee))
    return functions, edges


def runtime_edges(csv_path):
    """Read the resolved C runtime edge counts."""
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        return {
            (row["caller"], row["callee"]): int(row["count"])
            for row in csv.DictReader(csv_file)
        }


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
    """Embed heatmap and design/runtime edge meanings in the graph."""
    dot_file.write('comparison_legend [shape=plain, label=<\n')
    dot_file.write('<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">\n')
    dot_file.write('<TR><TD COLSPAN="2"><B>Legend</B></TD></TR>\n')
    dot_file.write(
        f'<TR><TD BGCOLOR="{ZERO_HEAT_COLOR}"> </TD>'
        '<TD ALIGN="LEFT">node: no incoming runtime calls</TD></TR>\n'
    )
    for color, lower, upper in bands:
        dot_file.write(
            f'<TR><TD BGCOLOR="{color}"> </TD>'
            f'<TD ALIGN="LEFT">node incoming calls: {lower} - {upper}</TD></TR>\n'
        )
    dot_file.write('<TR><TD BGCOLOR="#2a9d8f"> </TD>'
                   '<TD ALIGN="LEFT">solid green: static and executed</TD></TR>\n')
    dot_file.write('<TR><TD BGCOLOR="#9aa0a6"> </TD>'
                   '<TD ALIGN="LEFT">dashed grey: static, not executed</TD></TR>\n')
    dot_file.write('<TR><TD BGCOLOR="#e76f51"> </TD>'
                   '<TD ALIGN="LEFT">solid red: runtime-only</TD></TR>\n')
    dot_file.write('</TABLE>>];\n')


def write_outputs(output_dir, functions, static, runtime):
    """Write machine-readable, human-readable, and visual comparison outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)
    runtime_edge_set = set(runtime)
    hit = static & runtime_edge_set
    static_only = static - runtime_edge_set
    runtime_only = runtime_edge_set - static
    incoming = collections.Counter()
    for (_, callee), count in runtime.items():
        incoming[callee] += count
    bands = heat_bands(incoming.values())
    observed_functions = {function for edge in runtime_edge_set for function in edge}
    unobserved_functions = functions - observed_functions

    csv_path = output_dir / "c_phoenix_design_runtime_edges.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["caller", "callee", "status", "runtime_calls"])
        for edge in sorted(hit):
            writer.writerow([*edge, "hit", runtime[edge]])
        for edge in sorted(static_only):
            writer.writerow([*edge, "static_only", 0])
        for edge in sorted(runtime_only):
            writer.writerow([*edge, "runtime_only", runtime[edge]])

    dot_path = output_dir / "c_phoenix_design_runtime_comparison.dot"
    with dot_path.open("w", encoding="utf-8") as dot_file:
        dot_file.write(
            "digraph DesignRuntime { rankdir=LR; "
            "node [shape=box, style=filled, fillcolor=\"#f4f4f4\"];\n"
        )
        nodes = sorted({function for edge in static | runtime_edge_set for function in edge})
        for node in nodes:
            dot_file.write(
                f'"{node}" [fillcolor="{heat_color(incoming[node], bands)}"];\n'
            )
        for caller, callee in sorted(hit):
            dot_file.write(
                f'"{caller}" -> "{callee}" '
                f'[color="#2a9d8f", penwidth=2, label="{runtime[(caller, callee)]}"];\n'
            )
        for caller, callee in sorted(static_only):
            dot_file.write(
                f'"{caller}" -> "{callee}" '
                '[color="#9aa0a6", style=dashed];\n'
            )
        for caller, callee in sorted(runtime_only):
            dot_file.write(
                f'"{caller}" -> "{callee}" '
                f'[color="#e76f51", penwidth=2, label="{runtime[(caller, callee)]}"];\n'
            )
        write_legend(dot_file, bands)
        dot_file.write("}\n")
    for extension in ("svg", "png"):
        subprocess.run(
            ["dot", f"-T{extension}", str(dot_path), "-o",
             str(output_dir / f"c_phoenix_design_runtime_comparison.{extension}")],
            check=True,
        )

    report_path = output_dir / "c_phoenix_design_runtime_report.md"
    with report_path.open("w", encoding="utf-8") as report:
        report.write("# C-Phoenix: design-time versus runtime\n\n")
        report.write("| Measure | Count |\n| --- | ---: |\n")
        report.write(f"| Defined C functions | {len(functions)} |\n")
        report.write(f"| Static direct call candidates | {len(static)} |\n")
        report.write(f"| Executed runtime call edges | {len(runtime_edge_set)} |\n")
        report.write(f"| Hit static edges | {len(hit)} |\n")
        report.write(f"| Static-only edges | {len(static_only)} |\n")
        report.write(f"| Runtime-only edges | {len(runtime_only)} |\n")
        report.write(f"| Defined but unobserved functions | {len(unobserved_functions)} |\n\n")
        report.write(
            "Nodes use replay-specific incoming-call heatmap bands shown in the "
            "graph legend. Green edges were both statically identified and executed. "
            "Dashed grey edges are source-level call candidates not exercised by "
            "this replay. Red edges were executed but not recognised by the "
            "lightweight source extractor and should be investigated as analysis "
            "gaps before being treated as a code discrepancy.\n\n"
        )
        report.write("## Defined but unobserved functions\n\n")
        for function in sorted(unobserved_functions):
            report.write(f"- `{function}`\n")
        report.write("\n![Comparison graph](c_phoenix_design_runtime_comparison.svg)\n")

    return len(hit), len(static_only), len(runtime_only), len(unobserved_functions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--runtime", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    hit, static_only, runtime_only, unobserved = write_outputs(
        pathlib.Path(args.output_dir),
        *static_edges(pathlib.Path(args.source_dir)),
        runtime_edges(pathlib.Path(args.runtime)),
    )
    print(
        "C design/runtime: "
        f"{hit} hit, {static_only} static-only, {runtime_only} runtime-only, "
        f"{unobserved} defined functions unobserved"
    )


if __name__ == "__main__":
    main()
