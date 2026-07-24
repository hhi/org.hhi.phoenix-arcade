#!/usr/bin/env python3
"""Punt-4-vehicle: mapt jphoenix's PC-coverage van clean scripted-lockstep-
runs (spelstaat byte-exact; scherm hooguit transiente blips) op de functie-
ranges uit c_functions_by_address.md. Schrijft het resultaat als
repo-artefact naar context/mapping/lockstep_verified.json."""
import csv, json, os, re, datetime

from criteria import MAX_TRANSIENT_SCREEN_RECORDS, MAX_TRANSIENT_STATE_RECORDS

OUT = os.path.dirname(os.path.abspath(__file__))
CPHX = os.path.abspath(os.environ.get("CPHX", os.path.join(OUT, "..", "..")))

clean_scripts, dirty = [], []
with open(os.path.join(OUT, "results.jsonl")) as f:
    for line in f:
        r = json.loads(line)
        (clean_scripts if r["clean"] else dirty).append(r)

covered = set()
missing_cov = []
for r in clean_scripts:
    base = os.path.basename(r["script"]).replace(".txt", ".pc-coverage.csv").lower()
    path = os.path.join(OUT, "pc-coverage", base)
    if not os.path.exists(path):
        missing_cov.append(r["script"]); continue
    with open(path) as f:
        for row in csv.DictReader(f):
            covered.add(int(row["pc"], 16))

# PC-coverage registreert alleen opcode-fetch-adressen; tel dekking dus
# over de instructie-adressen uit code-annotated.asm, niet over ruwe bytes.
instr_addrs = set()
with open(os.path.join(CPHX, "context/code-annotated.asm")) as f:
    for line in f:
        m = re.match(r"^([0-9A-Fa-f]{4}):\s*[A-Fa-f0-9]{2}", line)
        if m:
            instr_addrs.add(int(m.group(1), 16))

rows = []
with open(os.path.join(CPHX, "context/mapping/c_functions_by_address.md")) as f:
    for line in f:
        if not line.startswith("|") or "Padding" in line or "UNREFERENCED" in line or "DATA TABLE" in line:
            continue
        m = re.search(r"\[`([^`]+)`\]", line)
        if not m: continue
        name = m.group(1)
        ranges = [(int(a,16), int(b,16)) for a,b in re.findall(r"([0-9A-F]{4})-([0-9A-F]{4})", line)]
        if ranges:
            rows.append((name, ranges))

verified, partial, unhit = [], {}, []
for name, ranges in rows:
    total = hit = 0
    for s, e in ranges:
        for pc in range(s, e+1):
            if pc not in instr_addrs:
                continue
            total += 1
            if pc in covered: hit += 1
    pct = 100*hit/total if total else 0
    if total and pct >= 95.0: verified.append(name)
    elif hit: partial[name] = round(pct, 1)
    else: unhit.append(name)

result = {
    "generated": str(datetime.date.today()),
    "criterion": ("clean run = spelstaat ($4340-$4BE5, excl. gedocumenteerde "
                  "ruis 438A-438D) byte-exact over de hele run (excl. "
                  "game-start-init-venster rec 40-60); spelstaat-blips hooguit "
                  f"{MAX_TRANSIENT_STATE_RECORDS} record en scherm-diffs hooguit "
                  f"zelfherstellende blips van <= {MAX_TRANSIENT_SCREEN_RECORDS} records. "
                  "Functie geldt als geverifieerd bij >= 95% PC-dekking van zijn "
                  "ROM-range binnen minimaal een clean run; dekking geteld over "
                  "instructie-adressen (opcode-fetches)."),
    "clean_scripts": [r["script"] for r in clean_scripts],
    "dirty_scripts": {r["script"]: r.get("first_state_divergence") or r.get("long_screen_runs")
                      for r in dirty},
    "verified": sorted(verified),
    "partial": partial,
    "unhit": sorted(unhit),
}
dest = os.path.join(CPHX, "context/mapping/lockstep_verified.json")
with open(dest, "w") as f:
    json.dump(result, f, indent=1, ensure_ascii=False)

print(f"clean: {len(clean_scripts)}, dirty: {len(dirty)}, coverage-CSV ontbreekt: {len(missing_cov)}")
print(f"PC-adressen gedekt door clean runs: {len(covered)}")
print(f"functies: geverifieerd={len(verified)} gedeeltelijk={len(partial)} niet-geraakt={len(unhit)}")
print(f"geschreven: {dest}")
if dirty:
    print("\ndirty scripts (eerste spelstaat-divergentie):")
    for r in dirty:
        print(f"  {r['script']}: {r.get('first_state_divergence')}")
