#!/usr/bin/env python3
"""Generate HTML pages for Markdown documents referenced by the knowledge graph."""
import argparse, html, json, os, re, sys
from pathlib import Path
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
def paths(graph):
    out=set()
    for node in json.loads(graph.read_text(encoding="utf-8"))["nodes"]:
        docs=node.get("evidence",{}).get("documentation",[])
        out.update(([docs] if isinstance(docs,str) else docs) if docs else [])
    return sorted(p for p in out if isinstance(p,str) and p.endswith(".md"))
def render(source,destination,explorer):
    lines=source.read_text(encoding="utf-8").splitlines()
    body="<pre>" + html.escape("\n".join(lines)) + "</pre>"
    back=Path(os.path.relpath(explorer,destination.parent)).as_posix()
    return '<!doctype html><html><head><meta charset="utf-8"><title>'+html.escape(source.stem)+'</title><style>:root{color-scheme:dark}body{max-width:1000px;margin:auto;padding:2rem;background:#09111a;color:#e8f0f7;font:16px/1.6 system-ui}a{color:#82cdf6}pre{white-space:pre-wrap;overflow:auto;padding:1rem;background:#071018;border:1px solid #29455d;font:.9rem/1.5 ui-monospace,monospace}</style></head><body><p><a href="'+back+'">← Back to knowledge base</a></p><h1>'+html.escape(source.stem)+'</h1>'+body+'</body></html>'
def main():
    parser=argparse.ArgumentParser();parser.add_argument("--graph",type=Path,required=True);parser.add_argument("--root",type=Path,default=Path("c-phoenix"));parser.add_argument("--check",action="store_true");args=parser.parse_args()
    explorer=args.root/"c-annotated/knowledge-base-explorer/index.html";stale=[]
    for relative in paths(args.graph):
        source=args.root/relative;destination=source.with_suffix(".html");rendered=render(source,destination,explorer)
        if args.check:
            if not destination.exists() or destination.read_text(encoding="utf-8")!=rendered: stale.append(destination)
        else: destination.write_text(rendered,encoding="utf-8")
    if stale: print("Knowledge-base HTML is stale ("+str(len(stale))+" files)",file=sys.stderr);return 1
    print("Knowledge-base HTML: "+("current" if args.check else "generated")+" ("+str(len(paths(args.graph)))+" files)");return 0
if __name__=="__main__": raise SystemExit(main())
