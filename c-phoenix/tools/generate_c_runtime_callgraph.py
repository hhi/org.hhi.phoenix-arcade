#!/usr/bin/env python3
"""Generate a C function call graph from an aggregated runtime trace."""

import argparse
import bisect
import collections
import csv
import os
import pathlib
import re
import struct
import subprocess
import json


TRACE_MAGIC = b"CPHXCG01"
HEADER = struct.Struct("=8sQQII")
EDGE = struct.Struct("=QQQ")
HEAT_COLORS = ("#dbe7f3", "#8fd3c7", "#b8de6f", "#ffd166", "#e76f51")
ZERO_HEAT_COLOR = "#eceff1"

# This is intentionally a small, stable architectural vocabulary rather than
# a second naming taxonomy. It turns a recording's function-level trace into
# an answer to "which game systems interacted?". The detail remains available
# in c_phoenix_runtime_calls.csv and c_phoenix_functional_runtime_functions.csv.
FUNCTIONAL_AREAS = (
    ("frame_loop", "Frame loop & cabinet", "frame timing, input and hardware I/O",
     {"platform_sdl.c", "hw_video_audio.c"}, ("platform_", "hw_", "wait_vblank")),
    ("game_flow", "Game flow & attract", "attract mode, game states and round setup",
     {"game_state_machine.c", "state_init.c", "state_play.c", "state_endings.c",
      "attract_mode.c", "init_global_level_data.c"},
     ("game_state", "state_", "attract", "prompt_", "init_global")),
    ("player", "Player, laser & shield", "player control, projectile and explosion",
     {"player_logic.c", "player_explosion.c"}, ("player", "weapon")),
    ("birds", "Birds & alien waves", "formations, bird movement, dives and enemy fire",
     {"bird_logic.c", "birds_vertical_movement.c", "bird_wave_behavior.c",
      "alien_logic.c", "alien_wave.c"}, ("bird", "alien")),
    ("mothership", "Mothership", "mothership approach, combat and scoring phase",
     {"mothership_logic.c", "mothership_impl.c"}, ("mothership",)),
    ("collision", "Collisions & scoring", "hit detection, damage, score and bonus lives",
     {"collision_detection.c", "weapon_collision.c", "scoring.c"},
     ("collision", "score", "bonus")),
    ("video", "Video & sprites", "tile drawing, palette, scroll and sprite composition",
     {"sprite_rendering.c"}, ("sprite", "draw_", "clear_", "print_")),
    ("audio", "Audio", "sound controls, synthesis and sample generation",
     {"sound.c", "sound_discrete.c", "sound_dispatcher.c", "tms36xx.c",
      "mame_lofi_resampler.c"}, ("sound", "tms36", "mame_")),
    ("utilities", "Utilities & state data", "RAM helpers, tables and shared support",
     {"utilities.c", "misc_logic.c", "rom_compat_stubs.c", "coverage.c",
      "runtime_call_trace.c"}, ()),
)
AREA_BY_ID = {area[0]: area for area in FUNCTIONAL_AREAS}
FUNCTIONAL_AREAS_NL = {
    "frame_loop": ("Frameloop & cabinet", "frametiming, invoer en hardware-I/O"),
    "game_flow": ("Spelverloop & attractmodus", "attractmodus, spelstaten en rondeopbouw"),
    "player": ("Speler, laser & schild", "spelerbesturing, projectiel en explosie"),
    "birds": ("Vogels & aliengolven", "formaties, vogelbeweging, duiken en vijandelijk vuur"),
    "mothership": ("Moederschip", "nadering, gevecht en scorefase van het moederschip"),
    "collision": ("Botsingen & score", "raakdetectie, schade, score en bonuslevens"),
    "video": ("Video & sprites", "tegeltekening, palet, scroll en spritecompositie"),
    "audio": ("Geluid", "geluidssturing, synthese en samplegeneratie"),
    "utilities": ("Hulpfuncties & statusdata", "RAM-hulpfuncties, tabellen en gedeelde ondersteuning"),
}


def source_function_files(source_dir):
    """Map functions to their defining C file for functional grouping."""
    return {
        function: source_file
        for function, (source_file, _) in source_function_locations(source_dir).items()
    }


def source_function_locations(source_dir):
    """Map functions to their defining source file and one-based line number."""
    function_locations = {}
    trailing_identifier = re.compile(r"(?P<function>[A-Za-z_][A-Za-z0-9_]*)\s*$")
    type_tokens = re.compile(r"[A-Za-z_][A-Za-z0-9_ \t*]*$")
    control_words = {"else", "for", "if", "return", "switch", "while"}
    # A runtime edge can enter a static inline helper from a header, while
    # multiline signatures are common in the gameplay code. Parse complete C
    # and header files so the explorer never silently drops those source links.
    source_paths = sorted(source_dir.glob("*.c")) + sorted(source_dir.glob("*.h"))
    for source_path in source_paths:
        lines = source_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for line_index, line in enumerate(lines):
            if "(" not in line or line.lstrip().startswith("#"):
                continue
            prefix = line.split("(", 1)[0]
            match = trailing_identifier.search(prefix)
            if not match:
                continue
            type_part = prefix[:match.start()].strip()
            if (
                not type_part
                or not type_tokens.fullmatch(type_part)
                or type_part.split()[0] in control_words
            ):
                continue
            signature = "\n".join(lines[line_index:line_index + 16])
            opening_brace = signature.find("{")
            semicolon = signature.find(";")
            if opening_brace < 0 or (semicolon >= 0 and semicolon < opening_brace):
                continue
            function_locations.setdefault(
                match.group("function"),
                (source_path.name, line_index + 1),
            )
    return function_locations


def functional_area(function, function_files):
    """Return the functional area for a recorded function."""
    source_file = function_files.get(function)
    for area_id, _, _, files, prefixes in FUNCTIONAL_AREAS:
        if source_file in files or any(function.startswith(prefix) for prefix in prefixes):
            return area_id
    return "utilities"


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


def compact_count(value):
    """Format a call count for labels without hiding its order of magnitude."""
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(value)


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


def write_functional_graph(output_dir, counts, function_files, function_locations=None):
    """Write a compact, recording-specific graph of functional areas."""
    functions = sorted({function for edge in counts for function in edge})
    area_functions = collections.defaultdict(set)
    incoming = collections.Counter()
    outgoing = collections.Counter()
    area_edges = collections.Counter()
    for caller, callee in counts:
        caller_area = functional_area(caller, function_files)
        callee_area = functional_area(callee, function_files)
        area_functions[caller_area].add(caller)
        area_functions[callee_area].add(callee)
        outgoing[caller_area] += counts[caller, callee]
        incoming[callee_area] += counts[caller, callee]
        if caller_area != callee_area:
            area_edges[caller_area, callee_area] += counts[caller, callee]

    dot_path = output_dir / "c_phoenix_functional_runtime_callgraph.dot"
    max_count = max(area_edges.values(), default=1)
    with dot_path.open("w", encoding="utf-8") as dot_file:
        dot_file.write(
            "digraph FunctionalRuntime { rankdir=LR; concentrate=true; "
            "node [shape=box style=\"rounded,filled\" fontname=Helvetica]; "
            "edge [color=gray45 fontname=Helvetica];\n"
        )
        for area_id, title, _, _, _ in FUNCTIONAL_AREAS:
            if area_id not in area_functions:
                continue
            label = (
                f"{title}\\n{len(area_functions[area_id])} executed functions"
                f"\\n{compact_count(incoming[area_id])} incoming calls"
            )
            dot_file.write(
                f'"{area_id}" [label="{label}" fillcolor="#dbe7f3"];\n'
            )
        for (caller, callee), count in sorted(area_edges.items()):
            width = 1.0 + (5.0 * count / max_count)
            dot_file.write(
                f'"{caller}" -> "{callee}" [label="{compact_count(count)}" '
                f'penwidth="{width:.2f}"];\n'
            )
        dot_file.write("}\n")

    subprocess.run(
        ["dot", "-Tsvg", str(dot_path), "-o",
         str(output_dir / "c_phoenix_functional_runtime_callgraph.svg")],
        check=True,
    )
    subprocess.run(
        ["dot", "-Tpng", str(dot_path), "-o",
         str(output_dir / "c_phoenix_functional_runtime_callgraph.png")],
        check=True,
    )

    csv_path = output_dir / "c_phoenix_functional_runtime_functions.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["area", "function", "source_file", "incoming_calls", "outgoing_calls"])
        function_incoming = collections.Counter()
        function_outgoing = collections.Counter()
        for (caller, callee), count in counts.items():
            function_outgoing[caller] += count
            function_incoming[callee] += count
        for area_id, title, _, _, _ in FUNCTIONAL_AREAS:
            for function in sorted(area_functions[area_id]):
                writer.writerow([
                    title, function, function_files.get(function, "runtime symbol"),
                    function_incoming[function], function_outgoing[function],
                ])

    report_path = output_dir / "c_phoenix_functional_runtime_callgraph.md"
    with report_path.open("w", encoding="utf-8") as report_file:
        report_file.write("# Functional runtime decomposition\n\n")
        report_file.write(
            "This recording groups executed C functions by their gameplay or "
            "engine responsibility. Edge labels in the graph are observed call "
            "counts between areas; calls within an area are deliberately folded "
            "into its node.\n\n"
        )
        report_file.write(
            "![Functional runtime callgraph](c_phoenix_functional_runtime_callgraph.svg)\n\n"
        )
        report_file.write("| Functional area | Responsibility | Executed functions | Incoming calls |\n")
        report_file.write("| --- | --- | ---: | ---: |\n")
        for area_id, title, description, _, _ in FUNCTIONAL_AREAS:
            if area_id in area_functions:
                report_file.write(
                    f"| {title} | {description} | {len(area_functions[area_id])} | "
                    f"{incoming[area_id]} |\n"
                )
        report_file.write(
            "\nThe per-function membership and measured call totals are in "
            "`c_phoenix_functional_runtime_functions.csv`. The existing "
            "`c_phoenix_runtime_callgraph.svg` remains the drill-down view. "
            "The [runtime trace explorer](../../../tools/runtime-trace-explorer/index.html) "
            "links both levels interactively.\n"
        )

    dutch_report_path = output_dir / "c_phoenix_functional_runtime_callgraph.nl.md"
    with dutch_report_path.open("w", encoding="utf-8") as report_file:
        report_file.write("# Functionele runtimedecompositie\n\n")
        report_file.write(
            "Deze opname groepeert uitgevoerde C-functies naar hun spel- of "
            "engineverantwoordelijkheid. Pijllabels in de graaf zijn gemeten "
            "aantallen aanroepen tussen gebieden; aanroepen binnen één gebied "
            "zijn bewust samengevouwen in de knoop.\n\n"
        )
        report_file.write(
            "![Functionele runtime-callgraph](c_phoenix_functional_runtime_callgraph.svg)\n\n"
        )
        report_file.write("| Functioneel gebied | Verantwoordelijkheid | Uitgevoerde functies | Inkomende aanroepen |\n")
        report_file.write("| --- | --- | ---: | ---: |\n")
        for area_id, title, description, _, _ in FUNCTIONAL_AREAS:
            if area_id in area_functions:
                dutch_title, dutch_description = FUNCTIONAL_AREAS_NL[area_id]
                report_file.write(
                    f"| {dutch_title} | {dutch_description} | {len(area_functions[area_id])} | "
                    f"{incoming[area_id]} |\n"
                )
        report_file.write(
            "\nDe lidmaatschappen per functie en de gemeten aantallen staan in "
            "`c_phoenix_functional_runtime_functions.csv`. De bestaande "
            "`c_phoenix_runtime_callgraph.svg` blijft de detailweergave. De "
            "interactieve [runtimetrace-explorer](../../../tools/runtime-trace-explorer/index.html) "
            "koppelt beide niveaus.\n"
        )



def runtime_explorer_data(counts, function_files, function_locations=None):
    """Build the hierarchy and measured edges consumed by the HTML explorer.

    The hierarchy deliberately uses the existing functional grouping as its
    subsystem level. Source files are modules and observed symbols are leaves;
    this keeps the view trace-backed instead of inventing a second taxonomy.
    """
    functions = sorted({function for edge in counts for function in edge})
    function_locations = function_locations or {}
    modules = collections.defaultdict(list)
    for function in functions:
        area_id = functional_area(function, function_files)
        module = function_files.get(function, "runtime symbols")
        modules[area_id, module].append(function)

    children = []
    for area_id, title, description, _, _ in FUNCTIONAL_AREAS:
        area_modules = []
        for (module_area, module_name), members in sorted(modules.items()):
            if module_area != area_id:
                continue
            area_modules.append({
                "id": f"module:{area_id}:{module_name}",
                "label": module_name,
                "kind": "module",
                "children": [{
                    "id": f"function:{function}",
                    "label": function,
                    "kind": "function",
                    "function": function,
                    "source_file": function_locations.get(function, (None, None))[0],
                    "source_line": function_locations.get(function, (None, None))[1],
                    "children": [],
                } for function in members],
            })
        if area_modules:
            children.append({
                "id": f"area:{area_id}",
                "label": title,
                "description": description,
                "kind": "subsystem",
                "area": area_id,
                "children": area_modules,
            })
    return {
        "root": {
            "id": "domain:runtime",
            "label": "C-Phoenix runtime",
            "kind": "domain",
            "children": children,
        },
        "edges": [
            {"caller": caller, "callee": callee, "count": count}
            for (caller, callee), count in sorted(counts.items())
        ],
    }


def write_runtime_explorer(html_path, counts, function_files, function_locations=None):
    """Write a dependency-free explorer for a recorded runtime trace."""
    data = json.dumps(
        runtime_explorer_data(counts, function_files, function_locations), ensure_ascii=False
    )
    source_dir = pathlib.Path(__file__).resolve().parents[1]
    source_prefix = pathlib.PurePosixPath(os.path.relpath(source_dir, html_path.parent))
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html = f'''<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>C-Phoenix runtime trace explorer</title>
<style>
:root {{ color-scheme: dark; --ink:#d8e0e8; --muted:#a7b7c8; --line:#2d4a60; --panel:#111d29; --surface:#09111a; --accent:#77d7ff; --selected:#1e587c; --edge:#7193aa; }}
* {{ box-sizing:border-box }} body {{ margin:0; font:14px/1.45 system-ui,-apple-system,sans-serif; color:var(--ink); background:var(--surface) }}
header {{ padding:16px 22px; background:#0e1b27; color:var(--ink); border-bottom:1px solid var(--line) }} header h1 {{ margin:0; font-size:19px }} header p {{ margin:3px 0 0; color:var(--muted) }}
main {{ display:grid; grid-template-columns:minmax(265px, 28%) 1fr; min-height:calc(100vh - 82px); gap:1px; background:var(--line) }}
aside,section {{ background:var(--surface); min-width:0 }} aside {{ padding:16px; overflow:auto }} section {{ padding:18px 22px; overflow:auto }}
.eyebrow {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.06em; margin-bottom:8px }}
#tree button {{ display:block; width:100%; border:0; border-radius:5px; background:transparent; padding:5px 7px; text-align:left; color:inherit; cursor:pointer; white-space:nowrap; overflow:hidden; text-overflow:ellipsis }}
#tree button:hover {{ background:#182b3b }} #tree button.selected {{ background:var(--selected); color:var(--ink); font-weight:650 }}
.twisty {{ display:inline-block; width:15px; color:var(--muted) }} .tree-children {{ margin-left:15px }}
#breadcrumb {{ margin-bottom:13px; color:var(--muted); white-space:nowrap; overflow:auto }} #breadcrumb button {{ border:0; padding:0; color:var(--accent); background:transparent; cursor:pointer; font:inherit }}
#summary {{ margin:0 0 5px; color:var(--muted) }} #source {{ min-height:22px; margin:0 0 15px; color:var(--muted) }} #source a {{ color:var(--accent); font-weight:600 }} #graph {{ width:100%; min-height:480px; border:1px solid var(--line); border-radius:8px; background:var(--panel) }}
.node {{ cursor:pointer }} .node.unresolved {{ cursor:default }} .node rect {{ stroke:#5f849a; stroke-width:1.2; fill:#162a39 }} .node.selected rect {{ fill:var(--selected); stroke:var(--accent); stroke-width:2 }} .node text {{ font-size:12px; fill:var(--ink) }} .edge {{ stroke:var(--edge); fill:none; marker-end:url(#arrow) }} .edge-label {{ font-size:11px; fill:#b9c9d8 }}
.empty {{ padding:50px; text-align:center; color:var(--muted) }} @media(max-width:760px) {{ main {{ grid-template-columns:1fr; }} aside {{ max-height:42vh }} }}
</style>
<header><h1>Runtime trace explorer</h1><p>Functional decomposition linked to recorded runtime calls.</p></header>
<main><aside><div class="eyebrow">Functional scope</div><div id="tree"></div></aside><section><nav id="breadcrumb" aria-label="Breadcrumb"></nav><h2 id="title"></h2><p id="summary"></p><p id="source"></p><svg id="graph" role="img" aria-label="Runtime call graph"></svg></section></main>
<script>
const DATA = {data};
const nodes = new Map(), parents = new Map();
const functionIds = new Map();
function index(node, parent=null) {{ nodes.set(node.id,node); if(node.function) functionIds.set(node.function,node.id); if(parent) parents.set(node.id,parent.id); node.children.forEach(c=>index(c,node)); }} index(DATA.root);
let selected = DATA.root.id, expanded = new Set([DATA.root.id]);
function descendants(id) {{ const node=nodes.get(id), result=[]; (function visit(n) {{ result.push(n); n.children.forEach(visit); }})(node); return result; }}
function functions(id) {{ return new Set(descendants(id).flatMap(n=>n.function?[n.function]:[])); }}
function label(id) {{ return nodes.get(id).label; }}
function select(id) {{ selected=id; for(let cursor=id; parents.has(cursor); cursor=parents.get(cursor)) expanded.add(parents.get(cursor)); render(); }}
function renderTree(node, host, depth=0) {{ const row=document.createElement('button'), has=node.children.length; row.style.paddingLeft=(7+depth*14)+'px'; row.className=node.id===selected?'selected':''; row.title=node.label;
  row.innerHTML='<span class="twisty">'+(has?(expanded.has(node.id)?'▾':'▸'):'')+'</span>'+node.label; row.onclick=()=>{{ if(has) expanded.has(node.id)?expanded.delete(node.id):expanded.add(node.id); select(node.id); }}; host.append(row);
  if(has && expanded.has(node.id)) {{ const branch=document.createElement('div'); branch.className='tree-children'; node.children.forEach(c=>renderTree(c,branch,depth)); host.append(branch); }} }}
function aggregate() {{ const scope=functions(selected), node=nodes.get(selected); let level=node.kind==='domain'?'subsystem':node.kind==='subsystem'?'module':'function';
  const member=new Map(); for(const child of (level==='function'?descendants(selected).filter(n=>n.function):descendants(selected).filter(n=>n.kind===level))) {{ const names=functions(child.id); names.forEach(n=>member.set(n,child.id)); }}
  if(node.kind==='function') member.set(node.function,node.id); const result=new Map();
  const graphId=name=>member.get(name)||functionIds.get(name)||'context:'+name;
  for(const edge of DATA.edges) {{ if(!scope.has(edge.caller)&&!scope.has(edge.callee)) continue; const a=graphId(edge.caller), b=graphId(edge.callee); if(a===b) continue; const key=a+'|'+b; result.set(key,{{a,b,count:(result.get(key)?.count||0)+edge.count}}); }}
  const display=new Map(); for(const [name,id] of member) display.set(id,label(id)); for(const edge of result.values()) {{ if(!display.has(edge.a)) display.set(edge.a,edge.a.slice(8)); if(!display.has(edge.b)) display.set(edge.b,edge.b.slice(8)); }} return {{display,edges:[...result.values()]}}; }}
function graph() {{ const {{display,edges}}=aggregate(), svg=document.querySelector('#graph'); svg.replaceChildren(); const list=[...display]; if(!list.length) {{ svg.innerHTML='<text x="50%" y="50%" text-anchor="middle">No observed calls in this selection.</text>'; return; }}
  const width=Math.max(760, svg.clientWidth||760), columns=Math.min(3,list.length), cardWidth=Math.min(190,Math.max(125,(width-80)/columns)), rows=Math.ceil(list.length/columns), height=Math.max(480,rows*120+100); svg.setAttribute('viewBox',`0 0 ${{width}} ${{height}}`); const defs=document.createElementNS('http://www.w3.org/2000/svg','defs'); defs.innerHTML='<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#7193aa"/></marker>'; svg.append(defs);
  const pos=new Map(), gap=columns===1?0:(width-cardWidth-80)/(columns-1); list.forEach(([id,name],i)=>{{ const col=i%columns,row=Math.floor(i/columns), x=columns===1?(width-cardWidth)/2:40+col*gap,y=50+row*120; pos.set(id,{{x,y}}); }}); const max=Math.max(...edges.map(e=>e.count),1), labelled=new Set(edges.slice().sort((a,b)=>b.count-a.count).slice(0,8).map(e=>`${{e.a}}|${{e.b}}`));
  edges.forEach(e=>{{ const a=pos.get(e.a),b=pos.get(e.b); if(!a||!b)return; const path=document.createElementNS(svg.namespaceURI,'path'); path.setAttribute('class','edge'); path.setAttribute('stroke-width',1+5*e.count/max); path.setAttribute('d',`M${{a.x+cardWidth/2}},${{a.y+29}} L${{b.x+cardWidth/2}},${{b.y+29}}`); const title=document.createElementNS(svg.namespaceURI,'title'); title.textContent=`${{display.get(e.a)}} → ${{display.get(e.b)}}: ${{e.count}} calls`; path.append(title); svg.append(path); if(labelled.has(`${{e.a}}|${{e.b}}`)) {{ const t=document.createElementNS(svg.namespaceURI,'text'); t.setAttribute('class','edge-label'); t.setAttribute('x',(a.x+b.x+cardWidth)/2); t.setAttribute('y',(a.y+b.y+24)/2); t.setAttribute('text-anchor','middle'); t.textContent=compact(e.count); svg.append(t); }} }});
  list.forEach(([id,name])=>{{ const p=pos.get(id),g=document.createElementNS(svg.namespaceURI,'g'), target=id.startsWith('context:')?functionIds.get(id.slice(8)):id; g.setAttribute('class','node '+(id===selected?'selected':'')+(target?'':' unresolved')); if(target) g.onclick=()=>select(target); const rect=document.createElementNS(svg.namespaceURI,'rect'); rect.setAttribute('x',p.x); rect.setAttribute('y',p.y); rect.setAttribute('width',cardWidth); rect.setAttribute('height',58); rect.setAttribute('rx',7); const text=document.createElementNS(svg.namespaceURI,'text'); text.setAttribute('x',p.x+cardWidth/2); text.setAttribute('y',p.y+23); text.setAttribute('text-anchor','middle'); const words=name.split(' '), lines=['']; words.forEach(word=>{{ const line=lines[lines.length-1], next=(line+' '+word).trim(); if(next.length>21&&lines.length<2) lines.push(word); else lines[lines.length-1]=next; }}); if(words.join(' ').length>lines.join(' ').length) lines[lines.length-1]+='…'; lines.forEach((line,i)=>{{const span=document.createElementNS(svg.namespaceURI,'tspan');span.setAttribute('x',p.x+cardWidth/2);span.setAttribute('dy',i?14:0);span.textContent=line;text.append(span)}});g.append(rect,text);svg.append(g); }}); }}
function compact(value) {{ return value>=1e9?(value/1e9).toFixed(1)+'B':value>=1e6?(value/1e6).toFixed(1)+'M':value>=1e3?(value/1e3).toFixed(1)+'k':String(value); }}
const SOURCE_VIEWER_PREFIX='__SOURCE_VIEWER_PREFIX__';
function sourceViewerHref(file,line) {{ const page=file.replace(/\\.h$/i,'-h.html').replace(/\\.c$/i,'.html'); return `${{SOURCE_VIEWER_PREFIX}}/${{page}}#L${{line}}`; }}
function render() {{ const tree=document.querySelector('#tree'); tree.replaceChildren(); renderTree(DATA.root,tree); const path=[]; for(let id=selected;;id=parents.get(id)){{path.unshift(id);if(!parents.has(id))break;}} const crumb=document.querySelector('#breadcrumb'); crumb.replaceChildren(); path.forEach((id,i)=>{{if(i)crumb.append(' › ');const b=document.createElement('button');b.textContent=label(id);b.onclick=()=>select(id);crumb.append(b)}}); const scope=functions(selected), calls=DATA.edges.filter(e=>scope.has(e.caller)||scope.has(e.callee)).reduce((n,e)=>n+e.count,0), node=nodes.get(selected); document.querySelector('#title').textContent=node.label; document.querySelector('#summary').textContent=`${{scope.size}} observed functions · ${{compact(calls)}} calls touching this scope · select a node to refine`; const source=document.querySelector('#source'); source.replaceChildren(); if(node.kind==='function' && node.source_file && node.source_line) {{ const link=document.createElement('a'); link.href=sourceViewerHref(node.source_file,node.source_line); link.textContent=`Open source viewer: ${{node.source_file}}:${{node.source_line}}`; source.append(link); }} graph(); }} render();
</script></html>'''
    html_path.write_text(
        html.replace(
            "../../../${node.source_file}",
            f"{source_prefix}/${{node.source_file}}",
        ).replace("__SOURCE_VIEWER_PREFIX__", f"{source_prefix}/context/source"),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace")
    parser.add_argument("--binary", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--explorer-output")
    args = parser.parse_args()

    trace_path = pathlib.Path(args.trace)
    output_dir = pathlib.Path(args.output_dir)
    source_dir = pathlib.Path(__file__).resolve().parents[1]
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
    function_files = source_function_files(source_dir)
    function_locations = source_function_locations(source_dir)
    write_functional_graph(output_dir, counts, function_files, function_locations)
    explorer_path = pathlib.Path(args.explorer_output) if args.explorer_output else output_dir / "c_phoenix_runtime_explorer.html"
    write_runtime_explorer(explorer_path, counts, function_files, function_locations)
    print(f"Executed C call edges: {len(counts)}")
    print("Functional runtime decomposition written alongside the detailed graph.")
    if dropped_edges:
        print(f"Dropped unique edges: {dropped_edges}")


if __name__ == "__main__":
    main()
