import os
import re
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.abspath(os.path.join(script_dir, ".."))

    categories = {
        "Core_Architecture": ["platform_sdl.c", "hw_video_audio.c", "phoenix_render_assets.h"],
        "Game_State": ["game_state_machine.c", "state_init.c", "state_play.c", "state_endings.c", "attract_mode.c"],
        "Audio": ["sound.c", "sound_discrete.c", "tms36xx.c", "mame_lofi_resampler.c"],
        "Entity_Logic": ["player_logic.c", "player_explosion.c", "bird_logic.c", "birds_vertical_movement.c", "bird_wave_behavior.c", "alien_logic.c", "alien_wave.c", "mothership_logic.c", "mothership_impl.c"],
        "Collision_Mechanics": ["collision_detection.c", "weapon_collision.c", "scoring.c"],
        "Rendering": ["sprite_rendering.c"],
        "Utilities_Infrastructure": ["utilities.c", "coverage.c", "init_global_level_data.c", "misc_logic.c", "rom_compat_stubs.c"],
        "Audio": ["sound_dispatcher.c"]
    }

    files = [f for f in os.listdir(dir_path) if f.endswith('.c')]

    func_to_category = {}
    all_funcs = set()

    for file in files:
        filepath = os.path.join(dir_path, file)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        cat = "Unknown"
        for c, f_list in categories.items():
            if file in f_list:
                cat = c
                break

        for line in content.split('\n'):
            match = re.match(r'^(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)\s*\{?', line)
            if match and not line.endswith(';'):
                func_name = match.group(1)
                all_funcs.add(func_name)
                func_to_category[func_name] = cat

    raw_calls = set()
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
                        raw_calls.add((current_func, cf))

    stub_hunter_calls = set()
    active_nodes = set()

    # Include all stubs by default, so we can see orphaned ones
    for f, c in func_to_category.items():
        if c == "Stubs_To_Refactor":
            active_nodes.add(f)

    for caller, callee in raw_calls:
        if func_to_category[callee] == "Stubs_To_Refactor":
            stub_hunter_calls.add((caller, callee))
            active_nodes.add(caller)

    dot_path = os.path.join(dir_path, "context", "graphs", "stub_hunter_callgraph.dot")
    with open(dot_path, "w") as f:
        f.write("digraph StubHunterGraph {\n")
        f.write("  node [shape=box, style=filled, fillcolor=white, fontname=\"Helvetica\", fontsize=12];\n")
        f.write("  edge [color=red, penwidth=2.0];\n")
        f.write("  rankdir=LR;\n")
        f.write("  splines=true;\n")
        f.write("  overlap=false;\n")

        for category in categories.keys():
            nodes_in_cat = [n for n in active_nodes if func_to_category[n] == category]
            if not nodes_in_cat:
                continue

            f.write(f"  subgraph cluster_{category} {{\n")
            if category == "Stubs_To_Refactor":
                f.write(f"    label=\"STUBS TO REFACTOR (Target Zone)\";\n")
                f.write("    fillcolor=mistyrose;\n")
                f.write("    color=red;\n")
            else:
                f.write(f"    label=\"{category.replace('_', ' ')}\";\n")
                f.write("    fillcolor=aliceblue;\n")
                f.write("    color=black;\n")

            f.write("    fontname=\"Helvetica-bold\";\n")
            f.write("    style=\"rounded,filled\";\n")
            for func in nodes_in_cat:
                if category == "Stubs_To_Refactor":
                    f.write(f"    \"{func}\" [fillcolor=lightcoral, fontcolor=white];\n")
                else:
                    f.write(f"    \"{func}\" [fillcolor=lightgreen];\n")
            f.write("  }\n")

        for caller, callee in stub_hunter_calls:
            f.write(f"  \"{caller}\" -> \"{callee}\";\n")

        f.write("}\n")

    try:
        svg_path = os.path.join(dir_path, "context", "graphs", "stub_hunter_callgraph.svg")
        subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
        print("Stub Hunter SVG generated successfully at " + svg_path)
    except Exception as e:
        print("Failed to run dot: " + str(e))

if __name__ == '__main__':
    main()
