#!/usr/bin/env python3
"""Generate the knowledge-graph architecture SVG from repository metadata."""

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

svg_content = """<svg width="1000" height="780" viewBox="0 0 1000 780" xmlns="http://www.w3.org/2000/svg" style="background:#050C08; border-radius:12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;">
  <defs>
    <!-- Glowing gradients for layers -->
    <linearGradient id="hdrGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00FFCC" />
      <stop offset="50%" stop-color="#D500F9" />
      <stop offset="100%" stop-color="#00E5FF" />
    </linearGradient>

    <linearGradient id="layerZ80" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1A261D" />
      <stop offset="100%" stop-color="#0D1A10" />
    </linearGradient>

    <linearGradient id="layerC" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#142634" />
      <stop offset="100%" stop-color="#0A1520" />
    </linearGradient>

    <linearGradient id="layerJSON" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2D1236" />
      <stop offset="100%" stop-color="#17081E" />
    </linearGradient>

    <linearGradient id="layerMD" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F2D25" />
      <stop offset="100%" stop-color="#061813" />
    </linearGradient>

    <!-- Arrow marker definitions -->
    <marker id="arrowCyan" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#00FFCC" />
    </marker>

    <marker id="arrowPurple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#D500F9" />
    </marker>

    <marker id="arrowYellow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1 L 10 5 L 0 9 z" fill="#FFCC00" />
    </marker>

    <!-- Drop Shadow -->
    <filter id="glowCyan" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <style>
    .title { font-size: 22px; font-weight: 800; fill: url(#hdrGrad); letter-spacing: 1px; }
    .subtitle { font-size: 13px; font-weight: 600; fill: #88C4A3; letter-spacing: 1px; }
    .box-title { font-size: 14px; font-weight: 700; }
    .node-label { font-size: 12px; font-weight: 600; fill: #FFFFFF; }
    .sub-label { font-size: 11px; font-family: monospace; fill: #A0C0B0; }
    .edge-label { font-size: 10px; font-family: monospace; font-weight: bold; fill: #00FFCC; }
    .code-text { font-size: 11px; font-family: monospace; fill: #00E5FF; }
  </style>

  <!-- Header Banner -->
  <text x="40" y="42" class="title">PHOENIX KENNISGRAAF ARCHITECTUUR</text>
  <text x="40" y="66" class="subtitle">SYNCHRONISATIE TUSSEN Z80 HARDWARE, C-PORT, MACHINEGRAAF (.JSON) &amp; OBSIDIAN VAULT (.MD)</text>

  <!-- ==================== TIER 1: Z80 HARDWARE & ROM LAYER ==================== -->
  <rect x="40" y="95" width="920" height="135" rx="10" fill="url(#layerZ80)" stroke="#00E676" stroke-width="1.5" stroke-dasharray="6 3" opacity="0.9" />
  <text x="60" y="122" class="box-title" fill="#00E676">1. HARDWARE &amp; Z80 ROM/RAM LAAG (Oorspronkelijke Bron van Waarheid)</text>

  <!-- Z80 ROM Box -->
  <rect x="60" y="138" width="260" height="75" rx="6" fill="#04180A" stroke="#00E676" stroke-width="1.2" />
  <text x="75" y="160" class="node-label">Z80 ROM Code &amp; Vector Tabellen</text>
  <text x="75" y="180" class="sub-label">ROM $1020-$10BF (Alien Trajecten)</text>
  <text x="75" y="196" class="sub-label">ROM $0D70-$0DB5 (Animatie Logica)</text>

  <!-- Arcade RAM Box -->
  <rect x="370" y="138" width="260" height="75" rx="6" fill="#04180A" stroke="#00E676" stroke-width="1.2" />
  <text x="385" y="160" class="node-label">Arcade RAM Geheugenkaart</text>
  <text x="385" y="180" class="sub-label">RAM $4000-$4BFF (PhoenixState)</text>
  <text x="385" y="196" class="sub-label">RAM $4370 (Alien Control Matrix)</text>

  <!-- I/O Ports Box -->
  <rect x="680" y="138" width="260" height="75" rx="6" fill="#04180A" stroke="#00E676" stroke-width="1.2" />
  <text x="695" y="160" class="node-label">Hardware I/O &amp; Sound Chips</text>
  <text x="695" y="180" class="sub-label">Poorten $5000-$7800 (DIP Switches)</text>
  <text x="695" y="196" class="sub-label">TMS3615 &amp; 555 Audio Multivibrators</text>


  <!-- ==================== TIER 2: C-PORT SOURCE CODE ==================== -->
  <rect x="40" y="260" width="920" height="135" rx="10" fill="url(#layerC)" stroke="#00E5FF" stroke-width="1.5" opacity="0.9" />
  <text x="60" y="287" class="box-title" fill="#00E5FF">2. C-PORT BRONCODE &amp; HEADERS (c-phoenix/*.c, *.h)</text>

  <!-- C File 1 -->
  <rect x="60" y="303" width="260" height="75" rx="6" fill="#061624" stroke="#00E5FF" stroke-width="1.2" />
  <text x="75" y="325" class="node-label">alien_logic.c / .h</text>
  <text x="75" y="345" class="sub-label">alien_animation_update()</text>
  <text x="75" y="361" class="sub-label">/* [ASM: 0D70-0DB5] */</text>

  <!-- C File 2 -->
  <rect x="370" y="303" width="260" height="75" rx="6" fill="#061624" stroke="#00E5FF" stroke-width="1.2" />
  <text x="385" y="325" class="node-label">phoenix_tables.c / .h</text>
  <text x="385" y="345" class="sub-label">phoenix_alien_direction_vectors</text>
  <text x="385" y="361" class="sub-label">phoenix_alien_movement_cluster_a</text>

  <!-- C File 3 -->
  <rect x="680" y="303" width="260" height="75" rx="6" fill="#061624" stroke="#00E5FF" stroke-width="1.2" />
  <text x="695" y="325" class="node-label">game_state_machine.c / .h</text>
  <text x="695" y="345" class="sub-label">GAME_STATE_PLAY = 0x03</text>
  <text x="695" y="361" class="sub-label">LEVEL_PATTERN_BIRDS_1 = 0x00</text>


  <!-- ==================== TIER 3 & TIER 4 SPLIT ==================== -->

  <!-- TIER 3: MACHINE KNOWLEDGE GRAPH JSON -->
  <rect x="40" y="425" width="445" height="235" rx="10" fill="url(#layerJSON)" stroke="#D500F9" stroke-width="1.5" opacity="0.9" />
  <text x="60" y="452" class="box-title" fill="#D500F9">3. MACHINEGRAAF (knowledge-graph.json)</text>

  <rect x="60" y="468" width="405" height="175" rx="6" fill="#14051B" stroke="#D500F9" stroke-width="1" />
  <text x="75" y="490" class="sub-label" fill="#E080FF">{{NODE_KIND_COUNT}} Node Typen ("kind"):</text>
  <text x="75" y="508" class="code-text" fill="#FF80AB">• c-function | • asm-routine | • ram-slot</text>
  <text x="75" y="524" class="code-text" fill="#FF80AB">• rom-pattern | • game-state | • table-asset</text>
  <text x="75" y="540" class="code-text" fill="#FF80AB">• claim (uit knowledge-claims.json)</text>

  <text x="75" y="565" class="sub-label" fill="#E080FF">{{RELATION_KIND_COUNT}} Relatietypen ("relations"):</text>
  <text x="75" y="583" class="code-text" fill="#D500F9">• implements | • calls | • uses-table</text>
  <text x="75" y="599" class="code-text" fill="#D500F9">• handles-state | • asserts</text>
  <text x="75" y="625" class="sub-label" fill="#00FFCC">Generator: python3 tools/generate_knowledge_graph.py</text>

  <!-- TIER 4: HUMAN OBSIDIAN MARKDOWN VAULT & ANIMATIONS -->
  <rect x="515" y="425" width="445" height="235" rx="10" fill="url(#layerMD)" stroke="#00FFCC" stroke-width="1.5" opacity="0.9" />
  <text x="535" y="452" class="box-title" fill="#00FFCC">4. OBSIDIAN VAULT &amp; SVG (c-annotated/*.md)</text>

  <rect x="535" y="468" width="405" height="175" rx="6" fill="#041812" stroke="#00FFCC" stroke-width="1" />
  <text x="550" y="490" class="sub-label" fill="#80FFE4">{{DOCUMENT_COUNT}} Geannoteerde Documenten + {{SVG_COUNT}} SVG Bestanden:</text>
  <text x="550" y="510" class="node-label">c-annotated/alien-logic.md</text>
  <text x="550" y="528" class="sub-label">Outgoing &amp; Backlink Markdown Koppelingen</text>
  <text x="550" y="550" class="node-label">animations/cluster_a/pattern_01.svg</text>
  <text x="550" y="568" class="sub-label">Interactive SVG met Arcade Display &amp; Path Motion</text>
  <text x="550" y="595" class="sub-label" fill="#FFCC00">Obsidian Settings: .obsidian/graph.json (Color Groups)</text>
  <text x="550" y="625" class="sub-label" fill="#00E5FF">Validatie: python3 tools/validate_documentation.py</text>


  <!-- ==================== CONNECTING ARROWS & DATA FLOW ==================== -->

  <!-- Top-down Arrow Tier 1 -> Tier 2 -->
  <line x1="190" y1="213" x2="190" y2="300" stroke="#00E676" stroke-width="2" marker-end="url(#arrowCyan)" />
  <text x="200" y="248" class="edge-label">Z80 Porting</text>

  <line x1="500" y1="213" x2="500" y2="300" stroke="#00E676" stroke-width="2" marker-end="url(#arrowCyan)" />
  <text x="510" y="248" class="edge-label">RAM Mapping</text>

  <!-- Mid Arrow Tier 2 -> Tier 3 (Generator) -->
  <path d="M 190,378 L 190,410 L 260,410 L 260,422" fill="none" stroke="#D500F9" stroke-width="2" marker-end="url(#arrowPurple)" />
  <text x="200" y="402" class="edge-label" fill="#D500F9">Auto Extract</text>

  <!-- Mid Arrow Tier 2 -> Tier 4 (Documentation) -->
  <path d="M 810,378 L 810,410 L 740,410 L 740,422" fill="none" stroke="#00FFCC" stroke-width="2" marker-end="url(#arrowCyan)" />
  <text x="750" y="402" class="edge-label">Annotation</text>

  <!-- Horizontal Double Arrow Tier 3 <-> Tier 4 (Evidence & Backlinks) -->
  <line x1="485" y1="520" x2="512" stroke="#FFCC00" stroke-width="2.5" marker-end="url(#arrowYellow)" />
  <line x1="515" y1="550" x2="488" stroke="#00FFCC" stroke-width="2.5" marker-end="url(#arrowCyan)" />
  <text x="435" y="508" class="edge-label" fill="#FFCC00">evidence.documentation</text>
  <text x="445" y="575" class="edge-label" fill="#00FFCC">backlinks &amp; links</text>

  <!-- FOOTER STATUS BADGE -->
  <rect x="40" y="680" width="920" height="50" rx="8" fill="#09140C" stroke="#00FFCC" stroke-width="1" />
  <text x="60" y="710" class="sub-label" font-size="12px" fill="#00FFCC">BEWIJSVOLGORDE: Z80 ASM/ROM -&gt; C-PORT CODE -&gt; GEANNOTEERDE DOCUMENTATIE -&gt; VISUELE SVG'S</text>
</svg>"""

def render_svg(project_root: Path) -> str:
    """Fill the architecture template with current graph and asset counts."""
    graph = json.loads(
        (project_root / "c-annotated" / "knowledge-graph.json").read_text(
            encoding="utf-8"
        )
    )
    replacements = {
        "{{NODE_KIND_COUNT}}": str(len({node["kind"] for node in graph["nodes"]})),
        "{{RELATION_KIND_COUNT}}": str(
            len({relation["kind"] for relation in graph["relations"]})
        ),
        "{{DOCUMENT_COUNT}}": str(len(list((project_root / "c-annotated").glob("*.md")))),
        "{{SVG_COUNT}}": str(len(list((project_root / "animations").rglob("*.svg")))),
    }
    rendered = svg_content
    for marker, value in replacements.items():
        rendered = rendered.replace(marker, value)
    ET.fromstring(rendered)
    return rendered


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("c-annotated/kennisgraaf_meta_architectuur.svg"),
        help="SVG to write (default: c-annotated/kennisgraaf_meta_architectuur.svg)",
    )
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else project_root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_svg(project_root), encoding="utf-8")
    print(f"Generated and XML-validated {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
