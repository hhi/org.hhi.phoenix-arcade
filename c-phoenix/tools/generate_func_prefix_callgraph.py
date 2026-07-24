import os
import re
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.abspath(os.path.join(script_dir, ".."))

    files = [f for f in os.listdir(dir_path) if f.endswith('.c')]

    # 1. Find all defined functions
    all_funcs = set()
    for file in files:
        filepath = os.path.join(dir_path, file)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        for line in content.split('\n'):
            match = re.match(r'^(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)\s*\{?', line)
            if match and not line.endswith(';'):
                func_name = match.group(1)
                all_funcs.add(func_name)

    # 2. Extract calls
    calls = set()
    for file in files:
        filepath = os.path.join(dir_path, file)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        current_func = None
        for line in content.split('\n'):
            match = re.match(r'^(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)\s*\{?', line)
            if match and not line.endswith(';'):
                current_func = match.group(1)
                continue

            if current_func:
                called_funcs = re.findall(r'\b([a-zA-Z0-9_]+)\s*\(', line)
                for cf in called_funcs:
                    if cf in all_funcs and cf != current_func:
                        calls.add((current_func, cf))

    # 3. Categorize purely by function name heuristics
    categories = {
        "Audio": [],
        "Player_And_Weapons": [],
        "Enemies": [],
        "Game_State_Control": [],
        "Collision_And_Scoring": [],
        "Rendering_And_Hardware": [],
        "Direct_Z80_Translations": [],
        "Utilities": []
    }

    for f in all_funcs:
        if f.startswith('sound') or f.startswith('tms36xx') or f.startswith('mame'):
            categories["Audio"].append(f)
        elif f.startswith('player') or f.startswith('weapon'):
            categories["Player_And_Weapons"].append(f)
        elif f.startswith('bird') or f.startswith('alien') or f.startswith('mothership'):
            categories["Enemies"].append(f)
        elif f.startswith('state') or f.startswith('game_state') or f.startswith('attract') or f.startswith('init'):
            categories["Game_State_Control"].append(f)
        elif f.startswith('collision') or f.startswith('scoring') or f.startswith('score') or 'bonus' in f:
            categories["Collision_And_Scoring"].append(f)
        elif f.startswith('sprite') or f.startswith('phoenix') or f.startswith('hw') or f.startswith('platform') or f.startswith('draw'):
            categories["Rendering_And_Hardware"].append(f)
        elif re.match(r'^l[0-9a-f]{4}', f):
            categories["Direct_Z80_Translations"].append(f)
        else:
            categories["Utilities"].append(f)

    # 4. Generate DOT file
    dot_path = os.path.join(dir_path, "context", "graphs", "func_prefix_callgraph.dot")
    with open(dot_path, "w") as f:
        f.write("digraph FuncPrefixGraph {\n")
        f.write("  node [shape=box, style=filled, fillcolor=lightyellow, fontname=\"Helvetica\", fontsize=12];\n")
        f.write("  edge [color=gray60];\n")
        f.write("  rankdir=LR;\n")
        f.write("  splines=true;\n")
        f.write("  overlap=false;\n")

        colors = {
            "Audio": "lightcyan",
            "Player_And_Weapons": "lightgreen",
            "Enemies": "lightcoral",
            "Game_State_Control": "lightblue",
            "Collision_And_Scoring": "thistle",
            "Rendering_And_Hardware": "lightgray",
            "Direct_Z80_Translations": "wheat",
            "Utilities": "white"
        }

        for category, funcs in categories.items():
            if not funcs: continue
            f.write(f"  subgraph cluster_{category} {{\n")
            f.write(f"    label=\"{category.replace('_', ' ')}\";\n")
            f.write("    fontname=\"Helvetica-bold\";\n")
            f.write("    style=filled;\n")
            f.write(f"    fillcolor={colors.get(category, 'white')};\n")
            for func in funcs:
                f.write(f"    \"{func}\";\n")
            f.write("  }\n")

        for caller, callee in calls:
            f.write(f"  \"{caller}\" -> \"{callee}\";\n")

        f.write("}\n")

    try:
        svg_path = os.path.join(dir_path, "context", "graphs", "func_prefix_callgraph.svg")
        # For a massive node graph, sfdp or fdp can sometimes be better, but dot handles clusters well.
        # Let's use standard dot
        subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
        print("Prefix Func SVG generated successfully at " + svg_path)
    except Exception as e:
        print("Failed to run dot: " + str(e))

if __name__ == '__main__':
    main()
