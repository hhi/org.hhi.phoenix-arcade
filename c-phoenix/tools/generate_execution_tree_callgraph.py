import os
import re
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.abspath(os.path.join(script_dir, ".."))
    out_dir = os.path.join(dir_path, "context", "graphs")
    os.makedirs(out_dir, exist_ok=True)

    files = [f for f in os.listdir(dir_path) if f.endswith('.c')]

    all_funcs = set()
    raw_calls = set()

    for file in files:
        filepath = os.path.join(dir_path, file)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        current_func = None
        for line in content.split('\n'):
            match = re.match(r'^(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)\s*\{?', line)
            if match and not line.endswith(';'):
                func_name = match.group(1)
                all_funcs.add(func_name)
                current_func = func_name
                continue

            if current_func:
                called_funcs = re.findall(r'\b([a-zA-Z0-9_]+)\s*\(', line)
                for cf in called_funcs:
                    raw_calls.add((current_func, cf))

    # Filter out external calls not defined in our files
    calls = set()
    for caller, callee in raw_calls:
        if callee in all_funcs and caller != callee:
            # Skip massive utility functions to keep tree legible
            if callee not in ['mem_read', 'mem_write', 'check_input_bits', 'add_to_score', 'print_number']:
                calls.add((caller, callee))

    dot_path = os.path.join(out_dir, "execution_tree_callgraph.dot")
    with open(dot_path, "w") as f:
        f.write("digraph ExecutionTreeGraph {\n")
        f.write("  node [shape=box, style=filled, fillcolor=white, fontname=\"Helvetica\", fontsize=12];\n")
        f.write("  edge [color=gray40];\n")
        f.write("  rankdir=TB;\n") # Top to Bottom for tree
        f.write("  splines=true;\n")
        f.write("  overlap=false;\n")

        # Highlight entry points
        entry_points = ['main', 'phoenix_main_loop', 'run_demo_sequence']
        for ep in entry_points:
            if ep in all_funcs:
                f.write(f"  \"{ep}\" [fillcolor=lightblue, style=\"filled,bold\", fontname=\"Helvetica-bold\"];\n")

        for caller, callee in calls:
            f.write(f"  \"{caller}\" -> \"{callee}\";\n")

        f.write("}\n")

    try:
        svg_path = os.path.join(out_dir, "execution_tree_callgraph.svg")
        subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
        print("Execution Tree SVG generated successfully at " + svg_path)
    except Exception as e:
        print("Failed to run dot: " + str(e))

if __name__ == '__main__':
    main()
