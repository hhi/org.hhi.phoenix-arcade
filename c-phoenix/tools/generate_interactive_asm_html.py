#!/usr/bin/env python3
"""Render the Phoenix ASM cross-reference Markdown as an interactive HTML page."""

import argparse
import html
import re
from pathlib import Path


LABEL_HEADING_RE = re.compile(r"^### ([A-Za-z_][A-Za-z0-9_]*):\s*$")
ORG_RE = re.compile(r"\.ORG\s+\$([0-9A-Fa-f]+)")
LEGACY_LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*$")
LEGACY_ADDRESS_RE = re.compile(r"^([0-9A-Fa-f]{4}):")
C_PORT_RE = re.compile(
    r"\*\*Ported to C:\*\* \[`(?P<function>[^`]+)`\]\(\.\./(?P<file>[^#]+\.c)#L(?P<line>\d+)\).*?"
    r"\(ASM: `(?P<ranges>[^`]+)`\)"
)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
C_SOURCE_LINK_RE = re.compile(r"(?P<source>\.\./[^#]+\.c)#L(?P<line>\d+)$")
C_ASM_RANGE_RE = re.compile(r"\[ASM:\s*(?P<start>[0-9A-Fa-f]{4})-(?P<end>[0-9A-Fa-f]{4})\]")
C_ARRAY_DECL_RE = re.compile(
    r"^\s*(?:static\s+)?(?:const\s+)?[A-Za-z_][A-Za-z0-9_\s\*]*?\s+"
    r"(?P<symbol>[A-Za-z_][A-Za-z0-9_]*)\s*\["
)
EQU_SYMBOL_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+\.EQU\s+([^;]+?)(?:\s*;\s*(.*))?$"
)
ASM_TOKEN_RE = re.compile(r"\$[0-9A-Fa-f]+|0x[0-9A-Fa-f]+|\.[A-Za-z]+|[A-Za-z_][A-Za-z0-9_]*")
CONTROL_FLOW_SEPARATOR_RE = re.compile(r"^\s*(?:RET|JP)\b", re.IGNORECASE)
Z80_MNEMONICS = {
    "ADC", "ADD", "AND", "BIT", "CALL", "CCF", "CP", "CPD", "CPDR", "CPI",
    "CPIR", "CPL", "DAA", "DEC", "DI", "DJNZ", "EI", "EX", "EXX", "HALT",
    "IM", "IN", "INC", "IND", "INDR", "INI", "INIR", "JP", "JR", "LD", "LDD",
    "LDDR", "LDI", "LDIR", "NEG", "NOP", "OR", "OTDR", "OTIR", "OUT", "OUTD",
    "OUTI", "POP", "PUSH", "RES", "RET", "RETI", "RETN", "RL", "RLA", "RLC",
    "RLCA", "RLD", "RR", "RRA", "RRC", "RRCA", "RRD", "RST", "SBC", "SCF",
    "SET", "SLA", "SLL", "SRA", "SRL", "SUB", "XOR",
}
Z80_REGISTERS = {
    "A", "AF", "AF'", "B", "BC", "C", "D", "DE", "E", "F", "H", "HL", "I",
    "IX", "IXH", "IXL", "IY", "IYH", "IYL", "L", "R", "SP",
}
EMPHASIZED_MNEMONICS = {"CALL", "RET", "JP", "JR"}
DATA_DIRECTIVES = {".DB", ".DEFB", ".DW", ".DEFW", ".DS", ".DEFS"}
LABEL_KIND_NAMES = {"code": "Code", "data": "Data", "unknown": "Other"}


def label_id(name):
    return f"label-{name.lower()}"


def label_addresses(markdown):
    """Return the most recent .ORG address for every generated label."""
    addresses = {}
    current_address = None
    for line in markdown.splitlines():
        if match := ORG_RE.search(line):
            current_address = int(match.group(1), 16)
        if match := LABEL_HEADING_RE.match(line):
            addresses[match.group(1)] = current_address
    return addresses


def label_c_references(markdown):
    """Associate each label with the preceding generated C-port reference."""
    references = {}
    pending_reference = None
    for line in markdown.splitlines():
        if match := C_PORT_RE.search(line):
            pending_reference = (match.group("file"), match.group("function"))
        if match := LABEL_HEADING_RE.match(line):
            references[match.group(1)] = pending_reference
            pending_reference = None
    return references


def c_data_representations(source_root, addresses, label_kinds):
    """Find C arrays annotated as representations of ASM data ranges."""
    ranges = []
    for path in source_root.glob("*.c"):
        pending_ranges = []
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            if match := C_ASM_RANGE_RE.search(line):
                pending_ranges.append((
                    int(match.group("start"), 16), int(match.group("end"), 16), line_number
                ))
                continue
            if pending_ranges and (match := C_ARRAY_DECL_RE.match(line)):
                for start, end, _ in pending_ranges:
                    ranges.append({
                        "start": start,
                        "end": end,
                        "file": path.name,
                        "line": line_number,
                        "symbol": match.group("symbol"),
                    })
                pending_ranges.clear()
            elif pending_ranges and line_number - pending_ranges[0][2] > 32:
                # An ASM annotation belongs to the nearby declaration, not a
                # later unrelated array in the same C source file.
                pending_ranges.clear()

    representations = {}
    for name, fallback_address in addresses.items():
        if label_kinds.get(name) != "data":
            continue
        address = label_actual_address(name, fallback_address)
        candidates = [
            item for item in ranges
            if address is not None and item["start"] <= address <= item["end"]
        ]
        if candidates:
            representations[name] = min(candidates, key=lambda item: item["end"] - item["start"])
    return representations


def label_tooltip(name, addresses, c_references, suffix=""):
    address = addresses.get(name)
    tooltip = f"{name}: (${address:04X})" if address is not None else name
    if reference := c_references.get(name):
        tooltip += f" — {reference[0]} / {reference[1]}"
    return f"{tooltip}{suffix}"


def label_actual_address(name, fallback_address):
    """Use addresses encoded in conventional Lxxxx/Txxxx labels when present."""
    if match := re.fullmatch(r"[LT]([0-9A-Fa-f]{4})", name):
        return int(match.group(1), 16)
    return fallback_address


def legacy_label_addresses(legacy_assembly):
    """Extract exact label addresses from the byte-addressed legacy listing."""
    addresses = {}
    pending_labels = []
    for line in legacy_assembly.splitlines():
        if match := LEGACY_LABEL_RE.match(line):
            pending_labels.append(match.group(1))
            continue
        if pending_labels and (match := LEGACY_ADDRESS_RE.match(line)):
            address = int(match.group(1), 16)
            for label in pending_labels:
                addresses[label] = address
            pending_labels.clear()
    return addresses


def c_function_scopes(markdown, addresses, extra_markdown=""):
    """Map labels that fall in a documented C-port ASM range to that C scope."""
    ranges = []
    for line in (markdown + "\n" + extra_markdown).splitlines():
        if not (match := C_PORT_RE.search(line)):
            continue
        for range_text in match.group("ranges").split(","):
            start_text, end_text = (part.strip() for part in range_text.split("-", maxsplit=1))
            ranges.append({
                "file": match.group("file"),
                "function": match.group("function"),
                "line": match.group("line"),
                "start": int(start_text, 16),
                "end": int(end_text, 16),
            })

    scopes = {}
    for name, fallback_address in addresses.items():
        address = label_actual_address(name, fallback_address)
        candidates = [
            scope for scope in ranges
            if address is not None and scope["start"] <= address <= scope["end"]
        ]
        if candidates:
            scopes[name] = min(candidates, key=lambda scope: scope["end"] - scope["start"])

    # Keep the scope header honest: show exactly which generated labels fall
    # within the documented address range, including local branch labels.
    for scope in ranges:
        scope["labels"] = [
            name for name, fallback_address in addresses.items()
            if (address := label_actual_address(name, fallback_address)) is not None
            and scope["start"] <= address <= scope["end"]
        ]
    return scopes


def render_scope_boundary(scope, boundary):
    if boundary == "start":
        included_labels = ", ".join(scope["labels"])
        return (
            '<div class="c-function-boundary c-function-start">'
            f'<span class="c-scope-next">C function ASM scope begins at ${scope["start"]:04X}</span>'
            f'<a class="c-source-link" href="../{scope["file"]}#L{scope["line"]}" '
            f'data-source="../{scope["file"]}" data-line="{scope["line"]}">'
            f'{scope["function"]} — {scope["file"]}</a>'
            f'<code>ASM ${scope["start"]:04X}–${scope["end"]:04X}</code>'
            f'<span class="c-scope-labels">Includes: {included_labels}</span>'
            '</div>'
        )
    return (
        '<div class="c-function-boundary c-function-end">'
        f'End C function scope: {scope["function"]} '
        f'<code>ASM ${scope["start"]:04X}–${scope["end"]:04X}</code>'
        '</div>'
    )


def render_data_representation(representation):
    return (
        '<p class="data-c-representation"><span>C data representation:</span>'
        f'<a class="c-source-link" href="../{representation["file"]}#L{representation["line"]}" '
        f'data-source="../{representation["file"]}" data-line="{representation["line"]}">'
        f'{representation["symbol"]} — {representation["file"]}</a></p>'
    )


def classify_labels(markdown):
    """Classify each labelled block from its first meaningful ASM statement."""
    lines = markdown.splitlines()
    headings = [index for index, line in enumerate(lines)
                if LABEL_HEADING_RE.match(line)]
    classifications = {}
    for position, start in enumerate(headings):
        name = LABEL_HEADING_RE.match(lines[start]).group(1)
        end = headings[position + 1] if position + 1 < len(headings) else len(lines)
        kind = "unknown"
        for line in lines[start + 1:end]:
            statement = line.strip()
            if not statement or statement.startswith(("`", ";", ".ORG")):
                continue
            first_token = statement.split(maxsplit=1)[0].upper()
            if first_token in DATA_DIRECTIVES:
                kind = "data"
                break
            if first_token in Z80_MNEMONICS:
                kind = "code"
                break
        classifications[name] = kind
    return classifications


def render_inline(text):
    escaped = html.escape(text)

    def render_link(match):
        label, href = match.groups()
        c_source_match = C_SOURCE_LINK_RE.fullmatch(href)
        if c_source_match:
            source = c_source_match.group("source")
            line = c_source_match.group("line")
            return (
                f'<a class="c-source-link" href="{html.escape(href, quote=True)}" '
                f'data-source="{html.escape(source, quote=True)}" '
                f'data-line="{line}">{label}</a>'
            )
        return f'<a href="{html.escape(href, quote=True)}">{label}</a>'

    return MARKDOWN_LINK_RE.sub(
        render_link,
        escaped,
    )


def render_asm_tokens(text, labels, label_kinds, symbols, addresses, c_references):
    """Apply Z80 syntax styling and interactive label/symbol references."""
    parts = []
    position = 0
    for match in ASM_TOKEN_RE.finditer(text):
        parts.append(html.escape(text[position:match.start()]))
        token = match.group(0)
        upper = token.upper()
        if token in symbols:
            description = symbols[token]
            tooltip = html.escape(f"{token}: {description}", quote=True)
            parts.append(
                f'<span class="symbol-ref" tabindex="0" data-tooltip="{tooltip}" '
                f'>{html.escape(token)}</span>'
            )
        elif token in labels:
            kind = label_kinds.get(token, "unknown")
            tooltip = label_tooltip(token, addresses, c_references)
            if kind == "data":
                tooltip = f"DATA reference: {tooltip}"
            parts.append(
                f'<a class="label-ref label-ref-{kind}" href="#{label_id(token)}" '
                f'data-label="{token}" data-kind="{kind}" '
                f'data-tooltip="{html.escape(tooltip, quote=True)}">{token}</a>'
            )
        elif upper in Z80_MNEMONICS:
            emphasis = " mnemonic-emphasis" if upper in EMPHASIZED_MNEMONICS else ""
            parts.append(f'<span class="mnemonic{emphasis}">{html.escape(token)}</span>')
        elif upper in Z80_REGISTERS:
            parts.append(f'<span class="register">{html.escape(token)}</span>')
        elif token.startswith("."):
            parts.append(f'<span class="directive">{html.escape(token)}</span>')
        elif token.startswith(("$", "0x")):
            parts.append(f'<span class="literal">{html.escape(token)}</span>')
        else:
            parts.append(html.escape(token))
        position = match.end()
    parts.append(html.escape(text[position:]))
    return "".join(parts)


def render_code(line, labels, label_kinds, symbols, addresses, c_references):
    # The source aligns columns with a wide leading margin; remove only that
    # margin in HTML so long annotations retain usable horizontal space.
    line = line.lstrip()
    code, separator, comment = line.partition(";")
    rendered = render_asm_tokens(code, labels, label_kinds, symbols, addresses, c_references)
    if separator:
        rendered += f'<span class="comment">;{html.escape(comment)}</span>'
    if CONTROL_FLOW_SEPARATOR_RE.match(code):
        rendered += '<span class="control-separator" aria-hidden="true"></span>'
    return rendered


def render_markdown(markdown, legacy_assembly="", legacy_markdown="", source_root=None):
    label_names = [match.group(1) for line in markdown.splitlines()
                   if (match := LABEL_HEADING_RE.match(line))]
    unique_labels = list(dict.fromkeys(label_names))
    label_set = set(unique_labels)
    addresses = label_addresses(markdown)
    addresses.update({
        name: address for name, address in legacy_label_addresses(legacy_assembly).items()
        if name in label_set
    })
    label_kinds = classify_labels(markdown)
    c_references = label_c_references(markdown)
    data_representations = c_data_representations(
        source_root or Path(__file__).resolve().parents[1], addresses, label_kinds
    )
    for name, representation in data_representations.items():
        c_references[name] = (representation["file"], representation["symbol"])
    scopes = c_function_scopes(markdown, addresses, legacy_markdown)
    symbols = {
        match.group(1): f"{match.group(2).strip()} — {match.group(3) or 'Assembly symbol'}"
        for line in markdown.splitlines()
        if (match := EQU_SYMBOL_RE.match(line))
    }

    parts = []
    in_code = False
    in_section = False
    active_scope = None
    paragraph = []
    callout = []

    def flush_paragraph():
        if paragraph:
            parts.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_callout():
        if callout:
            parts.append('<aside class="callout">')
            parts.extend(f"<p>{render_inline(line)}</p>" for line in callout)
            parts.append("</aside>")
            callout.clear()

    for line in markdown.splitlines():
        if line.startswith("```"):
            flush_paragraph()
            flush_callout()
            if in_code:
                parts.append("</code></pre>")
            else:
                parts.append('<pre class="asm"><code>')
            in_code = not in_code
            continue

        if in_code:
            parts.append(render_code(line, label_set, label_kinds, symbols, addresses, c_references))
            continue

        heading_match = LABEL_HEADING_RE.match(line)
        if heading_match:
            flush_paragraph()
            flush_callout()
            name = heading_match.group(1)
            kind = label_kinds[name]
            tooltip = label_tooltip(name, addresses, c_references)
            scope = scopes.get(name)
            if in_section:
                parts.append("</section>")
                in_section = False
            if active_scope and active_scope != scope:
                parts.append(render_scope_boundary(active_scope, "end"))
                parts.append("</div>")
                active_scope = None
            if scope and scope != active_scope:
                parts.append('<div class="c-function-scope">')
                parts.append(render_scope_boundary(scope, "start"))
                active_scope = scope
            parts.append(
                f'<section class="asm-section" id="{label_id(name)}">'
                f'<h3><a class="permalink" href="#{label_id(name)}" '
                f'data-tooltip="{html.escape(tooltip, quote=True)}">{name}</a>'
                f'<span class="label-kind label-kind-{kind}">{LABEL_KIND_NAMES[kind]}</span></h3>'
            )
            if representation := data_representations.get(name):
                parts.append(render_data_representation(representation))
            in_section = True
            continue

        if line.startswith("# "):
            flush_paragraph()
            parts.append(f"<h1>{render_inline(line[2:])}</h1>")
            continue

        if line.startswith("## "):
            flush_paragraph()
            parts.append(f"<h2>{render_inline(line[3:])}</h2>")
            continue

        if line.startswith("> "):
            flush_paragraph()
            # A port annotation introduces the next documented ASM range.
            # Keep it outside the preceding C scope box, even when the
            # Markdown source has not reached the next label heading yet.
            if port_match := C_PORT_RE.search(line[2:]):
                if in_section:
                    # The port annotation belongs to the following .ORG
                    # banner, so it must not nest a new scope inside the
                    # preceding label section.
                    parts.append("</section>")
                    in_section = False
                if active_scope:
                    parts.append(render_scope_boundary(active_scope, "end"))
                    parts.append("</div>")
                    active_scope = None

                first_range = port_match.group("ranges").split(",", maxsplit=1)[0]
                start_text, _ = (part.strip() for part in first_range.split("-", maxsplit=1))
                start_address = int(start_text, 16)
                port_scope = next(
                    (scope for scope in scopes.values() if scope["start"] == start_address), None
                )
                if port_scope:
                    # The scope is now the single representation of this
                    # mapping. Opening it here includes the following .ORG
                    # banner and avoids a duplicate "Ported to C" callout.
                    parts.append('<div class="c-function-scope">')
                    parts.append(render_scope_boundary(port_scope, "start"))
                    active_scope = port_scope
                    continue
            if not line.startswith("> [!NOTE]"):
                callout.append(line[2:])
            continue

        if not line.strip():
            flush_paragraph()
            flush_callout()
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_callout()
    if in_code:
        parts.append("</code></pre>")
    if in_section:
        parts.append("</section>")
    if active_scope:
        parts.append(render_scope_boundary(active_scope, "end"))
        parts.append("</div>")

    navigation = "\n".join(
        f'<a class="label-nav-{label_kinds[name]}" href="#{label_id(name)}" '
        f'data-label="{name}" data-kind="{label_kinds[name]}" '
        f'data-search="{name} {label_kinds[name]}" '
        f'data-tooltip="{html.escape(label_tooltip(name, addresses, c_references), quote=True)}" '
        f'aria-label="{html.escape(label_tooltip(name, addresses, c_references), quote=True)}">'
        f'<span>{name}</span><span class="label-kind label-kind-{label_kinds[name]}">'
        f'{LABEL_KIND_NAMES[label_kinds[name]]}</span></a>'
        for name in unique_labels
    )
    return "\n".join(parts), navigation, len(unique_labels)


def page_document(content, navigation):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Interactive Phoenix Z80 assembly to C port cross-reference">
  <title>Phoenix Z80 ASM — Interactive Cross-Reference</title>
  <style>
    :root {{ color-scheme: light dark; --bg: #101419; --panel: #182027; --code: #0c1116; --text: #d8e0e8; --muted: #92a2b2; --accent: #77d7ff; --border: #2d3a44; --focus: #ffd166; --badge-text: #101419; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font: 16px/1.55 system-ui, sans-serif; }}
    a {{ color: var(--accent); }}
    .layout {{ display: grid; grid-template-columns: minmax(15rem, 21rem) minmax(0, 1fr); min-height: 100vh; }}
    aside#navigator {{ position: sticky; top: 0; height: 100vh; overflow: auto; padding: 1.25rem; background: var(--panel); border-right: 1px solid var(--border); }}
    #navigator h2 {{ font-size: 1rem; margin: 1rem 0 .5rem; }}
    #label-search {{ width: 100%; padding: .55rem .65rem; border: 1px solid var(--border); border-radius: .35rem; background: var(--code); color: var(--text); }}
    .nav-controls {{ display: flex; gap: .5rem; }}
    button {{ padding: .4rem .65rem; border: 1px solid var(--border); border-radius: .3rem; background: var(--code); color: var(--text); cursor: pointer; }}
    button:focus, a:focus, input:focus {{ outline: 2px solid var(--focus); outline-offset: 2px; }}
    #label-list {{ display: grid; gap: .12rem; margin-top: .65rem; }}
    #label-list a {{ display: flex; align-items: center; justify-content: space-between; gap: .5rem; padding: .15rem .35rem; border-radius: .25rem; color: var(--text); text-decoration: none; font: .85rem ui-monospace, monospace; }}
    #label-list a:hover, #label-list a:focus {{ background: #263b49; color: var(--accent); }}
    #label-list a[data-tooltip], .permalink[data-tooltip] {{ position: relative; }} #label-list a[data-tooltip]:hover::after, #label-list a[data-tooltip]:focus::after, .permalink[data-tooltip]:hover::after, .permalink[data-tooltip]:focus::after {{ content: attr(data-tooltip); position: absolute; z-index: 4; right: 0; bottom: calc(100% + .25rem); width: max-content; max-width: min(18rem, 90vw); padding: .35rem .5rem; border: 1px solid var(--border); border-radius: .3rem; background: var(--panel); color: var(--text); font: .78rem/1.25 system-ui, sans-serif; white-space: normal; box-shadow: 0 .3rem .8rem #0008; }}
    .label-kind {{ display: inline-block; margin-left: .55rem; padding: .06rem .35rem; border: 1px solid currentColor; border-radius: 999px; color: var(--muted); font: 700 .62rem/1.25 system-ui, sans-serif; letter-spacing: .04em; text-transform: uppercase; vertical-align: middle; }}
    .label-kind-code {{ --kind-color: #ff9e64; color: var(--kind-color); }} .label-kind-data {{ --kind-color: #7ee787; color: var(--kind-color); }} .label-kind-unknown {{ --kind-color: #92a2b2; color: var(--kind-color); }}
    .label-legend {{ display: flex; flex-wrap: wrap; gap: .25rem; margin: .45rem 0; }} .label-filter {{ display: inline-flex; align-items: center; gap: .25rem; cursor: pointer; }} .label-filter input {{ width: 1rem; height: 1rem; margin: 0; accent-color: var(--accent); }} .label-filter .label-kind {{ margin-left: 0; }} .label-filter input:checked + .label-kind {{ background: var(--kind-color); color: var(--badge-text); }} .label-filter:has(input:not(:checked)) .label-kind {{ opacity: .45; }} .label-filter input:focus-visible + .label-kind {{ outline: 2px solid var(--focus); outline-offset: 2px; }}
    main {{ min-width: 0; padding: clamp(1rem, 3vw, 3rem); }}
    h1 {{ line-height: 1.15; }} h2 {{ margin-top: 2.2rem; }} h3 {{ scroll-margin-top: 1rem; margin: 2.4rem 0 .5rem; font: 600 1.1rem ui-monospace, monospace; }}
    .permalink {{ color: var(--text); text-decoration: none; }} .permalink:hover {{ color: var(--accent); }}
    .asm {{ overflow: auto; margin: 0; padding: 1rem 1rem 1rem 1.5rem; border: 1px solid var(--border); background: var(--code); tab-size: 4; font: .86rem/1.45 ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre; }}
    .mnemonic {{ color: #6cb6ff; font-weight: 400; }} .mnemonic-emphasis {{ color: #56d4ff; font-weight: 700; }} .register {{ color: #c099ff; }} .directive {{ color: #7dcfff; }} .literal {{ color: #9ece6a; }} .comment {{ color: #9aa8b7; font-style: italic; }}
    .control-separator {{ display: block; height: 1px; margin: .4em 0; background: color-mix(in srgb, var(--border) 75%, transparent); }}
    .label-ref {{ color: #ffe08a; text-decoration: underline dotted; text-underline-offset: .2em; cursor: pointer; }} .label-ref-data {{ color: #7ee787; text-decoration-color: #7ee787; }} .label-ref-unknown {{ color: var(--muted); }}
    .label-ref:hover {{ color: var(--focus); }}
    .symbol-ref {{ color: #7ee787; text-decoration: underline dotted; text-underline-offset: .2em; cursor: help; }}
    #code-tooltip {{ position: fixed; z-index: 10; width: max-content; max-width: min(28rem, calc(100vw - 1rem)); padding: .45rem .6rem; border: 1px solid var(--border); border-radius: .35rem; background: #26343d; color: var(--text); font: .82rem/1.35 system-ui, sans-serif; white-space: normal; pointer-events: none; box-shadow: 0 .35rem 1rem #0008; }}
    .c-source-link {{ color: #9ece6a; text-decoration: underline; text-underline-offset: .15em; }}
    .data-c-representation {{ display: flex; flex-wrap: wrap; gap: .35rem .65rem; align-items: baseline; margin: -.35rem 0 .7rem; padding: .45rem .65rem; border-left: 3px solid #7ee787; background: color-mix(in srgb, #7ee787 9%, var(--panel)); font-size: .88rem; }} .data-c-representation span {{ color: var(--muted); }}
    .c-function-scope {{ margin: 2.75rem 0; padding: 1rem; border: 1px solid color-mix(in srgb, var(--accent) 62%, var(--border)); border-radius: .5rem; background: color-mix(in srgb, var(--accent) 5%, var(--code)); }} .c-function-scope .asm-section {{ position: relative; }} .c-function-scope .asm-section + .asm-section {{ border-top: 1px solid color-mix(in srgb, var(--border) 80%, transparent); margin-top: 1.25rem; padding-top: 1.25rem; }} .c-function-boundary {{ display: flex; flex-wrap: wrap; align-items: center; gap: .5rem 1rem; margin: 0 0 .75rem; padding: .7rem .8rem; border: 1px dashed var(--accent); border-top: 3px solid var(--accent); border-radius: .35rem; background: #132e3c; color: var(--text); font-size: .84rem; }} .c-function-scope > .c-function-start {{ margin: 0 0 .75rem; }} .c-function-boundary .c-scope-next {{ flex-basis: 100%; color: var(--accent); font-weight: 800; letter-spacing: .025em; }} .c-function-boundary .c-scope-labels {{ flex-basis: 100%; color: var(--muted); font-weight: 500; }} .c-function-boundary code {{ color: var(--muted); }} .c-function-end {{ margin: .75rem 0 0; border-top: 1px dashed var(--border); background: transparent; }}
    #c-viewer {{ width: min(90rem, 96vw); height: min(90vh, 60rem); padding: 0; border: 1px solid var(--border); border-radius: .5rem; background: var(--panel); color: var(--text); }}
    #c-viewer::backdrop {{ background: #000b; }} #c-viewer header {{ display: flex; justify-content: space-between; gap: 1rem; align-items: center; position: sticky; top: 0; padding: .8rem 1rem; background: var(--panel); border-bottom: 1px solid var(--border); }}
    #c-source-code {{ display: block; margin: 0; padding: 1rem; overflow: auto; height: calc(100% - 3.8rem); background: var(--code); font: .84rem/1.45 ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre; }}
    .c-line {{ display: block; padding: 0 .5rem; }} .c-line::before {{ content: attr(data-line); display: inline-block; width: 4.5em; margin-right: 1em; color: var(--muted); text-align: right; user-select: none; }} .c-line-highlight {{ background: #4b3f1a; }}
    .callout {{ margin: .75rem 0; padding: .5rem 1rem; border-left: 3px solid var(--accent); background: #162b36; }} .callout p {{ margin: .25rem 0; }}
    .asm-section:target h3 {{ color: var(--focus); }}
    .hidden, #label-list a.hidden {{ display: none; }}
    @media (prefers-color-scheme: light) {{
      :root {{ --bg: #f4f7fb; --panel: #ffffff; --code: #f8fafc; --text: #17212b; --muted: #52606d; --accent: #006e9c; --border: #b7c3cf; --focus: #8a5700; --badge-text: #17212b; }}
      #label-list a:hover, #label-list a:focus {{ background: #dcecf5; }}
      .label-kind-code {{ --kind-color: #a84d0e; color: var(--kind-color); }} .label-kind-data {{ --kind-color: #26733a; color: var(--kind-color); }} .label-kind-unknown {{ --kind-color: #52606d; color: var(--kind-color); }}
      .mnemonic {{ color: #1267b3; }} .mnemonic-emphasis {{ color: #007da8; }} .register {{ color: #7040a0; }} .directive {{ color: #00749f; }} .literal {{ color: #26733a; }} .comment {{ color: #4b5968; }}
      .control-separator {{ background: color-mix(in srgb, var(--border) 85%, transparent); }}
      .label-ref {{ color: #805900; }} .label-ref-data {{ color: #176c38; text-decoration-color: #176c38; }} .label-ref-unknown {{ color: var(--muted); }} .symbol-ref {{ color: #176c38; }} .c-source-link {{ color: #176c38; }} .data-c-representation {{ border-left-color: #26733a; background: #e9f6ec; }} #code-tooltip {{ background: #ffffff; }} .callout {{ background: #e6f4fb; }} .c-function-boundary {{ background: #e6f4fb; }} .c-line-highlight {{ background: #fff0bf; }}
    }}
    body.theme-light {{ color-scheme: light; --bg: #f4f7fb; --panel: #ffffff; --code: #f8fafc; --text: #17212b; --muted: #52606d; --accent: #006e9c; --border: #b7c3cf; --focus: #8a5700; --badge-text: #17212b; }}
    body.theme-light #label-list a:hover, body.theme-light #label-list a:focus {{ background: #dcecf5; }}
    body.theme-light .label-kind-code {{ --kind-color: #a84d0e; color: var(--kind-color); }} body.theme-light .label-kind-data {{ --kind-color: #26733a; color: var(--kind-color); }} body.theme-light .label-kind-unknown {{ --kind-color: #52606d; color: var(--kind-color); }}
    body.theme-light .mnemonic {{ color: #1267b3; }} body.theme-light .mnemonic-emphasis {{ color: #007da8; }} body.theme-light .register {{ color: #7040a0; }} body.theme-light .directive {{ color: #00749f; }} body.theme-light .literal {{ color: #26733a; }} body.theme-light .comment {{ color: #4b5968; }}
    body.theme-light .control-separator {{ background: color-mix(in srgb, var(--border) 85%, transparent); }} body.theme-light .label-ref {{ color: #805900; }} body.theme-light .label-ref-data {{ color: #176c38; text-decoration-color: #176c38; }} body.theme-light .label-ref-unknown {{ color: var(--muted); }} body.theme-light .symbol-ref, body.theme-light .c-source-link {{ color: #176c38; }} body.theme-light .data-c-representation {{ border-left-color: #26733a; background: #e9f6ec; }} body.theme-light #code-tooltip {{ background: #ffffff; }} body.theme-light .callout, body.theme-light .c-function-boundary {{ background: #e6f4fb; }} body.theme-light .c-line-highlight {{ background: #fff0bf; }}
    @media (max-width: 760px) {{ .layout {{ display: block; }} aside#navigator {{ position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--border); }} #label-list {{ max-height: 13rem; overflow: auto; }} main {{ padding: 1rem; }} }}
  </style>
</head>
<body>
  <div class="layout">
    <aside id="navigator" aria-label="Assembly label navigation">
      <strong>Phoenix ASM</strong>
      <h2>Navigate</h2>
      <div class="nav-controls"><button id="go-back" type="button">← Back</button><button id="go-forward" type="button">Forward →</button></div>
      <h2>Labels</h2>
      <label for="label-search">Filter labels</label>
      <input id="label-search" type="search" placeholder="e.g. MainLoop or data" autocomplete="off">
      <fieldset class="label-legend"><legend>Show label types</legend><label class="label-filter"><input type="checkbox" data-kind="code" checked><span class="label-kind label-kind-code">Code</span></label><label class="label-filter"><input type="checkbox" data-kind="data" checked><span class="label-kind label-kind-data">Data</span></label><label class="label-filter"><input type="checkbox" data-kind="unknown" checked><span class="label-kind label-kind-unknown">Other</span></label></fieldset>
      <nav id="label-list">{navigation}</nav>
    </aside>
    <main id="document">{content}</main>
  </div>
  <dialog id="c-viewer" aria-label="C source viewer"><header><strong id="c-source-title">C source</strong><button id="close-c-viewer" type="button">Close</button></header><code id="c-source-code"></code></dialog>
  <div id="code-tooltip" role="tooltip" hidden></div>
  <script>
    if (new URLSearchParams(location.search).get('theme') === 'light') document.body.classList.add('theme-light');
    const historyStack = [], forwardStack = [];
    const currentTarget = () => location.hash || '#document';
    const visit = (target) => {{ historyStack.push(currentTarget()); forwardStack.length = 0; location.hash = target; updateButtons(); }};
    const updateButtons = () => {{ document.querySelector('#go-back').disabled = !historyStack.length; document.querySelector('#go-forward').disabled = !forwardStack.length; }};
    document.addEventListener('click', event => {{ const link = event.target.closest('.label-ref'); if (link) {{ event.preventDefault(); visit(link.getAttribute('href')); }} }});
    document.querySelector('#go-back').addEventListener('click', () => {{ if (historyStack.length) {{ forwardStack.push(currentTarget()); location.hash = historyStack.pop(); updateButtons(); }} }});
    document.querySelector('#go-forward').addEventListener('click', () => {{ if (forwardStack.length) {{ historyStack.push(currentTarget()); location.hash = forwardStack.pop(); updateButtons(); }} }});
    const filterLabels = (resetNavigation = false) => {{ const query = document.querySelector('#label-search').value.toLowerCase(); const enabledKinds = new Set(Array.from(document.querySelectorAll('.label-filter input:checked'), input => input.dataset.kind)); document.querySelectorAll('#label-list a').forEach(link => {{ const matchesText = link.dataset.label.toLowerCase().includes(query); const matchesKind = enabledKinds.has(link.dataset.kind); link.classList.toggle('hidden', !(matchesText && matchesKind)); }}); if (resetNavigation) document.querySelector('#navigator').scrollTop = 0; }};
    document.querySelector('#label-search').addEventListener('input', filterLabels);
    document.addEventListener('change', event => {{ if (event.target.matches('.label-filter input')) filterLabels(true); }});
    const cViewer = document.querySelector('#c-viewer'), cSourceCode = document.querySelector('#c-source-code');
    document.querySelector('#close-c-viewer').addEventListener('click', () => cViewer.close());
    document.addEventListener('click', async event => {{ const link = event.target.closest('.c-source-link'); if (!link) return; event.preventDefault(); const response = await fetch(link.dataset.source); if (!response.ok) {{ alert(`Could not load ${{link.dataset.source}}`); return; }} const lines = (await response.text()).split('\\n'); cSourceCode.replaceChildren(...lines.map((text, index) => {{ const line = document.createElement('span'); line.className = 'c-line'; line.dataset.line = index + 1; line.textContent = text; return line; }})); document.querySelector('#c-source-title').textContent = `${{link.dataset.source}} : line ${{link.dataset.line}}`; cViewer.showModal(); const target = cSourceCode.querySelector(`[data-line="${{link.dataset.line}}"]`); target.classList.add('c-line-highlight'); target.scrollIntoView({{ block: 'center' }}); }});
    const codeTooltip = document.querySelector('#code-tooltip');
    const tooltipTarget = event => event.target.closest('.asm .symbol-ref, .asm .label-ref');
    const showCodeTooltip = target => {{ codeTooltip.textContent = target.dataset.tooltip; codeTooltip.hidden = false; const rect = target.getBoundingClientRect(); const tooltipRect = codeTooltip.getBoundingClientRect(); const left = Math.max(8, Math.min(rect.left, window.innerWidth - tooltipRect.width - 8)); const top = rect.bottom + tooltipRect.height + 8 > window.innerHeight ? Math.max(8, rect.top - tooltipRect.height - 8) : rect.bottom + 8; codeTooltip.style.left = `${{left}}px`; codeTooltip.style.top = `${{top}}px`; }};
    const hideCodeTooltip = () => {{ codeTooltip.hidden = true; }};
    document.addEventListener('pointerover', event => {{ const target = tooltipTarget(event); if (target) showCodeTooltip(target); }});
    document.addEventListener('pointerout', event => {{ const target = tooltipTarget(event); if (target && !target.contains(event.relatedTarget)) hideCodeTooltip(); }});
    document.addEventListener('focusin', event => {{ const target = tooltipTarget(event); if (target) showCodeTooltip(target); }});
    document.addEventListener('focusout', event => {{ if (tooltipTarget(event)) hideCodeTooltip(); }});
    filterLabels();
    updateButtons();
  </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="context/Phoenix.md")
    parser.add_argument("output", nargs="?", default="context/Phoenix.html")
    args = parser.parse_args()

    source = Path(args.input)
    destination = Path(args.output)
    legacy_assembly = source.with_name("code-annotated.asm")
    legacy_markdown = source.with_name("code-annotated.md")
    content, navigation, labels = render_markdown(
        source.read_text(encoding="utf-8"),
        legacy_assembly.read_text(encoding="utf-8") if legacy_assembly.exists() else "",
        legacy_markdown.read_text(encoding="utf-8") if legacy_markdown.exists() else "",
    )
    destination.write_text(page_document(content, navigation), encoding="utf-8")
    print(f"{destination} generated successfully with {labels} labels")


if __name__ == "__main__":
    main()
