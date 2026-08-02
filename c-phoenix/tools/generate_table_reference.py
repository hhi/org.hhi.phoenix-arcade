#!/usr/bin/env python3
"""Generate the annotated reference for the program-ROM tables.

`phoenix_tables.c` holds the game-data tables extracted from the program ROM.
Its knowledge-base page used to describe two of them; this builds the full
reference from sources that cannot drift out of date:

  * ``phoenix_tables.h``  - one doc comment per table, each carrying an
    ``[ASM: nnnn-nnnn]`` ROM range and a prose description.
  * the C sources         - grepped for every function that reads each table,
    so the page says where a table is *used*, not just what it contains.

Usage:  python3 tools/generate_table_reference.py [--outdir DIR]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

TABLES_H = PROJECT / "phoenix_tables.h"
TABLES_C = PROJECT / "phoenix_tables.c"

DECL_RE = re.compile(r"extern const uint8_t (?P<name>phoenix_\w+)\s*\[(?P<size>[^\]]*)\];")
ASM_RE = re.compile(r"\[ASM:\s*([0-9A-Fa-f]+)\s*-\s*([0-9A-Fa-f]+)\]")
FUNC_RE = re.compile(r"^[A-Za-z_][\w \t\*]*\b(\w+)\s*\([^;]*\)\s*\{", re.M)


def clean(doc: str) -> str:
    """Turn a block comment into one paragraph of prose."""
    lines = [re.sub(r"^\s*\*?\s?", "", l).rstrip() for l in doc.strip("\n").split("\n")]
    text = " ".join(l for l in lines if l.strip())
    text = ASM_RE.sub("", text).strip()
    return re.sub(r"\s+", " ", text)


def read_tables():
    """Read each table declaration and the comment block directly above it.

    An earlier version matched comment-then-declaration with one regex. Where
    a header has an inline accessor between the two, that swallowed the wrong
    comment and produced a Purpose describing a different symbol. Scanning
    backwards from each declaration cannot make that mistake.
    """
    text = TABLES_H.read_text()
    out = []
    for m in DECL_RE.finditer(text):
        before = text[:m.start()].rstrip()
        doc = ""
        if before.endswith("*/"):
            open_at = before.rfind("/*")
            if open_at != -1:
                block = before[open_at + 2:-2]
                # a comment that itself contains a declaration is not this
                # table's doc block; better no text than the wrong text
                if "extern const" not in block and "static inline" not in block:
                    doc = block
        rng = ASM_RE.search(doc)
        out.append({
            "name": m["name"],
            "size": m["size"].strip(),
            "asm": (rng[1].upper(), rng[2].upper()) if rng else None,
            "text": clean(doc) if doc else "",
        })
    return out


def strip_comments(src: str) -> str:
    """Blank out comments, keeping offsets intact.

    Without this a table mentioned in a doc comment is reported as a reader.
    That happened for real: phoenix_alien_explosion_frames was credited to
    attract_mode.c because its name appears in a comment there.
    """
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j == -1 else j + 2
            out.append("".join(c if c == "\n" else " " for c in src[i:j]))
            i = j
        elif src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j == -1 else j
            out.append(" " * (j - i))
            i = j
        else:
            out.append(src[i])
            i += 1
    return "".join(out)


def _hits(src, name, starts):
    """Function names containing a reference to `name`, in already-stripped src."""
    found = []
    for hit in re.finditer(r"\b" + re.escape(name) + r"\b", src):
        fn = None
        for pos, label in starts:
            if pos < hit.start():
                fn = label
            else:
                break
        if fn not in found:
            found.append(fn)
    return found


def find_users(names):
    """Map each table to the C functions that read it.

    Some tables are never named in a .c file: they are reached through a small
    accessor in phoenix_tables.h. For those the accessor is resolved one step
    further, so the page still shows a real call site.
    """
    users = {n: [] for n in names}
    sources = {}
    for path in sorted(PROJECT.glob("*.c")):
        if path.name == "phoenix_tables.c":
            continue                      # the definitions, not a use
        src = strip_comments(path.read_text(errors="ignore"))
        sources[path.name] = (src, [(m.start(), m[1]) for m in FUNC_RE.finditer(src)])

    for fname, (src, starts) in sources.items():
        for name in names:
            for fn in _hits(src, name, starts):
                entry = (fname, fn, None)
                if entry not in users[name]:
                    users[name].append(entry)

    # tables reached only through an accessor in the header
    hdr = strip_comments(TABLES_H.read_text())
    hdr_starts = [(m.start(), m[1]) for m in FUNC_RE.finditer(hdr)]
    for name in names:
        if users[name]:
            continue
        for accessor in _hits(hdr, name, hdr_starts):
            if not accessor:
                continue
            for fname, (src, starts) in sources.items():
                for fn in _hits(src, accessor, starts):
                    entry = (fname, fn, accessor)
                    if entry not in users[name]:
                        users[name].append(entry)
    return users


def render(tables, users, lang):
    t = {
        "en": dict(
            title="Phoenix ROM Tables (`phoenix_tables.c`)",
            intro=("Every game-data table extracted from the program ROM, with its ROM range, "
                   "what it is for, and the C functions that read it. Generated by "
                   "`tools/generate_table_reference.py` from the doc comments in "
                   "`phoenix_tables.h` and a scan of the C sources — do not edit by hand."),
            counth="Tables", rangeh="ROM range", sizeh="Size", useh="Read by",
            toc="Contents", none="no reader found in the C sources",
            usedby="Read by", purpose="Purpose", back="Back to", via="via", nodoc="no doc comment directly above the declaration in phoenix_tables.h"),
        "nl": dict(
            title="Phoenix ROM-tabellen (`phoenix_tables.c`)",
            intro=("Elke speldata-tabel uit de programma-ROM, met zijn ROM-bereik, waar hij voor "
                   "dient, en de C-functies die hem lezen. Gegenereerd door "
                   "`tools/generate_table_reference.py` uit de doc-commentaren in "
                   "`phoenix_tables.h` en een scan van de C-bronnen — niet met de hand aanpassen."),
            counth="Tabellen", rangeh="ROM-bereik", sizeh="Grootte", useh="Gelezen door",
            toc="Inhoud", none="geen lezer gevonden in de C-bronnen",
            usedby="Gelezen door", purpose="Doel", back="Terug naar", via="via", nodoc="geen doc-commentaar direct boven de declaratie in phoenix_tables.h"),
    }[lang]

    out = [f"# {t['title']}", "", t["intro"], "",
           f"**{t['counth']}: {len(tables)}**", "", "---", "",
           f"## {t['toc']}", ""]

    # overview table, sorted by ROM address so it reads like a memory map
    ordered = sorted(tables, key=lambda x: x["asm"][0] if x["asm"] else "ZZZZ")
    out.append(f"| {t['rangeh']} | {t['counth'][:-1] if lang=='en' else 'Tabel'} | {t['sizeh']} | {t['useh']} |")
    out.append("| --- | --- | --- | --- |")
    for tb in ordered:
        rng = f"`${tb['asm'][0]}-${tb['asm'][1]}`" if tb["asm"] else "—"
        anchor = tb["name"].replace("_", "-")
        readers = users.get(tb["name"], [])
        files = sorted({e[0] for e in readers})
        rd = ", ".join(f"`{f}`" for f in files) if files else "—"
        out.append(f"| {rng} | [`{tb['name']}`](#{anchor}) | `{tb['size']}` | {rd} |")
    out += ["", "---", ""]

    for tb in ordered:
        out.append(f"## `{tb['name']}`")
        out.append("")
        if tb["asm"]:
            out.append(f"**ROM:** `${tb['asm'][0]}-${tb['asm'][1]}` · **{t['sizeh']}:** `{tb['size']}`")
            out.append("")
        out.append(f"**{t['purpose']}.** {tb['text']}" if tb["text"] else f"*{t['nodoc']}*")
        out.append("")
        readers = users.get(tb["name"], [])
        if readers:
            out.append(f"**{t['usedby']}:**")
            out.append("")
            for fname, fn, via in sorted(readers, key=lambda e: (e[0], e[1] or '')):
                where = f"`{fname}` → `{fn}()`" if fn else f"`{fname}`"
                if via:
                    where += f" ({t['via']} `{via}()`)"
                out.append(f"- {where}")
        else:
            out.append(f"*{t['none']}*")
        out += ["", "---", ""]

    out.append(f"{t['back']} [`README.md`](README.md).")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", type=Path, default=PROJECT / "c-annotated")
    args = ap.parse_args()

    tables = read_tables()
    if not tables:
        raise SystemExit("no tables found in phoenix_tables.h")
    users = find_users([t["name"] for t in tables])

    for lang in ("en", "nl"):
        path = args.outdir / lang / "phoenix-tables.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(tables, users, lang))
        label = path.relative_to(PROJECT) if PROJECT in path.parents else path
        print("wrote", label)

    linked = sum(1 for t in tables if users.get(t["name"]))
    print(f"{len(tables)} tables, {linked} with at least one reader in the C sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
