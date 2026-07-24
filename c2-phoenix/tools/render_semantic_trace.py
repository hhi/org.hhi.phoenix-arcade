#!/usr/bin/env python3
"""Create a standalone C2 high-resolution canvas viewer from semantic frames."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def html_document(title: str, document: dict) -> str:
    payload = json.dumps(document, separators=(",", ":")).replace("<", "\\u003c")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root {{ color-scheme: dark; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
body {{ margin: 0; background: #101820; color: #e8f0f7; }}
main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
h1 {{ font-size: 22px; margin: 0 0 6px; }} p {{ color: #a8bbc8; margin: 0 0 18px; }}
.layout {{ display: grid; grid-template-columns: minmax(360px, 2fr) minmax(280px, 1fr); gap: 22px; }}
canvas {{ width: 100%; max-width: 832px; aspect-ratio: 13 / 16; background: #06131a; border: 1px solid #355263; image-rendering: auto; }}
.panel {{ border: 1px solid #355263; padding: 14px; background: #13232e; }}
button {{ color: #e8f0f7; background: #1d3341; border: 1px solid #527185; padding: 8px 12px; font: inherit; cursor: pointer; }}
button:disabled {{ opacity: .45; cursor: not-allowed; }} input {{ width: 100%; accent-color: #ffcd4a; }}
.controls {{ display: grid; grid-template-columns: auto auto 1fr; gap: 8px; align-items: center; }}
dl {{ display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 7px 12px; font-size: 13px; }} dt {{ color: #98adbd; }} dd {{ margin: 0; overflow-wrap: anywhere; }}
.legend {{ display: grid; gap: 8px; font-size: 13px; }} .swatch {{ display: inline-block; width: 12px; height: 12px; margin-right: 7px; vertical-align: -1px; }}
.events {{ margin: 0; padding-left: 18px; color: #cbd8e1; font-size: 12px; line-height: 1.45; }}
@media (max-width: 820px) {{ main {{ padding: 16px; }} .layout {{ grid-template-columns: 1fr; }} }}
</style></head><body><main>
<h1>{html.escape(title)}</h1><p>Semantic C2 presentation. Shapes and colours are original renderer choices, not ROM or PROM output.</p>
<div class="layout"><section><canvas id="field" width="832" height="1024"></canvas><div class="controls"><button id="previous" aria-label="Previous frame">Previous</button><button id="play" aria-label="Play">Play</button><input id="frame" type="range" min="0" value="0"></div></section>
<aside class="panel"><h2>Frame</h2><dl id="meta"></dl><h2>Mothership</h2><dl id="mothership"></dl><h2>Theme</h2><div class="legend"><span><i class="swatch" style="background:#63d8ff"></i>player and bullets</span><span><i class="swatch" style="background:#f1d65c"></i>alien formation</span><span><i class="swatch" style="background:#ff7d63"></i>birds</span></div><h2>Events</h2><ul id="events" class="events"></ul><p id="count"></p></aside></div>
</main><script>const trace={payload};
const frames=trace.frames, canvas=document.querySelector('#field'), ctx=canvas.getContext('2d'), slider=document.querySelector('#frame'), meta=document.querySelector('#meta'), mothership=document.querySelector('#mothership'), count=document.querySelector('#count'), events=document.querySelector('#events'), play=document.querySelector('#play');
let index=0, playing=false, progress=0, lastTimestamp=null, animationRequest=null; slider.max=Math.max(0,frames.length-1); const PLAYBACK_FRAME_MS=1000/40;
const colour={{player_ship:'#63d8ff',player_bullet:'#a7ecff',above_player_bullet:'#a7ecff',enemy_bullet:'#ff9e62',alien:'#f1d65c',bird:'#ff7d63'}};
function point(object){{const p=object.position; if(!p)return null; return {{x:p.x*4,y:p.y*4}};}}
function drawObject(object){{if(!(object.visible ?? object.active))return; const p=point(object); if(!p)return; ctx.save();ctx.translate(p.x,p.y);ctx.fillStyle=colour[object.kind]||'#f5f5f5';ctx.strokeStyle='#ffffff';ctx.lineWidth=2;
if(object.kind==='player_ship'){{ctx.beginPath();ctx.moveTo(0,-18);ctx.lineTo(16,15);ctx.lineTo(0,9);ctx.lineTo(-16,15);ctx.closePath();ctx.fill();ctx.stroke();}}
else if(object.kind==='bird'){{ctx.beginPath();ctx.ellipse(0,0,13,8,0,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.moveTo(-6,0);ctx.lineTo(-22,-12);ctx.lineTo(-13,7);ctx.closePath();ctx.fill();ctx.beginPath();ctx.moveTo(7,-1);ctx.lineTo(18,-5);ctx.lineTo(8,5);ctx.closePath();ctx.fill();}}
else if(object.kind==='alien'){{ctx.beginPath();ctx.arc(0,0,12,Math.PI,0);ctx.lineTo(12,10);ctx.lineTo(5,6);ctx.lineTo(0,14);ctx.lineTo(-5,6);ctx.lineTo(-12,10);ctx.closePath();ctx.fill();ctx.stroke();}}
else if(object.kind==='bird_explosion'||object.kind==='player_explosion'){{const radius=object.kind==='player_explosion'?22:14;ctx.fillStyle='#ff7452';ctx.beginPath();for(let point=0;point<8;point+=1){{const angle=point*Math.PI/4,outer=point%2?radius*.45:radius,x=Math.cos(angle)*outer,y=Math.sin(angle)*outer;if(point===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}}ctx.closePath();ctx.fill();ctx.stroke();}}
else if(object.kind==='shield_segments'){{ctx.strokeStyle='#80eeff';ctx.lineWidth=4;ctx.beginPath();ctx.arc(0,0,26,Math.PI*.15,Math.PI*.85);ctx.stroke();}}
else{{ctx.fillRect(-3,-10,6,20);}}ctx.restore();}}
function drawImpact(event,age){{const p=event.position;if(!p)return;ctx.save();ctx.translate(p.x*4,p.y*4);ctx.globalAlpha=Math.max(.2,1-age*.24);ctx.strokeStyle='#fff3a3';ctx.fillStyle='#ff7452';ctx.lineWidth=3;const radius=10+age*8;ctx.beginPath();for(let point=0;point<8;point+=1){{const angle=point*Math.PI/4,outer=point%2?radius*.5:radius,x=Math.cos(angle)*outer,y=Math.sin(angle)*outer;if(point===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);}}ctx.closePath();ctx.fill();ctx.stroke();ctx.restore();}}
function eventText(event){{if(event.type==='score_changed')return `${{event.player}} score: ${{event.from}} -> ${{event.to}}`;if(event.type==='lives_changed')return `${{event.player}} lives: ${{event.from}} -> ${{event.to}}`;if(event.type==='level_round_changed')return `level ${{event.level}}, round ${{event.round}}`;if(event.type==='game_state_changed')return `state: ${{event.state}}`;if(event.type==='impact_observed')return `impact: ${{event.target}}`;return event.type.replaceAll('_',' ') + (event.object ? `: ${{event.object}}` : '');}}
function interpolatedObjects(frame,next,amount){{const following=new Map(next.objects.map(object=>[object.key,object]));return frame.objects.map(object=>{{const successor=following.get(object.key);if(!(object.visible ?? object.active)||!(successor&&(successor.visible ?? successor.active))||!object.position||!successor.position)return object;return {{...object,position:{{x:object.position.x+(successor.position.x-object.position.x)*amount,y:object.position.y+(successor.position.y-object.position.y)*amount}}}};}});}}
function recentImpacts(){{const impacts=[];for(let age=0;age<4&&index-age>=0;age+=1){{for(const event of frames[index-age].events||[])if(event.type==='impact_observed')impacts.push([event,age]);}}return impacts;}}
function render(amount=0){{const frame=frames[index], next=frames[Math.min(index+1,frames.length-1)], scores=frame.game.scores||{{}}, lives=frame.game.lives||{{}}, mothershipObject=frame.objects.find(object=>object.kind==='mothership');ctx.clearRect(0,0,canvas.width,canvas.height);ctx.strokeStyle='#1b3a49';ctx.lineWidth=2;for(let x=0;x<=832;x+=128){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,1024);ctx.stroke();}}for(let y=0;y<=1024;y+=128){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(832,y);ctx.stroke();}}interpolatedObjects(frame,next,amount).forEach(drawObject);recentImpacts().forEach(([event,age])=>drawImpact(event,age));slider.value=index;meta.innerHTML=`<dt>recorded frame</dt><dd>${{frame.frame}}</dd><dt>player</dt><dd>${{frame.game.player}}</dd><dt>level</dt><dd>${{frame.game.level}}</dd><dt>round</dt><dd>${{frame.game.round}}</dd><dt>state</dt><dd>${{frame.game.state}}</dd><dt>player 1 score</dt><dd>${{scores.player1 ?? 'unknown'}}</dd><dt>player 2 score</dt><dd>${{scores.player2 ?? 'unknown'}}</dd><dt>player 1 lives</dt><dd>${{lives.player1 ?? 'unknown'}}</dd><dt>player 2 lives</dt><dd>${{lives.player2 ?? 'unknown'}}</dd>`;mothership.innerHTML=`<dt>status</dt><dd>${{mothershipObject?.appearance.motion||'inactive'}}</dd>`;events.replaceChildren();const currentEvents=frame.events||[];if(!currentEvents.length){{const item=document.createElement('li');item.textContent='no state transition';events.append(item);}}else currentEvents.forEach(event=>{{const item=document.createElement('li');item.textContent=eventText(event);events.append(item);}});count.textContent=`${{frame.objects.filter(o=>o.visible ?? o.active).length}} visible semantic objects`;}}
function step(amount){{index=Math.max(0,Math.min(frames.length-1,index+amount));progress=0;render();}}
function animate(timestamp){{if(!playing)return;if(lastTimestamp===null)lastTimestamp=timestamp;progress+=(timestamp-lastTimestamp)/PLAYBACK_FRAME_MS;lastTimestamp=timestamp;while(progress>=1&&index<frames.length-1){{index+=1;progress-=1;}}if(index===frames.length-1){{playing=false;progress=0;play.textContent='Play';render();return;}}render(progress);animationRequest=requestAnimationFrame(animate);}}
document.querySelector('#previous').onclick=()=>step(-1);slider.oninput=()=>{{playing=false;play.textContent='Play';index=Number(slider.value);progress=0;render();}};play.onclick=()=>{{if(playing){{playing=false;play.textContent='Play';return;}}playing=true;lastTimestamp=null;play.textContent='Pause';animationRequest=requestAnimationFrame(animate);}};render();
</script></body></html>"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("semantic_trace", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="C2-Phoenix semantic replay")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    document = json.loads(args.semantic_trace.read_text(encoding="utf-8"))
    if document.get("schema") != "org.hhi.phoenix.c2.semantic-frame/v1":
        raise ValueError("unsupported semantic frame contract")
    args.output.write_text(html_document(args.title, document), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
