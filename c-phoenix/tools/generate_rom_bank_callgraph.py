import os
import re
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.abspath(os.path.join(script_dir, ".."))

    files = [f for f in os.listdir(dir_path) if f.endswith('.c')]

    # 1. Map each function to its ROM Bank
    func_to_bank = {}
    all_funcs = set()

    for file in files:
        filepath = os.path.join(dir_path, file)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.split('\n')
        current_asm_starts = []

        for line in lines:
            # Look for ASM tags in comments preceding the function
            asm_matches = re.findall(r'\[ASM:\s*([0-9A-Fa-f]{4})-[0-9A-Fa-f]{4}\]', line)
            if asm_matches:
                current_asm_starts.extend(asm_matches)

            match = re.match(r'^(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)\s*\{?', line)
            if match and not line.endswith(';'):
                func_name = match.group(1)
                all_funcs.add(func_name)

                # Determine bank
                bank = "Modern_C_Port_Logic"
                if current_asm_starts:
                    start_addr = int(current_asm_starts[0], 16)
                    if 0x0000 <= start_addr <= 0x0FFF:
                        bank = "ROM_Chip_1_0000_0FFF"
                    elif 0x1000 <= start_addr <= 0x1FFF:
                        bank = "ROM_Chip_2_1000_1FFF"
                    elif 0x2000 <= start_addr <= 0x2FFF:
                        bank = "ROM_Chip_3_2000_2FFF"
                    elif 0x3000 <= start_addr <= 0x3FFF:
                        bank = "ROM_Chip_4_3000_3FFF"

                func_to_bank[func_name] = bank
                current_asm_starts = [] # reset for next function
            elif line.strip() == '' or line.startswith('//') or line.startswith('/*') or line.startswith(' *') or line.startswith('*/'):
                pass
            else:
                if not match and not re.match(r'^\s*#', line):
                    current_asm_starts = []

    # 2. Extract dependencies
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

    # 3. Group by bank
    banks = {
        "ROM_Chip_1_0000_0FFF": [],
        "ROM_Chip_2_1000_1FFF": [],
        "ROM_Chip_3_2000_2FFF": [],
        "ROM_Chip_4_3000_3FFF": [],
        "Modern_C_Port_Logic": []
    }

    for f, b in func_to_bank.items():
        if b in banks:
            banks[b].append(f)

    # 4. Generate DOT
    dot_path = os.path.join(dir_path, "context", "graphs", "rom_bank_callgraph.dot")
    with open(dot_path, "w") as f:
        f.write("digraph ROMBankGraph {\n")
        f.write("  node [shape=box, style=filled, fillcolor=lightyellow, fontname=\"Courier\", fontsize=11];\n")
        f.write("  edge [color=gray60];\n")
        f.write("  rankdir=LR;\n")
        f.write("  splines=true;\n")
        f.write("  overlap=false;\n")

        colors = {
            "ROM_Chip_1_0000_0FFF": "lightpink",
            "ROM_Chip_2_1000_1FFF": "palegreen",
            "ROM_Chip_3_2000_2FFF": "lightblue",
            "ROM_Chip_4_3000_3FFF": "plum",
            "Modern_C_Port_Logic": "gainsboro"
        }

        for bank, funcs in banks.items():
            if not funcs: continue
            f.write(f"  subgraph cluster_{bank} {{\n")
            f.write(f"    label=\"{bank.replace('_', ' ')}\";\n")
            f.write("    fontname=\"Helvetica-bold\";\n")
            f.write("    style=filled;\n")
            f.write(f"    fillcolor={colors.get(bank, 'white')};\n")
            for func in funcs:
                f.write(f"    \"{func}\";\n")
            f.write("  }\n")

        for caller, callee in calls:
            f.write(f"  \"{caller}\" -> \"{callee}\";\n")

        f.write("}\n")

    try:
        svg_path = os.path.join(dir_path, "context", "graphs", "rom_bank_callgraph.svg")
        subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)
        print("ROM Bank SVG generated successfully at " + svg_path)
    except Exception as e:
        print("Failed to run dot: " + str(e))

if __name__ == '__main__':
    main()
