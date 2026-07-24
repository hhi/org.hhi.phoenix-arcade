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
        "Utilities_Infrastructure": ["utilities.c", "coverage.c", "init_global_level_data.c", "misc_logic.c", "sound_dispatcher.c", "rom_compat_stubs.c"]
    }

    files = [f for f in os.listdir(dir_path) if f.endswith('.c')]

    # 1. Map each function to its defining file
    func_to_file = {}
    for file in files:
        filepath = os.path.join(dir_path, file)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        for line in content.split('\n'):
            match = re.match(r'^(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)\s*\{?', line)
            if match and not line.endswith(';'):
                func_name = match.group(1)
                func_to_file[func_name] = file

    # 2. Extract inter-file dependencies
    file_dependencies = set()
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
                    if cf in func_to_file:
                        called_file = func_to_file[cf]
                        if called_file != file:
                            file_dependencies.add((file, called_file))

    # 3. Generate DOT file
    dot_path = os.path.join(dir_path, "context", "graphs", "file_callgraph.dot")
    with open(dot_path, "w") as f:
        f.write("digraph FileDependencyGraph {\n")
        f.write("  node [shape=box, style=\"rounded,filled\", fillcolor=white, fontname=\"Helvetica-bold\", fontsize=14];\n")
        f.write("  edge [color=gray40, penwidth=1.5];\n")
        f.write("  rankdir=LR;\n")
        f.write("  splines=true;\n")
        f.write("  overlap=false;\n")

        for category, cat_files in categories.items():
            f.write(f"  subgraph cluster_{category} {{\n")
            f.write(f"    label=\"{category.replace('_', ' ')}\";\n")
            f.write("    fontname=\"Helvetica-bold\";\n")
            f.write("    fontsize=16;\n")
            f.write("    style=\"rounded,filled\";\n")
            f.write("    fillcolor=aliceblue;\n")
            for file in cat_files:
                if file in files:
                    f.write(f"    \"{file}\";\n")
            f.write("  }\n")

        for caller_file, callee_file in file_dependencies:
            f.write(f"  \"{caller_file}\" -> \"{callee_file}\";\n")

        f.write("}\n")

    try:
        svg_path = os.path.join(dir_path, "context", "graphs", "file_callgraph.svg")
        subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
        print("File SVG generated successfully at " + svg_path)
    except Exception as e:
        print("Failed to run dot: " + str(e))

if __name__ == '__main__':
    main()
