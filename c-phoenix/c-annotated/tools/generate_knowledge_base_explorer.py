#!/usr/bin/env python3
"""Generate the self-contained interactive view of the Phoenix knowledge graph."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TOPICS = [
    ("architecture", "Phoenix architecture",
     "A map of the port: its frame loop, game states and the routines that connect the cabinet to the game.",
     ("frame", "game_state", "state_", "main", "init")),
    ("cabinet", "Frame loop & cabinet",
     "Inputs, credits, player selection and the once-per-frame work that turns cabinet input into game state.",
     ("input", "coin", "credit", "cabinet", "frame", "player_select")),
    ("player", "Player, laser & shield",
     "The player ship, its laser, shield, movement and the collision work around them.",
     ("player", "shield", "bullet", "laser", "ship")),
    ("birds", "Birds & alien waves",
     "Bird formations, their animation and the script-driven attacks that make a wave behave as it does.",
     ("bird", "egg", "alien", "wave", "dive")),
    ("mothership", "Mothership",
     "The mothership's appearance, movement, damage and scoring behaviour.",
     ("mothership",)),
    ("scoring", "Collision detection & scoring",
     "How hits are detected, how scores are added and how the values are shown.",
     ("collision", "score", "bcd", "kill")),
    ("state", "Game state & level flow",
     "The state machine, level transitions, lives and the flow from one screen to the next.",
     ("game_state", "state_", "level", "life", "game_over")),
    ("attract", "Attract mode, coins & demo",
     "The title and demo sequence, credits and the decision between one and two players.",
     ("attract", "splash", "demo", "coin", "credit", "prompt")),
    ("video", "Sprite rendering & video",
     "The tile and sprite drawing paths, scrolling, star field and video RAM.",
     ("sprite", "screen", "vram", "video", "scroll", "star")),
    ("sound", "Sound hardware & synthesis",
     "The sound registers and the software models that create Phoenix's effects.",
     ("sound", "tms36", "poly", "astable", "resampler")),
]


PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phoenix knowledge base explorer</title>
<style>
:root{color-scheme:dark;--page:#09111a;--panel:#0e1b28;--panel-2:#13283b;--line:#29455d;--text:#e8f0f7;--muted:#9db1c2;--accent:#5ab5ef;--accent-bg:#1d5074;--link:#82cdf6;--code:#071018}*{box-sizing:border-box}body{margin:0;background:var(--page);color:var(--text);font:15px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}header{padding:17px max(24px,calc((100% - 1280px)/2));border-bottom:1px solid var(--line);background:#0c1723}header h1{font-size:20px;margin:0;letter-spacing:.04em}header p{margin:4px 0 0;color:var(--muted);font-size:13px}main{max-width:1280px;margin:auto;display:grid;grid-template-columns:300px minmax(0,1fr);min-height:calc(100vh - 82px)}aside{border-right:1px solid var(--line);padding:20px 14px;background:var(--panel)}#search{width:100%;padding:10px 11px;background:var(--code);border:1px solid var(--line);border-radius:5px;color:var(--text);font:inherit}nav{margin-top:18px}.root{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin:0 0 7px 8px}.topic{display:block;width:100%;text-align:left;border:0;border-left:3px solid transparent;padding:9px 10px 9px 16px;background:transparent;color:var(--text);font:inherit;cursor:pointer}.topic:hover,.topic.active{background:var(--accent-bg);border-left-color:var(--accent);color:#fff}.topic small{display:block;color:var(--muted);font-size:11px;margin-top:2px}.trace{display:block;margin:20px 8px 0;padding-top:14px;border-top:1px solid var(--line);color:var(--link);font-size:13px}section{padding:28px 32px 48px;min-width:0}h2{margin:0;font-size:24px}h3{margin:26px 0 9px;font-size:16px;color:#d9e8f5}.lead{margin:8px 0 20px;color:var(--muted);max-width:72ch}.summary{padding:14px 16px;background:var(--panel-2);border:1px solid var(--line);border-radius:6px;color:var(--muted)}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(235px,1fr));gap:10px}.card{border:1px solid var(--line);border-radius:6px;background:var(--panel);padding:12px;text-align:left;color:var(--text);font:inherit;cursor:pointer}.card:hover{border-color:var(--accent);background:#122536}.card .kind,.badge{font-size:11px;color:var(--accent);text-transform:uppercase;letter-spacing:.06em}.card strong{display:block;margin:5px 0;overflow-wrap:anywhere}.card .where{font-size:12px;color:var(--muted)}.source-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:11px}.source{border:1px solid var(--line);border-radius:6px;background:var(--panel);padding:13px}.source h3{margin:0 0 5px;font-size:14px}.source p{margin:0;color:var(--muted);font-size:13px}.source a,.relations button{color:var(--link)}a{color:var(--link)}.relations{display:flex;gap:8px;flex-wrap:wrap}.relations button{background:var(--panel-2);border:1px solid var(--line);border-radius:4px;padding:6px 8px;font:inherit;cursor:pointer}.relations button:hover{border-color:var(--accent)}.empty{color:var(--muted);padding:18px;background:var(--panel);border:1px dashed var(--line)}.back{margin:0 0 16px;padding:0;border:0;background:transparent;color:var(--link);font:inherit;cursor:pointer}.asm{margin:5px 0}.status{color:#9edcb2;font-size:13px}@media(max-width:760px){main{display:block}aside{border-right:0;border-bottom:1px solid var(--line)}nav{display:flex;overflow:auto;margin:12px -14px 0}.topic{min-width:190px}section{padding:24px 18px}}
</style>
</head>
<body><header><h1>Phoenix knowledge base explorer</h1><p>Browse the port by game system; open the exact C implementation, original Z80 range, and explanatory documentation.</p></header>
<main><aside><input id="search" type="search" placeholder="Search routines, RAM, states…" aria-label="Search knowledge base"><nav id="topics"></nav><a class="trace" href="../../tools/runtime-trace-explorer/index.html">Open recorded runtime trace ↗</a></aside><section id="content"></section></main>
<script>
const GRAPH=__DATA__;
const TOPICS=__TOPICS__;
const nodeById=new Map(GRAPH.nodes.map(node=>[node.id,node]));
const content=document.querySelector('#content'), search=document.querySelector('#search'), topicNav=document.querySelector('#topics');
let active='architecture', selected=null, query='';
const esc=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const norm=value=>JSON.stringify(value).toLowerCase();
const docs=node=>node.evidence?.documentation||[];
const asmRanges=node=>node.asm_ranges||((node.asm?.start)?[{start:node.asm.start,end:node.asm.end}]:[]);
function topicNodes(topic){const terms=topic.terms;return GRAPH.nodes.filter(node=>node.kind!=='claim'&&terms.some(term=>norm(node).includes(term))).sort((a,b)=>a.name.localeCompare(b.name)||a.id.localeCompare(b.id));}
function cLink(node){if(!node.source?.path)return '';return `<a href="../../${esc(node.source.path)}#L${node.source.line}" target="_blank">Open ${esc(node.source.path)}:${node.source.line}</a>`;}
function docLink(path){const relative=path.startsWith('c-annotated/')?`../${path.slice('c-annotated/'.length)}`:`../../${path}`;return `<a href="${esc(relative)}" target="_blank">Open ${esc(path)}</a>`;}
function asmLinks(node){const ranges=asmRanges(node);if(!ranges.length)return '<p>No Z80 range is mapped to this item.</p>';return ranges.map(range=>`<p class="asm"><a href="../../Phoenix.asm" target="_blank">Open original Z80: ${esc(range.start)}–${esc(range.end)}</a></p>`).join('');}
function renderNav(){topicNav.innerHTML='<p class="root">Phoenix knowledge base</p>'+TOPICS.map(topic=>`<button class="topic ${active===topic.key&&!query?'active':''}" data-topic="${topic.key}">${esc(topic.title)}<small>${topicNodes(topic).length} mapped items</small></button>`).join('');topicNav.querySelectorAll('button').forEach(button=>button.onclick=()=>{active=button.dataset.topic;query='';search.value='';selected=null;render();});}
function card(node){const where=node.source?.path?`${node.source.path}:${node.source.line}`:asmRanges(node).map(range=>`${range.start}–${range.end}`).join(', ')||node.id;return `<button class="card" data-node="${esc(node.id)}"><span class="kind">${esc(node.kind)}</span><strong>${esc(node.name)}</strong><span class="where">${esc(where)}</span></button>`;}
function wireCards(){content.querySelectorAll('[data-node]').forEach(button=>button.onclick=()=>{selected=button.dataset.node;render();});}
function relationButtons(node){const related=GRAPH.relations.filter(relation=>relation.from===node.id||relation.to===node.id).map(relation=>({relation,other:nodeById.get(relation.from===node.id?relation.to:relation.from)})).filter(item=>item.other);if(!related.length)return '<div class="empty">No mapped relation from this item yet.</div>';return `<div class="relations">${related.map(({relation,other})=>`<button data-node="${esc(other.id)}">${esc(relation.kind.replaceAll('-',' '))}: ${esc(other.name)}</button>`).join('')}</div>`;}
function showNode(node){const docItems=docs(node);content.innerHTML=`<button class="back" id="back">← Back to ${query?'search results':TOPICS.find(topic=>topic.key===active).title}</button><span class="badge">${esc(node.kind)}</span><h2>${esc(node.name)}</h2><p class="lead"><span class="status">${esc(node.status||'mapped')}</span> · ${esc(node.id)}</p><h3>Direct sources</h3><div class="source-grid">${node.source?.path?`<article class="source"><h3>C implementation</h3><p>This is the readable port routine.</p>${cLink(node)}</article>`:''}<article class="source"><h3>Original Z80 routine</h3><p>The address range in the original arcade program that this item maps to.</p>${asmLinks(node)}</article><article class="source"><h3>Annotated explanation</h3><p>${docItems.length?docItems.map(docLink).join('<br>'):'No linked explanation has been mapped yet.'}</p></article></div><h3>Mapped connections</h3>${relationButtons(node)}`;document.querySelector('#back').onclick=()=>{selected=null;render();};wireCards();}
function showTopic(topic){const nodes=query?GRAPH.nodes.filter(node=>node.kind!=='claim'&&norm(node).includes(query)).sort((a,b)=>a.name.localeCompare(b.name)):topicNodes(topic);const groups=['c-function','asm-routine','game-state','ram-slot','table-asset','rom-pattern'];const count=nodes.length;content.innerHTML=`<h2>${query?'Search results':esc(topic.title)}</h2><p class="lead">${query?`Everything mapped for “${esc(query)}”.`:esc(topic.description)}</p><div class="summary">${count} mapped item${count===1?'':'s'}. Select an item to see direct links to the C implementation, its original Z80 range and the explanatory documentation.</div>${groups.map(kind=>{const entries=nodes.filter(node=>node.kind===kind);return entries.length?`<h3>${esc(kind.replaceAll('-',' '))} <span class="badge">${entries.length}</span></h3><div class="cards">${entries.map(card).join('')}</div>`:''}).join('')||'<p class="empty">No mapped items match this search.</p>'}`;wireCards();}
function render(){renderNav();if(selected){showNode(nodeById.get(selected));}else{showTopic(TOPICS.find(topic=>topic.key===active));}}
search.oninput=event=>{query=event.target.value.trim().toLowerCase();selected=null;render();};render();
</script></body></html>'''


def render(graph_path: Path) -> str:
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    topics = [
        {"key": key, "title": title, "description": description, "terms": terms}
        for key, title, description, terms in TOPICS
    ]
    return PAGE.replace("__DATA__", json.dumps(graph, separators=(",", ":"))).replace(
        "__TOPICS__", json.dumps(topics, separators=(",", ":"))
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(args.graph)
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            print(f"{args.output} is stale; run make kg-explorer", file=sys.stderr)
            return 1
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
