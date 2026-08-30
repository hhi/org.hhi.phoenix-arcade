#!/usr/bin/env python3
"""Generate standalone, syntax-coloured C source pages for the ASM viewer."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

KEYWORDS = re.compile(r"\b(?:auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)\b")
NUMBER = re.compile(r"\b(?:0x[0-9A-Fa-f]+|\d+)\b")
COMMENT = re.compile(r"(//.*|/\*.*?\*/)")
STRING = re.compile(r'("(?:\\.|[^"\\])*")')


def highlight(line: str) -> str:
    escaped = html.escape(line)
    parts = COMMENT.split(escaped)
    for index in range(0, len(parts), 2):
        code = STRING.sub(r'<span class="string">\1</span>', parts[index])
        code = NUMBER.sub(r'<span class="number">\g<0></span>', code)
        parts[index] = KEYWORDS.sub(r'<span class="keyword">\g<0></span>', code)
    for index in range(1, len(parts), 2):
        parts[index] = f'<span class="comment">{parts[index]}</span>'
    return "".join(parts)


def render(source: Path) -> str:
    lines = source.read_text(encoding="utf-8").splitlines()
    body = "\n".join(
        f'<span class="line" id="L{number}" data-line="{number}">{highlight(line) or " "}</span>'
        for number, line in enumerate(lines, 1)
    )
    title = html.escape(source.name)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Phoenix C source</title>
<style>
:root {{ color-scheme: dark; --bg:#101419; --panel:#182027; --code:#0c1116; --text:#d8e0e8; --muted:#92a2b2; --accent:#77d7ff; --border:#2d3a44; }}
body {{ margin:0; background:var(--bg); color:var(--text); font:16px/1.45 system-ui,sans-serif; }} header {{ position:sticky; top:0; padding:1rem 2rem; border-bottom:1px solid var(--border); background:var(--panel); }} header a {{ color:var(--accent); }} main {{ padding:1.5rem 2rem; }} pre {{ margin:0; overflow:auto; padding:1rem; border:1px solid var(--border); background:var(--code); font:.86rem/1.45 ui-monospace,SFMono-Regular,Menlo,monospace; }} .line {{ display:block; padding:0 .5rem; min-height:1.45em; }} .line::before {{ content:attr(data-line); display:inline-block; width:4.5em; margin-right:1em; color:var(--muted); text-align:right; user-select:none; }} .line:target {{ background:#4b3f1a; outline:1px solid #ffd166; }} .keyword {{ color:#c099ff; }} .number {{ color:#9ece6a; }} .string {{ color:#e6b673; }} .comment {{ color:#9aa8b7; font-style:italic; }}
</style></head><body><header><a href="../code-annotated.html">← Back to Phoenix ASM</a><h1>{title}</h1></header><main><pre><code>{body}</code></pre></main></body></html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "context/source")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sources = sorted(args.source_root.glob("*.c"))
    if not sources:
        raise ValueError(f"No C sources found in {args.source_root}")
    stale = []
    for source in sources:
        destination = args.output_dir / f"{source.stem}.html"
        rendered = render(source)
        if args.check:
            if not destination.exists() or destination.read_text(encoding="utf-8") != rendered:
                stale.append(destination)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(rendered, encoding="utf-8")
    if stale:
        print("Stale C source pages: " + ", ".join(str(path) for path in stale), file=sys.stderr)
        return 1
    print(f"C source pages: {'current' if args.check else 'generated'} ({len(sources)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
