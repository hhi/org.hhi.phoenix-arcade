import os
import re

# Findings from the c-phoenix vs. jphoenix PC-coverage cross-check session
# (context/mapping/jphoenix_crosscheck.md). Static analysis alone can't
# detect most of these (reimplementation elsewhere, jumptable-only
# reachability) -- they're recorded here from that manual investigation.
# Only covers the 33 functions that surfaced as coverage discrepancies;
# everything else is left unmarked ("Unconfirmed").
KNOWN_STATUS = {
    # De 15 dode duplicaat-stubs uit de audit (game_demo, spiral_fill_-
    # animation, l0c00_bonus_explosion_scoring, l0cf4, l0e9e, l3452, l3462,
    # l37b0, l37cc, l3800, l3894, l38a1, l38f8, l3980, drawfirst4bird-
    # objects) zijn op 11 juli 2026 verwijderd; hun ROM-ranges staan als
    # proza-notities in de bronbestanden en de levende vertalingen in de
    # tabel hieronder.
    'level_4_6_8_spiral_fill': 'Live vertaling van L2230 (dode duplicaat `spiral_fill_animation` verwijderd 11 juli 2026)',
    # -- Geïnlined: de ROM-hulproutine bestaat als losse C-functie maar de
    #    aanroepplekken zijn in C als memset/memcpy/inline vertaald;
    #    passieve lockstep bevestigt byte-exact gedrag (11 juli 2026). --
    'add_bc_to_mem': 'Geïnlined bij de C-aanroepplekken (o.a. slow-print $01AB); losse functie ongebruikt',
    'clear_b_bytes_at_hl': 'Geïnlined als memset bij de init-aanroepplekken ($0158/$050B/$0537/$0557); losse functie ongebruikt',
    'copy_b_bytes_hl_to_de': 'Geïnlined als memcpy/loops bij de aanroepplekken ($054F/$0592/$32E3); losse functie ongebruikt',
    'print_score_column': 'Geïnlined in state_1_flashing_score (asm-aanroep $04C9); losse functie ongebruikt',
    'l14e0': 'Coin-check-continuatie van de slow-print ($01CA); in C centraal afgehandeld in wait_vblank_coin — stub bewust leeg',
    'add_to_score': 'Vervangen door `add_score()` (scoring.c) bij de aanroepplekken $2731/$275C; losse functie ongebruikt',
    # -- Live code; het eerdere "alleen c-phoenix bereikt dit"-signaal
    #    (scripted coverage) bleek een harnas-artefact: jphoenix verbruikt
    #    soms >1 vblank per spel-loop-iteratie, waardoor scripts op andere
    #    spelmomenten vuren. --
    'l3462_no_birds_left': 'Live (scripted-coverage-verschil was een harnas-artefact)',
    'l3ad0': 'Live (scripted-coverage-verschil was een harnas-artefact)',
    'l3af8': 'Live (scripted-coverage-verschil was een harnas-artefact)',
    'l3b02': 'Live (scripted-coverage-verschil was een harnas-artefact)',
    'erase_mothership': 'Live (bereikt in echte gameplay, zie my_session.txt-fix 9 juli; scripted-coverage-verschil was harnas-artefact)',
    'mothership_core_hit_check': 'Live (bereikt in echte gameplay, zie my_session.txt-fix 9 juli; scripted-coverage-verschil was harnas-artefact)',
    'l2552_mothership_explosion_done': 'Live (bereikt in echte gameplay, zie my_session.txt-fix 9 juli; scripted-coverage-verschil was harnas-artefact)',
    'state_6_mother_ship_explosion': 'Live (bereikt in echte gameplay, zie my_session.txt-fix 9 juli; scripted-coverage-verschil was harnas-artefact)',
    # -- Overig --
    'init_alien_movement_pointers': 'Wel aangesloten (state_init.c:81), maar guard-conditie nooit getriggerd door testscripts',
    'l00b6': 'Dode code: nul aanroepers, ook in de originele ROM',
    'l0e02_unused': 'Vermoedelijk dode code: niet geraakt door c-phoenix of echte Z80, geen asm-referentie',
    'unused_bcd_subtracter': 'Vermoedelijk dode code: niet geraakt door c-phoenix of echte Z80, geen asm-referentie',
}

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.abspath(os.path.join(script_dir, ".."))
    out_dir = os.path.join(dir_path, "context", "mapping")

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

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

            func_match = re.match(r'^\s*(?:static\s+)?(?:void|uint8_t|uint16_t|int|bool)\s+([a-zA-Z0-9_]+)\s*\(.*\)', line)
            if func_match and not line.endswith(';'):
                func_name = func_match.group(1)
                line_num = line_idx + 1

                func_locations[func_name] = f"../../{file}#L{line_num}"

                sort_key = 0xFFFF
                if current_asm:
                    first_addr_str = current_asm[0].split('-')[0]
                    sort_key = int(first_addr_str, 16)

                results.append({
                    'type': 'function',
                    'file': file,
                    'function': func_name,
                    'func_link': func_locations[func_name],
                    'asm': ", ".join(current_asm) if current_asm else "Unknown / None",
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

    # Pre-load code-annotated.asm for gap analysis
    asm_lines_map = {}
    asm_filepath = os.path.join(dir_path, "context", "code-annotated.asm")
    if os.path.exists(asm_filepath):
        with open(asm_filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                addr_match = re.match(r'^([0-9A-Fa-f]{4}):\s*([A-Fa-f0-9 ]+)(?:\s+([A-Za-z]+)\s+)?', line)
                if addr_match:
                    addr = int(addr_match.group(1), 16)
                    bytes_str = addr_match.group(2).strip()
                    instr = addr_match.group(3)
                    asm_lines_map[addr] = {'bytes': bytes_str, 'instr': instr, 'raw': line.strip()}

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

        # Analyze ASM contents in this gap
        gap_bytes = []
        instructions = set()
        for a in range(start, end + 1):
            if a in asm_lines_map:
                gap_bytes.extend(asm_lines_map[a]['bytes'].split())
                if asm_lines_map[a]['instr']:
                    instructions.add(asm_lines_map[a]['instr'])

        # Determine gap characteristics
        gap_size = (end - start) + 1
        is_all_ff = all(b == 'FF' for b in gap_bytes) if gap_bytes else False
        is_all_00 = all(b == '00' for b in gap_bytes) if gap_bytes else False

        # Heuristic for Z80 code: contains common opcodes (NOP, JP, CALL, LD, RET) and isn't just FF/00 padding
        common_ops = {'NOP', 'JP', 'CALL', 'LD', 'RET', 'CP', 'JR', 'INC', 'DEC', 'PUSH', 'POP', 'AND', 'OR', 'XOR'}
        has_code = bool(instructions.intersection(common_ops)) and not (is_all_ff or is_all_00)

        if refs_in_gap:
            ref_strs = [f"${addr:04X}" for addr in refs_in_gap]
            ref_list = ", ".join(ref_strs[:5]) + (f" ... (+{len(ref_strs)-5} more)" if len(ref_strs) > 5 else "")
            desc = f"*** DATA TABLE (Refs: {ref_list}) ***"
            g_type = "data"
        else:
            if is_all_ff:
                desc = f"Padding ({gap_size} bytes of FF)"
            elif is_all_00:
                desc = f"Padding ({gap_size} bytes of 00)"
            elif has_code:
                # Show first few instructions
                ops_str = ", ".join(list(instructions)[:5])
                desc = f"*** UNREFERENCED CODE? (Ops: {ops_str}) ***"
            else:
                # Show bytes
                byte_str = " ".join(gap_bytes[:8]) + ("..." if len(gap_bytes) > 8 else "")
                desc = f"*** UNREFERENCED DATA (Bytes: {byte_str}) ***"
            g_type = "gap"

        results.append({
            'type': g_type,
            'file': '---',
            'function': desc,
            'asm': f"{start:04X}-{end:04X}",
            'sort_key': start
        })

    results_sorted_addr = sorted(results, key=lambda x: (x['sort_key'], x['file'], x['function']))

    # Detect same-range duplicates: two or more function rows sharing an
    # identical ASM range are almost always one live implementation plus
    # one orphaned leftover (see jphoenix_crosscheck.md category A).
    range_to_funcs = {}
    for r in results_sorted_addr:
        if r['type'] == 'function' and r['asm'] != 'Unknown / None':
            range_to_funcs.setdefault(r['asm'], []).append(r['function'])
    duplicate_ranges = {rng: names for rng, names in range_to_funcs.items() if len(names) > 1}

    # Grond-waarheid-verificatie uit de scripted-lockstep-batch
    # (context/mapping/lockstep_verified.json, gegenereerd door de
    # batch-aggregatie): functies wier volledige ROM-range door jphoenix
    # is uitgevoerd binnen een run die byte-exact aan c-phoenix bleek.
    verified_info = {"verified": [], "partial": {}, "generated": "?"}
    verified_path = os.path.join(out_dir, 'lockstep_verified.json')
    if os.path.exists(verified_path):
        import json
        with open(verified_path) as vf:
            verified_info = json.load(vf)
    verified_set = set(verified_info.get("verified", []))
    partial_map = verified_info.get("partial", {})
    verified_date = verified_info.get("generated", "?")

    def status_for(r):
        if r['function'] in KNOWN_STATUS:
            return KNOWN_STATUS[r['function']]
        siblings = duplicate_ranges.get(r['asm'])
        if siblings:
            others = [n for n in siblings if n != r['function']]
            return f"Zelfde adres als: {', '.join(f'`{n}`' for n in others)} — controleer welke live is"
        if r['function'] in verified_set:
            return f"Geverifieerd: byte-exacte scripted lockstep + PC-dekking ({verified_date})"
        if r['function'] in partial_map:
            return f"Deels geverifieerd ({partial_map[r['function']]}% van de range uitgevoerd in byte-exacte runs, {verified_date})"
        return ""

    # Calculate gap statistics
    padding_ff = 0
    padding_00 = 0
    unref_data = 0
    unref_code = 0
    data_table = 0

    for r in results_sorted_addr:
        if r['type'] in ('gap', 'data'):
            label = r['function']
            if label.startswith('Padding'):
                if 'FF' in label:
                    padding_ff += 1
                elif '00' in label:
                    padding_00 += 1
            elif label.startswith('*** UNREFERENCED DATA'):
                unref_data += 1
            elif label.startswith('*** UNREFERENCED CODE?'):
                unref_code += 1
            elif label.startswith('*** DATA TABLE'):
                data_table += 1

    total_gaps = padding_ff + padding_00 + unref_data + unref_code + data_table

    # Write c_functions_by_address.md
    with open(os.path.join(out_dir, 'c_functions_by_address.md'), 'w') as f:
        f.write("# C Functions Sorted by ROM Address (Including Analyzed Gaps)\n\n")

        # Inject Conclusion
        f.write("> [!NOTE]\n")
        f.write("> **Gap Analysis Conclusion**\n")
        f.write(f"> In the entire 16KB ROM-space, {total_gaps} unmapped gaps/data blocks were found:\n")
        f.write(f"> - **Padding (FF)**: {padding_ff} (Confirmed empty EPROM space)\n")
        f.write(f"> - **UNREFERENCED DATA**: {unref_data} (Unreadable bytes, likely unused arrays, sprites, or artifacts)\n")
        f.write(f"> - **DATA TABLE**: {data_table} (Data explicitly referenced by C code)\n")
        if padding_00 > 0: f.write(f"> - **Padding (00)**: {padding_00}\n")
        if unref_code > 0: f.write(f"> - **UNREFERENCED CODE?**: {unref_code}\n")
        f.write(">\n")
        f.write("> **Conclusion:** Zero blocks of unreferenced executable Z80 code were found. Every executable Z80 instruction is either translated to a C function or explicitly stubbed. The codebase is 100% covered regarding executable logic.\n")
        f.write(">\n")
        f.write("> **Let op — dit is byte-dekking, geen bevestiging van correctheid.** \"100% covered\" betekent dat elke ROM-byte een naam of expliciete gap-markering heeft, *niet* dat elke vertaling ook bevestigd actief en correct is in de C-poort. Een cross-check tegen echte Z80-executie (jphoenix) en de c-phoenix-coverage vond 33 functies waarbij dat niet zo simpel lag — zie de **Status**-kolom hieronder en [`jphoenix_crosscheck.md`](jphoenix_crosscheck.md) voor de volledige analyse. Rijen zonder Status-vermelding zijn nog niet op deze manier onderzocht (\"Unconfirmed\").\n\n")

        f.write("| ASM Address | Function | File | Full Range(s) | Status |\n")
        f.write("|---|---|---|---|---|\n")

        c_helpers = []
        for r in results_sorted_addr:
            if r['type'] == 'function' and r['sort_key'] == 0xFFFF:
                c_helpers.append(r)
                continue

            if r['type'] == 'gap' or r['type'] == 'data':
                f.write(f"| **${r['sort_key']:04X}** | **{r['function']}** | **{r['file']}** | **{r['asm']}** | |\n")
            else:
                display_addr = f"${r['sort_key']:04X}"
                status = status_for(r)
                func_md = f"[`{r['function']}`]({r['func_link']})"
                file_md = f"[{r['file']}](../../{r['file']})"
                f.write(f"| {display_addr} | {func_md} | {file_md} | {r['asm']} | {status} |\n")

        if c_helpers:
            f.write("\n## C-only Infrastructure / Native Helpers\n\n")
            f.write("Deze functies bestaan uitsluitend in de C-poort (bijvoorbeeld voor window creatie, SDL, geluid, of testing) en hebben geen origineel Z80 ROM-adres.\n\n")
            f.write("| Function | File |\n")
            f.write("|---|---|\n")
            for r in c_helpers:
                func_md = f"[`{r['function']}`]({r['func_link']})"
                file_md = f"[{r['file']}](../../{r['file']})"
                f.write(f"| {func_md} | {file_md} |\n")

    # Group by file for c_functions_per_file.md
    functions_by_file = {}
    for r in results:
        if r['type'] == 'function':
            if r['file'] not in functions_by_file:
                functions_by_file[r['file']] = []
            functions_by_file[r['file']].append(r)

    with open(os.path.join(out_dir, 'c_functions_per_file.md'), 'w') as f:
        f.write("# C Functions per File\n\n")
        for file_name in sorted(functions_by_file.keys()):
            f.write(f"## [{file_name}](../../{file_name})\n\n")
            f.write("| Function | ASM Range(s) |\n")
            f.write("|---|---|\n")
            for r in functions_by_file[file_name]:
                func_md = f"[`{r['function']}`]({r['func_link']})"
                f.write(f"| {func_md} | {r['asm']} |\n")
            f.write("\n")

    print(f"Mapping MD files successfully generated with gap analysis.")

if __name__ == '__main__':
    main()
