import os
import re
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.abspath(os.path.join(script_dir, ".."))
    out_dir = os.path.join(dir_path, "context", "graphs")
    os.makedirs(out_dir, exist_ok=True)

    categories = {
        "Core_Architecture": ["platform_sdl.c", "hw_video_audio.c", "phoenix_render_assets.h"],
        "Game_State": ["game_state_machine.c", "state_init.c", "state_play.c", "state_endings.c", "attract_mode.c"],
        "Audio": ["sound.c", "sound_discrete.c", "tms36xx.c", "mame_lofi_resampler.c"],
        "Entity_Logic": ["player_logic.c", "player_explosion.c", "bird_logic.c", "birds_vertical_movement.c", "bird_wave_behavior.c", "alien_logic.c", "alien_wave.c", "mothership_logic.c", "mothership_impl.c"],
        "Collision_Mechanics": ["collision_detection.c", "weapon_collision.c", "scoring.c"],
        "Rendering": ["sprite_rendering.c"],
        "Utilities_Infrastructure": ["utilities.c", "coverage.c", "init_global_level_data.c", "misc_logic.c", "sound_dispatcher.c", "rom_compat_stubs.c"]
    }

    files = [f for f in os.listdir(dir_path) if f.endswith('.c')]

    # 1. Parse coverage data from .gcov files
    func_coverage = {}

    for file in files:
        gcov_file = os.path.join(dir_path, file + ".gcov")
        if not os.path.exists(gcov_file):
            continue

        with open(gcov_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            # Match line format: "    ####:  123: void my_func() {" OR "       1:  123: void my_func() {"
            match = re.match(r'^\s*([0-9]+|####|-):\s*[0-9]+:\s*(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)\s*\{?', line)
            if match and not line.endswith(';'):
                hits = match.group(1)
                func_name = match.group(2)

                if hits == '####':
                    func_coverage[func_name] = False
                elif hits != '-':
                    func_coverage[func_name] = True

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

                # If we didn't get coverage data, assume false
                if func_name not in func_coverage:
                    func_coverage[func_name] = False

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

    dot_path = os.path.join(out_dir, "coverage_callgraph.dot")
    with open(dot_path, "w") as f:
        f.write("digraph CoverageGraph {\n")
        f.write("  node [shape=box, style=filled, fontname=\"Helvetica\", fontsize=12];\n")
        f.write("  edge [color=gray40];\n")
        f.write("  rankdir=LR;\n")
        f.write("  splines=true;\n")
        f.write("  overlap=false;\n")

        for category, cat_files in categories.items():
            funcs_in_cat = [f for f in all_funcs if func_to_category[f] == category]
            if not funcs_in_cat:
                continue

            f.write(f"  subgraph cluster_{category} {{\n")
            f.write(f"    label=\"{category.replace('_', ' ')}\";\n")
            f.write("    fontname=\"Helvetica-bold\";\n")
            f.write("    style=\"rounded,filled\";\n")
            f.write("    fillcolor=white;\n")

            for func in funcs_in_cat:
                if func_coverage.get(func, False):
                    f.write(f"    \"{func}\" [fillcolor=lightgreen];\n")
                else:
                    f.write(f"    \"{func}\" [fillcolor=lightcoral];\n")
            f.write("  }\n")

        for caller, callee in raw_calls:
            f.write(f"  \"{caller}\" -> \"{callee}\";\n")

        f.write("}\n")

    try:
        svg_path = os.path.join(out_dir, "coverage_callgraph.svg")
        subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
        print("Coverage SVG generated successfully at " + svg_path)
    except Exception as e:
        print("Failed to run dot: " + str(e))

if __name__ == '__main__':
    main()
