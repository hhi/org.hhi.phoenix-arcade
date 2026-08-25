#!/usr/bin/env python3
"""Render a self-contained interactive view of knowledge-graph.json."""

import argparse
import json
import pathlib
import sys


HTML = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phoenix Knowledge Base Explorer</title>
<style>
:root{color-scheme:light;--ink:#19324a;--muted:#627488;--line:#c8d6e1;--accent:#1677a6;--soft:#edf5f8}*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,sans-serif;color:var(--ink);background:#edf3f7}header{padding:16px 22px;background:#19324a;color:#fff}h1{font-size:20px;margin:0}header p{margin:3px 0 0;color:#cfdeea}main{display:grid;grid-template-columns:310px 1fr;min-height:calc(100vh - 82px);background:var(--line);gap:1px}aside,article{background:#fff}aside{padding:14px;overflow:auto}input,select{width:100%;font:inherit;padding:8px;border:1px solid var(--line);border-radius:5px;margin:0 0 8px}#results{margin-top:9px}.result{width:100%;border:0;background:transparent;padding:8px;text-align:left;border-radius:5px;cursor:pointer;color:inherit}.result:hover,.result.selected{background:var(--soft)}.kind{font-size:11px;color:var(--muted)}article{padding:22px;overflow:auto}h2{margin:0 0 3px;font-size:25px}.status{color:var(--muted);margin:0 0 16px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:13px}.box{border:1px solid var(--line);border-radius:7px;padding:12px}.box h3{font-size:13px;margin:0 0 7px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}.box ul{padding-left:18px;margin:0}.box a,.related{color:var(--accent);text-decoration:none}.related{background:none;border:0;padding:0;cursor:pointer;font:inherit;text-align:left}.empty{color:var(--muted);padding:12px 0}@media(max-width:720px){main{grid-template-columns:1fr}aside{max-height:40vh}}
</style>
<header><h1>Phoenix Knowledge Base Explorer</h1><p>Validated links between C, Z80, RAM/ROM, game states and technical claims.</p></header>
<main><aside><input id="query" type="search" placeholder="Search function, address, topic…" autofocus><select id="kind"><option value="">All knowledge types</option></select><div id="count" class="kind"></div><div id="results"></div></aside><article id="detail"></article></main>
<script>
const GRAPH=__DATA__;const nodes=new Map(GRAPH.nodes.map(n=>[n.id,n]));const edges=GRAPH.relations;const kinds=[...new Set(GRAPH.nodes.map(n=>n.kind))].sort();const query=document.querySelector('#query'),kind=document.querySelector('#kind'),results=document.querySelector('#results'),detail=document.querySelector('#detail'),count=document.querySelector('#count');let selected;
kind.append(...kinds.map(k=>{const o=document.createElement('option');o.value=k;o.textContent=k.replaceAll('-',' ');return o}));
function label(n){return n.name||n.id}function link(path){if(path.startsWith('c-annotated/'))return '../'+path.slice('c-annotated/'.length);return '../../'+path}function matches(n){const term=query.value.trim().toLowerCase();return(!kind.value||n.kind===kind.value)&&(!term||JSON.stringify(n).toLowerCase().includes(term))}function showList(){const list=GRAPH.nodes.filter(matches).sort((a,b)=>label(a).localeCompare(label(b)));count.textContent=`${list.length} of ${GRAPH.nodes.length} knowledge nodes`;results.replaceChildren(...list.slice(0,120).map(n=>{const b=document.createElement('button');b.className='result'+(n.id===selected?' selected':'');b.innerHTML=`<strong>${label(n)}</strong><br><span class="kind">${n.kind}</span>`;b.onclick=()=>select(n.id);return b}));if(!list.length)results.innerHTML='<p class="empty">No matching knowledge nodes.</p>'}function relationList(items){const ul=document.createElement('ul');items.slice(0,18).forEach(({node,kind})=>{const li=document.createElement('li'),b=document.createElement('button');b.className='related';b.textContent=`${kind}: ${label(node)}`;b.onclick=()=>select(node.id);li.append(b);ul.append(li)});return ul}function select(id){selected=id;const n=nodes.get(id),out=edges.filter(e=>e.from===id).map(e=>({kind:e.kind,node:nodes.get(e.to)})).filter(x=>x.node),inc=edges.filter(e=>e.to===id).map(e=>({kind:e.kind,node:nodes.get(e.from)})).filter(x=>x.node),docs=n.evidence?.documentation||[];detail.replaceChildren();const title=document.createElement('h2');title.textContent=label(n);const state=document.createElement('p');state.className='status';state.textContent=`${n.kind} · ${n.status||'documented'}`;detail.append(title,state);const grid=document.createElement('div');grid.className='grid';const about=document.createElement('section');about.className='box';about.innerHTML='<h3>Evidence</h3>';const pre=document.createElement('pre');pre.style.whiteSpace='pre-wrap';pre.style.margin='0';pre.textContent=JSON.stringify(Object.fromEntries(Object.entries(n).filter(([k])=>!['id','name','kind','evidence','status'].includes(k))),null,2)||'No extra metadata.';about.append(pre);grid.append(about);const docsBox=document.createElement('section');docsBox.className='box';docsBox.innerHTML='<h3>Documentation</h3>';if(docs.length){const ul=document.createElement('ul');docs.forEach(p=>{const li=document.createElement('li'),a=document.createElement('a');a.href=link(p);a.textContent=p;a.target='_blank';li.append(a);ul.append(li)});docsBox.append(ul)}else docsBox.innerHTML+='<p class="empty">No linked documentation page.</p>';grid.append(docsBox);for(const [heading,items] of [['Links from this node',out],['Links to this node',inc]]){const box=document.createElement('section');box.className='box';box.innerHTML=`<h3>${heading}</h3>`;box.append(items.length?relationList(items):Object.assign(document.createElement('p'),{className:'empty',textContent:'No graph links.'}));grid.append(box)}detail.append(grid);showList()}query.oninput=showList;kind.onchange=showList;showList();select(GRAPH.nodes.find(n=>n.kind==='c-function')?.id||GRAPH.nodes[0].id);
</script></html>'''


def render(graph_path: pathlib.Path) -> str:
    return HTML.replace("__DATA__", graph_path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(args.graph)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            print("Knowledge base explorer is stale. Regenerate it.", file=sys.stderr)
            return 1
        print("Knowledge base explorer: OK")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
