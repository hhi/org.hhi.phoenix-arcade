#!/usr/bin/env python3
"""Generate the animated explainer for the input bot's search loop.

The bot is what produced 50 of the 59 input scripts behind the coverage
figures, so it deserves a picture rather than a footnote. This emits the
English and Dutch versions from one template, so the two cannot drift apart.

Output: demo/input-bot-search.svg and demo/input-bot-search.nl.svg

Usage:  python3 c-phoenix/tools/generate_input_bot_visual.py [--outdir DIR]
"""

import argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE.parents[1] / "demo"

T = {
"en": dict(
 aria="Animated explanation of the Phoenix input bot: you name a target, the bot mutates a seed input script into twenty variations, replays each one headless, scores it against the target, and keeps the best. In generations mode the winner becomes the seed of the next round, so the search climbs.",
 title="How the input bot finds a test case",
 sub="You name what you want to see. It plays thousands of variations and keeps the ones that get there.",
 s1=("SEED", "one input script"), s2=("MUTATE", "20 variations"),
 s3=("REPLAY", "headless, no window"), s4=("SCORE", "against your target"),
 s5=("KEEP", "the best 3"),
 s1a="basic_playthrough", s2a="press / release", s3a="--no-render",
 s4a="gameplay_level_9", s5a="rank_01",
 ret="generation + 1  ·  the winner becomes the new seed",
 gen="generation", best="best score",
 f1="9 scripts written by hand", f2="50 written by the bot",
 f3="79.9% of the C functions reached",
 note="Without --generations the search is one flat round: every candidate comes from the same seed and the winner is never reused."),
"nl": dict(
 aria="Geanimeerde uitleg van de Phoenix input-bot: je noemt een doel, de bot muteert een seed-inputscript tot twintig varianten, speelt elke variant headless af, scoort hem tegen het doel en houdt de beste. In generatiemodus wordt de winnaar de seed van de volgende ronde, zodat de zoektocht klimt.",
 title="Hoe de input-bot een testcase vindt",
 sub="Jij noemt wat je wilt zien. Hij speelt duizenden varianten en houdt de varianten die er komen.",
 s1=("SEED", "één inputscript"), s2=("MUTEER", "20 varianten"),
 s3=("SPEEL AF", "headless, geen venster"), s4=("SCOOR", "tegen jouw doel"),
 s5=("HOUD", "de beste 3"),
 s1a="basic_playthrough", s2a="press / release", s3a="--no-render",
 s4a="gameplay_level_9", s5a="rank_01",
 ret="generatie + 1  ·  de winnaar wordt de nieuwe seed",
 gen="generatie", best="beste score",
 f1="9 scripts met de hand geschreven", f2="50 door de bot geschreven",
 f3="79,9% van de C-functies bereikt",
 note="Zonder --generations is de zoektocht één vlakke ronde: elke kandidaat komt uit dezelfde seed en de winnaar wordt nooit hergebruikt."),
}

W, H = 880, 372
BX = [26, 194, 362, 530, 698]      # box left edges
BW, BY, BH = 156, 104, 132
CY = BY + BH / 2                    # arrow line
SCORES = ["148 300", "212 900", "265 400"]

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build(t):
    b = []
    a = b.append
    a(f'<rect class="bg" width="{W}" height="{H}"/>')
    a(f'<text class="h1" x="26" y="34">{esc(t["title"])}</text>')
    a(f'<text class="sub" x="26" y="56">{esc(t["sub"])}</text>')

    # generation badge + running best, both stepping once per loop
    a(f'<rect class="badge" x="{W-236}" y="18" width="210" height="46" rx="6"/>')
    a(f'<text class="tag" x="{W-222}" y="36">{esc(t["gen"])}</text>')
    for i in range(3):
        a(f'<text class="genno g{i+1}" x="{W-152}" y="37">{i+1} / 3</text>')
    a(f'<text class="tag" x="{W-222}" y="55">{esc(t["best"])}</text>')
    for i, s in enumerate(SCORES):
        a(f'<text class="scoreno g{i+1}" x="{W-152}" y="56">{s}</text>')

    # the five stations
    for i, (bx, key, sub) in enumerate([
            (BX[0], *t["s1"]), (BX[1], *t["s2"]), (BX[2], *t["s3"]),
            (BX[3], *t["s4"]), (BX[4], *t["s5"])]):
        a(f'<rect class="panel st{i+1}" x="{bx}" y="{BY}" width="{BW}" height="{BH}" rx="7"/>')
        a(f'<text class="step" x="{bx+12}" y="{BY+24}">{i+1}</text>')
        a(f'<text class="lbl" x="{bx+32}" y="{BY+24}">{esc(key)}</text>')
        a(f'<text class="note" x="{bx+12}" y="{BY+42}">{esc(sub)}</text>')

    # 1 - a little script: frame / button lines
    x, y = BX[0] + 14, BY + 58
    for r in range(4):
        a(f'<text class="mono" x="{x}" y="{y + r*15}">{[" 120 fire  press"," 128 fire  rel"," 210 left  press"," 246 left  rel"][r]}</text>')
    a(f'<text class="tag" x="{x}" y="{BY+BH-9}">{esc(t["s1a"])}</text>')

    # 2 - three candidate scripts fanning out, each with an altered line
    for k in range(3):
        gy = BY + 52 + k * 22
        a(f'<g class="fan f{k+1}">')
        a(f'<rect class="cand" x="{BX[1]+16}" y="{gy}" width="118" height="18" rx="3"/>')
        a(f'<text class="mono2" x="{BX[1]+22}" y="{gy+13}">{["+ fire  @ 340","- left  @ 210","+ shield@ 512"][k]}</text>')
        a('</g>')
    a(f'<text class="tag" x="{BX[1]+16}" y="{BY+BH-9}">{esc(t["s2a"])}</text>')

    # 3 - a headless screen: player moves, a bird descends, a shot rises
    sx, sy, sw, sh = BX[2] + 30, BY + 52, 96, 58
    a(f'<rect class="screen" x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="3"/>')
    a(f'<g class="birdfall"><rect class="bird" x="{sx+40}" y="{sy+8}" width="9" height="7" rx="1"/></g>')
    a(f'<g class="shot"><rect class="shotpx" x="{sx+46}" y="{sy+40}" width="2" height="7"/></g>')
    a(f'<g class="ship"><path class="shippx" d="M {sx+40} {sy+52} l 6 -8 l 6 8 z"/></g>')
    a(f'<text class="tag" x="{BX[2]+16}" y="{BY+BH-9}">{esc(t["s3a"])}</text>')

    # 4 - the target line and a score that lands
    a(f'<text class="mono" x="{BX[3]+14}" y="{BY+62}">--target</text>')
    a(f'<text class="target" x="{BX[3]+14}" y="{BY+80}">{esc(t["s4a"])}</text>')
    a(f'<text class="verdict hitmark" x="{BX[3]+14}" y="{BY+104}">hit  +50 000</text>')
    a(f'<text class="tag" x="{BX[3]+14}" y="{BY+BH-9}">coverage.json</text>')

    # 5 - the kept ranking, top row highlighted
    for r in range(3):
        yy = BY + 52 + r * 20
        cls = "keeprow best" if r == 0 else "keeprow"
        a(f'<rect class="{cls}" x="{BX[4]+14}" y="{yy}" width="126" height="17" rx="3"/>')
        a(f'<text class="mono2" x="{BX[4]+20}" y="{yy+12}">rank {r+1}   {["265 400","240 100","198 750"][r]}</text>')
    a(f'<text class="tag" x="{BX[4]+14}" y="{BY+BH-9}">{esc(t["s5a"])}</text>')

    # arrows between the stations
    for i in range(4):
        x0, x1 = BX[i] + BW, BX[i+1]
        a(f'<path class="wire" d="M {x0+4} {CY} H {x1-10}"/>')
        a(f'<path class="head" d="M {x1-10} {CY-4} l 7 4 l -7 4 z"/>')

    # the return arrow: only this one is the new --generations behaviour
    ry = BY + BH + 38
    a(f'<path class="retwire" d="M {BX[4]+BW/2} {BY+BH+6} V {ry} H {BX[0]+BW/2} V {BY+BH+12}"/>')
    a(f'<path class="rethead" d="M {BX[0]+BW/2-4} {BY+BH+12} l 4 -8 l 4 8 z"/>')
    a(f'<text class="ret" x="{W/2}" y="{ry-8}" text-anchor="middle">{esc(t["ret"])}</text>')

    # the token doing the rounds
    a('<g class="token"><circle r="7" class="tokdot"/></g>')

    # footer facts
    fy = H - 34
    for i, (fx, txt) in enumerate([(26, t["f1"]), (300, t["f2"]), (556, t["f3"])]):
        a(f'<circle class="dot d{i+1}" cx="{fx+5}" cy="{fy-4}" r="4"/>')
        a(f'<text class="fact" x="{fx+18}" y="{fy}">{esc(txt)}</text>')
    a(f'<text class="foot" x="26" y="{H-12}">{esc(t["note"])}</text>')
    return "\n  ".join(b)

CSS = """
    .bg      { fill:#050510; }
    .panel   { fill:#0C0C1E; stroke:#2A2A4A; stroke-width:1.5; }
    .badge   { fill:#0C0C1E; stroke:#2A2A4A; stroke-width:1.5; }
    .h1      { fill:#E8E8FF; font-family:'Segoe UI',system-ui,sans-serif; font-size:19px; font-weight:600; }
    .sub     { fill:#8888AA; font-family:'Segoe UI',system-ui,sans-serif; font-size:12.5px; }
    .lbl     { fill:#AAAACC; font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; font-weight:600; letter-spacing:.5px; }
    .step    { fill:#4444AA; font-family:'Segoe UI',system-ui,sans-serif; font-size:13px; font-weight:700; }
    .note    { fill:#777799; font-family:'Segoe UI',system-ui,sans-serif; font-size:10.5px; }
    .tag     { fill:#5E5E80; font-family:monospace; font-size:9.5px; }
    .mono    { fill:#8899CC; font-family:monospace; font-size:10.5px; }
    .mono2   { fill:#AAB4DD; font-family:monospace; font-size:9.5px; }
    .target  { fill:#FFFF66; font-family:monospace; font-size:11.5px; font-weight:bold; }
    .verdict { fill:#00FF66; font-family:'Segoe UI',system-ui,sans-serif; font-size:11.5px; font-weight:600; }
    .genno   { fill:#E8E8FF; font-family:monospace; font-size:12.5px; font-weight:bold; }
    .scoreno { fill:#00FFCC; font-family:monospace; font-size:12.5px; font-weight:bold; }
    .cand    { fill:#141428; stroke:#2A2A4A; stroke-width:1; }
    .keeprow { fill:#141428; stroke:#2A2A4A; stroke-width:1; }
    .best    { fill:#10281E; stroke:#00FF66; stroke-width:1.3; }
    .screen  { fill:#000008; stroke:#2A2A4A; stroke-width:1; }
    .bird    { fill:#FF66AA; }
    .shotpx  { fill:#FFFF66; }
    .shippx  { fill:#00FFCC; }
    .wire    { fill:none; stroke:#4444AA; stroke-width:1.5; }
    .head    { fill:#4444AA; }
    .retwire { fill:none; stroke:#00FF66; stroke-width:1.5; stroke-dasharray:5 4; opacity:.75; }
    .rethead { fill:#00FF66; opacity:.75; }
    .ret     { fill:#00CC55; font-family:'Segoe UI',system-ui,sans-serif; font-size:11.5px; }
    .tokdot  { fill:#FFFF66; }
    .fact    { fill:#AAAACC; font-family:'Segoe UI',system-ui,sans-serif; font-size:12px; }
    .foot    { fill:#66668A; font-family:'Segoe UI',system-ui,sans-serif; font-size:10.5px; }
    .d1 { fill:#4444AA; } .d2 { fill:#00FFCC; } .d3 { fill:#00FF66; }

    /* Static fallback: with no animation the sheet reads as generation 3,
       every station lit, which is exactly the state the numbers describe. */
    .g1, .g2 { opacity: 0; }
    .token   { opacity: 0; }

    @keyframes ride {
      0%    { transform: translate(104px, 170px); }
      12%   { transform: translate(104px, 170px); }
      20%   { transform: translate(272px, 170px); }
      32%   { transform: translate(272px, 170px); }
      40%   { transform: translate(440px, 170px); }
      56%   { transform: translate(440px, 170px); }
      64%   { transform: translate(608px, 170px); }
      76%   { transform: translate(608px, 170px); }
      84%   { transform: translate(776px, 170px); }
      92%   { transform: translate(776px, 274px); }
      100%  { transform: translate(104px, 274px); }
    }
    @keyframes blip { 0%,8%,100% { opacity:0; } 12%,92% { opacity:1; } }
    .token { animation: ride 8s infinite linear, blip 8s infinite linear; }

    /* each station brightens as the token reaches it */
    @keyframes lit1 { 0%,22%,100% { stroke:#2A2A4A; } 2%,20% { stroke:#6666DD; } }
    @keyframes lit2 { 0%,18%,36%,100% { stroke:#2A2A4A; } 21%,34% { stroke:#6666DD; } }
    @keyframes lit3 { 0%,38%,60%,100% { stroke:#2A2A4A; } 41%,58% { stroke:#6666DD; } }
    @keyframes lit4 { 0%,62%,80%,100% { stroke:#2A2A4A; } 65%,78% { stroke:#6666DD; } }
    @keyframes lit5 { 0%,82%,100% { stroke:#2A2A4A; } 85%,97% { stroke:#00FF66; } }
    .st1 { animation: lit1 8s infinite; } .st2 { animation: lit2 8s infinite; }
    .st3 { animation: lit3 8s infinite; } .st4 { animation: lit4 8s infinite; }
    .st5 { animation: lit5 8s infinite; }

    /* the three mutated candidates appear one by one */
    @keyframes fan { 0%,20% { opacity:0; } 26%,100% { opacity:1; } }
    .fan { animation: fan 8s infinite; }
    .f2  { animation-delay: .35s; } .f3 { animation-delay: .7s; }

    /* the replayed frame: slow on purpose, this is for reading, not for speed */
    @keyframes fall  { 0%,40% { transform: translate(0,0); } 58% { transform: translate(0,32px); } 60%,100% { transform: translate(0,32px); opacity:0; } }
    @keyframes rise  { 0%,42% { transform: translate(0,0); opacity:0; } 44% { opacity:1; } 57% { transform: translate(0,-26px); opacity:1; } 59%,100% { opacity:0; } }
    @keyframes strafe{ 0%,40% { transform: translate(0,0); } 50% { transform: translate(6px,0); } 60%,100% { transform: translate(6px,0); } }
    .birdfall { animation: fall 8s infinite ease-in; }
    .shot     { animation: rise 8s infinite linear; }
    .ship     { animation: strafe 8s infinite ease-in-out; }

    /* the verdict only lands once the score has been computed */
    @keyframes verdict { 0%,66% { opacity:0; } 70%,100% { opacity:1; } }
    .hitmark { animation: verdict 8s infinite; }

    /* the return arrow pulses as the generation rolls over */
    @keyframes ret { 0%,88% { opacity:.25; } 93%,100% { opacity:.9; } }
    .retwire, .rethead { animation: ret 8s infinite; }

    /* generation counter and running best: one step per pass, three passes */
    @keyframes show1 { 0%,32.9% { opacity:1; } 33%,100% { opacity:0; } }
    @keyframes show2 { 0%,32.9% { opacity:0; } 33%,65.9% { opacity:1; } 66%,100% { opacity:0; } }
    @keyframes show3 { 0%,65.9% { opacity:0; } 66%,100% { opacity:1; } }
    .g1 { animation: show1 24s infinite steps(1); }
    .g2 { animation: show2 24s infinite steps(1); }
    .g3 { animation: show3 24s infinite steps(1); }

    @media (prefers-reduced-motion: reduce) {
      .token, .st1, .st2, .st3, .st4, .st5, .fan, .birdfall, .shot, .ship,
      .hitmark, .retwire, .rethead, .g1, .g2, .g3 { animation: none; }
      .fan, .hitmark { opacity: 1; }
      .g1, .g2 { opacity: 0; }
      .token { opacity: 0; }
    }
"""

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
args = ap.parse_args()
args.outdir.mkdir(parents=True, exist_ok=True)

for lang, t in T.items():
    out = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
           f'role="img" aria-label="{esc(t["aria"])}">\n'
           f'  <title>{esc(t["title"])}</title>\n  <style>{CSS}  </style>\n  '
           + build(t) + "\n</svg>\n")
    name = f"input-bot-search{'' if lang == 'en' else '.nl'}.svg"
    (args.outdir / name).write_text(out, encoding="utf-8")
    print("wrote", (args.outdir / name))
