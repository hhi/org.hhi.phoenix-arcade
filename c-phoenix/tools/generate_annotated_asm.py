import os
import re

OBJECT_LINK_RE = re.compile(
    r'\[Object\s+([^\]]+)\]\(((?:fg|bg)tiles\.md#[^)]+)\)(.*)$'
)


def object_reference_note(line):
    match = OBJECT_LINK_RE.search(line)
    if not match:
        return None

    obj, link, description = match.groups()
    description = description.strip()
    suffix = f" - {description}" if description else ""
    return f"> **Tile reference:** [Object {obj}]({link}){suffix}"


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.abspath(os.path.join(script_dir, ".."))
    out_dir = os.path.join(dir_path, "context")

    files = [f for f in os.listdir(dir_path) if f.endswith('.c') or f.endswith('.h')]
    results = []
    all_ranges = []
    referenced_addresses = set()
    func_locations = {}

    for file in sorted(files):
        filepath = os.path.join(dir_path, file)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        hex_matches = re.findall(r'0x([0-9A-Fa-f]{3,4})\b', content)
        for h in hex_matches:
            addr = int(h, 16)
            if 0x0000 <= addr <= 0x3FFF:
                referenced_addresses.add(addr)
        
        if not file.endswith('.c'):
            continue

        lines = content.split('\n')
        current_asm = []
        
        for line_idx, line in enumerate(lines):
            asm_matches = re.findall(r'\[ASM:\s*([0-9A-Fa-f]{4})-([0-9A-Fa-f]{4})\]', line)
            asm_str_matches = re.findall(r'\[ASM:\s*([0-9A-Fa-f]{4}-[0-9A-Fa-f]{4})\]', line)
            
            if asm_str_matches:
                current_asm.extend(asm_str_matches)
                
            for match in asm_matches:
                start = int(match[0], 16)
                end = int(match[1], 16)
                all_ranges.append((start, end))
            
            func_match = re.match(r'^(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)', line)
            if func_match and not line.endswith(';'):
                func_name = func_match.group(1)
                line_num = line_idx + 1
                func_locations[func_name] = f"../{file}#L{line_num}"
                
                sort_key = 0xFFFF
                if current_asm:
                    first_addr_str = current_asm[0].split('-')[0]
                    sort_key = int(first_addr_str, 16)
                
                if sort_key != 0xFFFF:
                    results.append({
                        'type': 'function',
                        'file': file,
                        'function': func_name,
                        'func_link': func_locations[func_name],
                        'asm': ", ".join(current_asm),
                        'sort_key': sort_key
                    })
                current_asm = []
            elif line.strip() == '' or line.startswith('//') or line.startswith('/*') or line.startswith(' *') or line.startswith('*/'):
                pass
            else:
                if not func_match:
                    if not re.match(r'^\s*#', line):
                        current_asm = []

    all_ranges.sort()
    merged = []
    for r in all_ranges:
        if not merged:
            merged.append(r)
        else:
            last = merged[-1]
            if r[0] <= last[1] + 1:
                merged[-1] = (last[0], max(last[1], r[1]))
            else:
                merged.append(r)

    gaps = []
    curr = 0
    for m in merged:
        if m[0] > curr:
            gaps.append((curr, m[0] - 1))
        curr = max(curr, m[1] + 1)

    if curr <= 0x3FFF:
        gaps.append((curr, 0x3FFF))

    for g in gaps:
        start, end = g
        refs_in_gap = sorted([addr for addr in referenced_addresses if start <= addr <= end])
        
        if refs_in_gap:
            ref_strs = [f"${addr:04X}" for addr in refs_in_gap]
            if len(ref_strs) > 10:
                ref_list = ", ".join(ref_strs[:10]) + f" ... (+{len(ref_strs)-10} more)"
            else:
                ref_list = ", ".join(ref_strs)
            desc = f"**Data Table** (Referenced at {ref_list})"
            g_type = "data"
        else:
            desc = "**Unreferenced Gap / TODO**"
            g_type = "gap"

        results.append({
            'type': g_type,
            'file': '---',
            'function': desc,
            'asm': f"{start:04X}-{end:04X}",
            'sort_key': start
        })

    annotations = {}
    for r in results:
        addr = r['sort_key']
        if addr not in annotations:
            annotations[addr] = []
        annotations[addr].append(r)

    in_asm = os.path.join(dir_path, "context", "code-annotated.asm")
    out_md = os.path.join(dir_path, "context", "code-annotated.md")

    with open(in_asm, 'r', encoding='utf-8', errors='ignore') as f:
        asm_lines = f.readlines()

    md_output = []
    md_output.append("# Phoenix Z80 ASM - C Port Cross-Reference")
    md_output.append("\nDit document bevat de originele Z80 assembly code met klikbare links naar de C-port. Je kunt op de functienamen klikken om direct naar de juiste regel in de broncode te gaan!")
    md_output.append("\n```asm")

    in_code_block = True
    last_annotated_addr = -1

    for line in asm_lines:
        stripped_line = line.strip()
        
        # Check if line is a label
        label_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*):$', stripped_line)
        
        if label_match:
            label_name = label_match.group(1)
            if in_code_block:
                md_output.append("```")
                in_code_block = False
            md_output.append(f"\n### {label_name}:\n")
            continue

        # Address line match
        addr_match = re.match(r'^([0-9A-Fa-f]{4}):', line)
        
        if addr_match:
            addr = int(addr_match.group(1), 16)
            
            if addr in annotations and addr != last_annotated_addr:
                if in_code_block:
                    md_output.append("```")
                    in_code_block = False
                
                for ann in annotations[addr]:
                    if ann['type'] == 'function':
                        md_output.append("> [!NOTE]")
                        md_output.append(f"> **Ported to C:** [`{ann['function']}`]({ann['func_link']}) in `{ann['file']}` (ASM: `{ann['asm']}`)")
                    elif ann['type'] == 'data':
                        md_output.append("> [!TIP]")
                        md_output.append(f"> {ann['function']} (ASM: `{ann['asm']}`)")
                    elif ann['type'] == 'gap':
                        md_output.append("> [!WARNING]")
                        md_output.append(f"> {ann['function']} (ASM: `{ann['asm']}`)")
                    md_output.append("")
                    
                last_annotated_addr = addr

        tile_note = object_reference_note(line)
        if tile_note:
            if in_code_block:
                md_output.append("```")
                in_code_block = False
            md_output.append(tile_note)
            md_output.append("")

        if not in_code_block and stripped_line != "":
            md_output.append("```asm")
            in_code_block = True

        if in_code_block:
            md_output.append(line.rstrip('\n'))

    if in_code_block:
        md_output.append("```")

    with open(out_md, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_output))

    print(f"code-annotated.md generated successfully in {out_dir}")

if __name__ == '__main__':
    main()
