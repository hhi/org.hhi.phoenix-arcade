#!/usr/bin/env python3
"""Create a standalone interactive object viewer from Phoenix RAM dumps.

The viewer is intentionally limited to object families that expose explicit
position bytes or screen-address anchors in RAM. It can show one dump, or a
reference/port pair for object-level divergence inspection.
"""

import argparse
import html
import json
import pathlib
import sys

import trace_sprites


VIEWER_KINDS = (
    "player_ship",
    "player_bullet",
    "above_player_bullet",
    "enemy_bullet",
    "aliens",
    "birds",
)
POSITIONED_KINDS = ("auto", "all") + VIEWER_KINDS
AUTO_KINDS = ("player_ship", "aliens", "birds")

SCREEN_BASES = (0x4000, 0x4800)
SCREEN_COLUMNS = 26
SCREEN_ROWS = 32
TILE_SIZE = 8
FIELD_WIDTH = SCREEN_COLUMNS * TILE_SIZE
FIELD_HEIGHT = SCREEN_ROWS * TILE_SIZE


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create an interactive Phoenix object-path HTML viewer."
    )
    parser.add_argument("ram_dump", help="RAM dump written by --ram-dump")
    parser.add_argument(
        "--compare",
        metavar="RAM_DUMP",
        help="optional second RAM dump to compare against the positional traces",
    )
    parser.add_argument(
        "--kind", choices=POSITIONED_KINDS, default="auto",
        help="object family to include; auto follows alien/bird level overlays (default)",
    )
    parser.add_argument(
        "--include-kind", choices=VIEWER_KINDS, action="append", default=[],
        help="additional object family to render (repeatable)",
    )
    parser.add_argument(
        "--player", choices=("all", "1", "2"), default="all",
        help="include one player bank or all recorded player banks",
    )
    parser.add_argument("--output", required=True, help="output HTML file")
    parser.add_argument(
        "--title", default=None, help="optional title shown in the viewer"
    )
    parser.add_argument(
        "--reference-label", default="reference", help="label for the first dump"
    )
    parser.add_argument(
        "--port-label", default="port", help="label for the compared dump"
    )
    return parser.parse_args()


def selected_kinds(primary_kind, included_kinds):
    if primary_kind == "auto":
        primary = AUTO_KINDS
    elif primary_kind == "all":
        primary = VIEWER_KINDS
    else:
        primary = (primary_kind,)
    return tuple(dict.fromkeys(primary + tuple(included_kinds)))


def screen_coordinate(screen_addr):
    if screen_addr is None:
        return None, None
    for base in SCREEN_BASES:
        offset = screen_addr - base
        if 0 <= offset < 0x340:
            tile_x = SCREEN_COLUMNS - 1 - offset // SCREEN_ROWS
            tile_y = offset % SCREEN_ROWS
            return tile_x * TILE_SIZE + TILE_SIZE // 2, tile_y * TILE_SIZE + TILE_SIZE // 2
    return None, None


def viewer_sample(snapshot, scroll=0):
    screen_x, screen_y = screen_coordinate(snapshot.get("screen_addr"))
    x = snapshot.get("x")
    y = snapshot.get("y")
    # DrawBirdObject ($34CC-$34CE) takes its anchor from B4B71/B4B72. Birds
    # live in background RAM, whose physical Y coordinate is scrolled by
    # CounterB9 through $5800 (platform_sdl.c's background renderer).
    if snapshot.get("kind") == "bird":
        visual_x = screen_x
        visual_y = None if screen_y is None else (screen_y - scroll) % FIELD_HEIGHT
    else:
        visual_x = x if x is not None else screen_x
        visual_y = y if y is not None else screen_y
    return {
        field: snapshot.get(field)
        for field in (
            "frame", "player", "kind", "id", "active", "phase", "type",
            "level_and_round", "game_state", "state", "shape", "x", "y",
            "vertical_offset", "old_screen_addr", "screen_addr",
            "movement_pattern", "timer", "flags", "source",
        )
    } | {
        "key": f"{snapshot.get('player')}:{snapshot.get('kind')}:{snapshot.get('id')}",
        "visual_x": visual_x,
        "visual_y": visual_y,
        "screen_x": screen_x,
        "screen_y": screen_y,
    }


def snapshots_for_dump(ram_dump, kinds, player):
    samples = []
    frames = []
    frame_metadata = []
    for record_index, (frame, ram) in enumerate(trace_sprites.iter_frames(ram_dump)):
        frames.append(frame)
        frame_metadata.append({
            "frame": frame,
            "counter98": (
                trace_sprites.ram_byte(ram, 0x4398) << 8
                | trace_sprites.ram_byte(ram, 0x4399)
            ),
            "level_and_round": trace_sprites.ram_byte(ram, 0x43B8),
            "game_state": trace_sprites.ram_byte(ram, 0x43A4),
            "scroll": trace_sprites.ram_byte(ram, 0x43B9),
            "bird_formation_scroll": trace_sprites.ram_byte(ram, 0x4BD2),
        })
        for kind in kinds:
            for snapshot in trace_sprites.EXTRACTORS[kind](frame, ram):
                if player != "all" and snapshot["player"] != f"player{player}":
                    continue
                sample = viewer_sample(
                    snapshot, scroll=trace_sprites.ram_byte(ram, 0x43B9)
                )
                sample["record_index"] = record_index
                samples.append(sample)
    return frames, samples, frame_metadata


def html_document(title, kind, frames, samples, frame_metadata, compare_frames,
                  compare_samples, compare_metadata, labels):
    payload = {
        "kind": kind,
        "labels": labels,
        "dumps": [
            {
                "label": labels[0], "frames": frames, "samples": samples,
                "metadata": frame_metadata,
            },
            {
                "label": labels[1], "frames": compare_frames,
                "samples": compare_samples, "metadata": compare_metadata,
            },
        ],
        "compare": bool(compare_samples),
    }
    data = json.dumps(payload, separators=(",", ":")).replace("<", "\\u003c")
    safe_title = html.escape(title)
    safe_kind = html.escape(kind)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{safe_title}</title>
<style>
  :root {{ color-scheme: dark; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  body {{ margin: 0; background: #111820; color: #e5edf5; }}
  main {{ width: min(100%, 1800px); box-sizing: border-box; margin: 0 auto; padding: 24px; }}
  h1 {{ font-size: 20px; font-weight: 600; margin: 0 0 4px; }}
  p {{ color: #aebdcb; margin: 0 0 20px; }}
  .layout {{ display: grid; grid-template-columns: minmax(480px, 1fr) minmax(420px, 1fr); gap: 24px; align-items: start; min-width: 0; }}
  .visual-panel {{ min-width: 0; }}
  canvas {{ display: block; width: min(100%, 624px); height: auto; box-sizing: border-box; aspect-ratio: 13 / 16; background: #071116; border: 1px solid #40505e; image-rendering: pixelated; }}
  .controls {{ display: grid; gap: 14px; min-width: 0; }}
  label {{ color: #aebdcb; display: grid; gap: 6px; font-size: 12px; }}
  select, input, button {{ font: inherit; }}
  select, button {{ min-height: 34px; color: #e5edf5; background: #1a2834; border: 1px solid #526474; padding: 6px 8px; }}
  button:disabled {{ cursor: not-allowed; opacity: 0.45; }}
  input[type=range] {{ width: 100%; accent-color: #ffcf4a; }}
  button {{ width: 42px; cursor: pointer; }}
  .slider-line {{ display: grid; grid-template-columns: 42px 34px 1fr 34px; gap: 8px; align-items: center; }}
  .step {{ width: 34px; }}
  .frame-overview {{ display: flex; gap: 12px; flex-wrap: wrap; color: #aebdcb; font-size: 12px; }}
  .frame-overview strong {{ color: #e5edf5; font-weight: 600; }}
  dl {{ margin: 8px 0 0; display: grid; grid-template-columns: max-content 1fr; gap: 7px 12px; font-size: 13px; }}
  dt {{ color: #8ca0b2; }} dd {{ margin: 0; overflow-wrap: anywhere; }}
  .legend {{ font-size: 12px; color: #aebdcb; line-height: 1.5; }}
  .timeline {{ display: flex; gap: 1px; min-width: 0; overflow: hidden; min-height: 30px; border: 1px solid #40505e; background: #0d151c; padding: 3px; }}
  .tick {{ width: auto; min-width: 0; flex: 1 1 1px; border: 0; padding: 0; background: #20303c; }}
  .tick.event {{ background: #48728c; }}
  .tick.diff {{ background: #d6604d; }}
  .tick.current {{ outline: 2px solid #ffcf4a; z-index: 1; }}
  .toolbar {{ display: flex; gap: 8px; flex-wrap: wrap; }}
  .toolbar button {{ width: auto; }}
  .summary {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; }}
  .metric {{ border: 1px solid #40505e; padding: 8px; background: #101b24; }}
  .metric strong {{ display: block; font-size: 18px; color: #fff; }}
  .visibility {{ margin: 0; padding: 10px; border: 1px solid #40505e; }}
  .visibility legend {{ color: #aebdcb; padding: 0 4px; font-size: 12px; }}
  .visibility label {{ display: flex; align-items: center; gap: 7px; color: #e5edf5; font-size: 12px; }}
  .visibility-options {{ display: flex; gap: 14px; flex-wrap: wrap; }}
  .objects {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 8px; border: 1px solid #40505e; }}
  .object-row {{ display: grid; grid-template-columns: max-content 10px minmax(0, 1fr) max-content; gap: 8px; padding: 6px 8px; border-bottom: 1px solid #263743; border-left: 3px solid var(--slot-color); cursor: pointer; }}
  .object-row.active {{ background: #243746; box-shadow: inset 0 0 0 1px var(--slot-color); }}
  .object-row.hovered {{ background: #1d303d; box-shadow: inset 0 0 0 1px #ffcf4a; }}
  .object-row:focus-visible, .slot-card:focus-visible {{ outline: 2px solid #ffcf4a; outline-offset: -2px; }}
  .object-row.diff {{ color: #ffd6cc; }}
  .object-swatch {{ width: 10px; height: 10px; align-self: center; border: 1px solid #e5edf5; background: var(--slot-color); }}
  .slot-data {{ margin-top: 18px; }}
  .slot-data h2 {{ margin: 0 0 8px; font-size: 14px; font-weight: 600; }}
  .slot-data-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }}
  .slot-card {{ border: 1px solid #40505e; padding: 8px; background: #0d151c; }}
  .slot-card.selected {{ border-color: var(--slot-color); box-shadow: inset 0 0 0 1px var(--slot-color); }}
  .slot-card h3 {{ margin: 0 0 7px; font-size: 12px; color: #fff; }}
  .slot-card dl {{ margin: 0; grid-template-columns: minmax(74px, max-content) minmax(0, 1fr); gap: 4px 8px; font-size: 11px; }}
  @media (max-width: 960px) {{ main {{ padding: 16px; }} .layout {{ grid-template-columns: 1fr; }} }}
  @media (max-width: 520px) {{ .objects, .slot-data-grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<main>
  <h1>{safe_title}</h1>
  <p>Object-space trace for <strong>{safe_kind}</strong>. Bright markers are the selected frame; red markers indicate field differences in records present in both dumps. Extra records are reported separately.</p>
  <div class="layout">
    <section class="visual-panel">
      <canvas id="field" width="624" height="768" aria-label="Object trace"></canvas>
      <section class="slot-data" aria-label="Slot structures">
        <h2>Slot structures</h2>
        <div class="slot-data-grid" id="slotData"></div>
      </section>
    </section>
    <section class="controls">
      <label>Player <select id="player"></select></label>
      <fieldset class="visibility">
        <legend>Visible objects</legend>
        <div class="visibility-options">
          <label><input id="allObjects" type="checkbox" checked>all objects</label>
          <label><input id="showCoordinatesOnGrid" type="checkbox">show coordinates on grid</label>
          <label><input id="showSelectedObjectLabel" type="checkbox">show selected object label</label>
          <label><input id="showGridTrace" type="checkbox">show raw grid trace</label>
          <label><input id="showInactiveTraces" type="checkbox">show inactive traces</label>
          <label><input id="showPreviousLevelTraces" type="checkbox">show previous level traces</label>
        </div>
        <div class="objects" id="objects"></div>
      </fieldset>
      <label>Frame <span id="frameText"></span>
        <span class="slider-line"><button id="play" type="button" title="Play">▶</button><button id="previousFrame" class="step" type="button" title="Previous frame">◀</button><input id="frame" type="range"><button id="nextFrame" class="step" type="button" title="Next frame">▶</button></span>
      </label>
      <div class="frame-overview" id="frameOverview" aria-label="Frame overview"></div>
      <div class="toolbar">
        <button id="prevLevel" type="button">Previous level</button>
        <button id="nextLevel" type="button">Next level</button>
        <button id="prevDiff" type="button">Previous diff</button>
        <button id="nextDiff" type="button">Next diff</button>
      </div>
      <div class="timeline" id="timeline" aria-label="Trace timeline"></div>
      <div class="summary">
        <div class="metric"><strong id="objectCount">0</strong>objects</div>
        <div class="metric"><strong id="eventCount">0</strong>events</div>
        <div class="metric"><strong id="diffCount">0</strong>diff frames</div>
        <div class="metric"><strong id="unmatchedCount">0</strong><span id="unmatchedLabel">unmatched records</span></div>
      </div>
      <dl id="details"></dl>
      <p class="legend">Grid: physical Phoenix screen-space (208x256). Solid path: physical bird draw position, including background scroll. Dashed path: raw bird bytes. V = physical draw position; A = unscrolled screen-RAM anchor; G = raw bird bytes. Both retain the full history with a brighter recent trail.</p>
    </section>
  </div>
</main>
<script>
"use strict";
const payload = {data};
const dumps = payload.dumps;
const samples = dumps[0].samples;
const compareSamples = dumps[1].samples;
const frames = dumps[0].frames;
const frameMetadataByFrame = new Map(dumps[0].metadata.map(item => [item.frame, item]));
const canvas = document.getElementById("field");
const ctx = canvas.getContext("2d");
const playerSelect = document.getElementById("player");
const frameInput = document.getElementById("frame");
const frameText = document.getElementById("frameText");
const frameOverview = document.getElementById("frameOverview");
const details = document.getElementById("details");
const playButton = document.getElementById("play");
const previousFrameButton = document.getElementById("previousFrame");
const nextFrameButton = document.getElementById("nextFrame");
const prevLevelButton = document.getElementById("prevLevel");
const nextLevelButton = document.getElementById("nextLevel");
const prevDiffButton = document.getElementById("prevDiff");
const nextDiffButton = document.getElementById("nextDiff");
const timeline = document.getElementById("timeline");
const objects = document.getElementById("objects");
const slotData = document.getElementById("slotData");
const allObjects = document.getElementById("allObjects");
const showCoordinatesOnGrid = document.getElementById("showCoordinatesOnGrid");
const showGridTrace = document.getElementById("showGridTrace");
const showInactiveTraces = document.getElementById("showInactiveTraces");
const showPreviousLevelTraces = document.getElementById("showPreviousLevelTraces");
const objectCount = document.getElementById("objectCount");
const eventCount = document.getElementById("eventCount");
const diffCount = document.getElementById("diffCount");
const unmatchedCount = document.getElementById("unmatchedCount");
const unmatchedLabel = document.getElementById("unmatchedLabel");
let playing = false;
let timer = null;
let playbackLastTime = 0;
let stepDelayTimer = null;
let stepRepeatTimer = null;
const playbackFrameMs = 1000 / 60;
const trailLength = 90;
const fieldWidth = {FIELD_WIDTH};
const fieldHeight = {FIELD_HEIGHT};
const canvasWidth = canvas.width;
const canvasHeight = canvas.height;
const sampleKey = sample => sample.player + ":" + sample.kind + ":" + sample.id;
const samplesByKey = new Map();
for (const sample of samples) {{
  const key = sampleKey(sample);
  if (!samplesByKey.has(key)) samplesByKey.set(key, []);
  samplesByKey.get(key).push(sample);
}}
function slotColor(key) {{
  const [, kind, id] = key.split(":");
  if (kind === "player_ship") return "#ffcf4a";
  const offset = kind === "alien" ? 0 : kind === "bird" ? 53 : 106;
  return "hsl(" + ((Number(id) * 137 + offset) % 360) + " 72% 62%)";
}}
function isProjectileKey(key) {{
  const [, kind] = key.split(":");
  return ["player_bullet", "above_player_bullet", "enemy_bullet"].includes(kind);
}}
const sampleByFrameKey = new Map(samples.map(sample => [sample.frame + "|" + sampleKey(sample), sample]));
const frameIndex = new Map(frames.map((frame, index) => [frame, index]));
const compareByRecordKey = new Map(compareSamples.map(sample => [sample.record_index + "|" + sampleKey(sample), sample]));
const unmatchedReferenceRecords = Math.max(0, frames.length - dumps[1].frames.length);
const unmatchedPortRecords = Math.max(0, dumps[1].frames.length - frames.length);
const levelSegments = [];
for (let index = 0; index < dumps[0].metadata.length; index++) {{
  const metadata = dumps[0].metadata[index];
  const levelKey = metadata.level_and_round;
  const previous = levelSegments[levelSegments.length - 1];
  if (!previous || previous.levelKey !== levelKey) {{
    levelSegments.push({{ levelKey, startIndex: index, endIndex: index }});
  }} else {{
    previous.endIndex = index;
  }}
}}
const levelSegmentByFrameIndex = new Map();
for (const segment of levelSegments) {{
  for (let index = segment.startIndex; index <= segment.endIndex; index++) {{
    levelSegmentByFrameIndex.set(index, segment);
  }}
}}
const keys = [...new Set(samples.map(sampleKey))].sort((a, b) => a.localeCompare(b, undefined, {{ numeric: true }}));
let selectedKey = keys[0] || "";
let hasExplicitSelection = false;
let visibleKeys = new Set(keys);
let hoveredKey = "";

function normalizedFields(sample) {{
  if (!sample) return null;
  return ["active", "state", "shape", "type", "phase", "x", "y", "screen_addr", "movement_pattern", "timer", "flags"]
    .map(key => [key, sample[key] == null ? null : sample[key]]);
}}
function levelDescription(level) {{
  return [
    "alien fade-in", "aliens active", "alien fade-in", "aliens active",
    "bird spiral fill", "birds active", "bird spiral fill", "birds active",
    "mothership spiral fill", "mothership fade-in", "mothership + aliens fade-in",
    "mothership escort aliens"
  ][level] || "unused";
}}
function gameStateDescription(gameState) {{
  return [
    "new game", "score flashing", "initialize level", "normal gameplay",
    "player exploding", "game over", "mothership exploding", "mothership score"
  ][gameState] || "unknown";
}}
function differs(sample, other) {{
  if (!payload.compare) return false;
  const left = normalizedFields(sample);
  const right = normalizedFields(other);
  if (!left || !right) return true;
  return left.some(([key, value], index) => key !== right[index][0] || value !== right[index][1]);
}}
function compareSample(sample) {{
  return sample ? compareByRecordKey.get(sample.record_index + "|" + sampleKey(sample)) : null;
}}
function isUnmatchedReferenceSample(sample) {{
  return payload.compare && sample && sample.record_index >= dumps[1].frames.length;
}}
function isDiff(sample, other = compareSample(sample)) {{
  return !isUnmatchedReferenceSample(sample) && differs(sample, other);
}}
const diffFrames = new Set();
const eventFrames = new Set();
for (const key of keys) {{
  let previous = null;
  for (const sample of samples.filter(item => sampleKey(item) === key)) {{
    const other = compareSample(sample);
    if (isDiff(sample, other)) diffFrames.add(sample.frame);
    if (previous && differs(sample, previous)) eventFrames.add(sample.frame);
    previous = sample;
  }}
}}

function options(select, values) {{
  select.replaceChildren(...values.map(value => {{
    const option = document.createElement("option");
    option.value = value; option.textContent = value; return option;
  }}));
}}
function sampleAtFrame(key, frame) {{
  return sampleByFrameKey.get(frame + "|" + key) || null;
}}
function isBirdLayer(frame) {{
  return Boolean(frameMetadataByFrame.get(frame)?.scroll);
}}
function displayKind(sample, frame) {{
  if (sample?.kind === "alien" && isBirdLayer(frame)) return "bird-wave";
  return sample?.kind || "object";
}}
function displaySlotLabel(sample, frame) {{
  if (!sample) return "no record";
  if (sample.kind === "player_ship") return "player ship slot " + sample.id;
  return displayKind(sample, frame) + " slot " + sample.id;
}}
function playerObjectKeys() {{
  return keys.filter(key => key.startsWith(playerSelect.value + ":"));
}}
function syncAllObjects() {{
  const objectKeys = playerObjectKeys();
  const visibleCount = objectKeys.filter(key => visibleKeys.has(key)).length;
  allObjects.checked = visibleCount === objectKeys.length;
  allObjects.indeterminate = visibleCount > 0 && visibleCount < objectKeys.length;
}}
function updateObjects() {{
  const objectKeys = keys.filter(key => key.startsWith(playerSelect.value + ":"));
  visibleKeys = new Set(objectKeys);
  selectedKey = objectKeys[0] || "";
  hasExplicitSelection = false;
  render();
}}
function setPlaying(next) {{
  playing = next; playButton.textContent = playing ? "❚❚" : "▶";
  if (timer !== null) {{ cancelAnimationFrame(timer); timer = null; }}
  if (playing) {{
    playbackLastTime = performance.now();
    timer = requestAnimationFrame(playTick);
  }}
}}
function playTick(now) {{
  if (!playing) return;
  if (now - playbackLastTime >= playbackFrameMs) {{
    frameInput.value = (Number(frameInput.value) + 1) % frames.length;
    playbackLastTime = now;
    render();
  }}
  timer = requestAnimationFrame(playTick);
}}
function setFrame(frame) {{
  const index = frameIndex.get(frame);
  if (index != null) {{ frameInput.value = index; render(); }}
}}
function moveFrame(direction) {{
  setPlaying(false);
  frameInput.value = (Number(frameInput.value) + direction + frames.length) % frames.length;
  render();
}}
function stopStepping() {{
  if (stepDelayTimer) {{ clearTimeout(stepDelayTimer); stepDelayTimer = null; }}
  if (stepRepeatTimer) {{ clearInterval(stepRepeatTimer); stepRepeatTimer = null; }}
}}
function startStepping(direction) {{
  stopStepping();
  moveFrame(direction);
  stepDelayTimer = setTimeout(() => {{
    stepRepeatTimer = setInterval(() => moveFrame(direction), 120);
  }}, 300);
}}
function bindStepButton(button, direction) {{
  button.addEventListener("pointerdown", event => {{
    event.preventDefault();
    button.setPointerCapture(event.pointerId);
    startStepping(direction);
  }});
  ["pointerup", "pointercancel", "lostpointercapture"].forEach(eventName =>
    button.addEventListener(eventName, stopStepping)
  );
}}
function jumpDiff(direction) {{
  const current = frames[Number(frameInput.value)] || 0;
  const ordered = [...diffFrames].sort((a, b) => a - b);
  const next = direction > 0
    ? ordered.find(frame => frame > current) || ordered[0]
    : ordered.slice().reverse().find(frame => frame < current) || ordered[ordered.length - 1];
  if (next != null) setFrame(next);
}}
function jumpLevel(direction) {{
  const currentIndex = Number(frameInput.value);
  if (!levelSegments.length) return;
  const next = direction > 0
    ? levelSegments.find(segment => segment.startIndex > currentIndex) || levelSegments[0]
    : [...levelSegments].reverse().find(segment => segment.startIndex < currentIndex) || levelSegments[levelSegments.length - 1];
  frameInput.value = next.startIndex;
  render();
}}
function drawGrid() {{
  ctx.fillStyle = "#071116"; ctx.fillRect(0, 0, canvasWidth, canvasHeight);
  ctx.strokeStyle = "#1d3741"; ctx.lineWidth = 1;
  for (let raw = 0; raw <= fieldWidth; raw += 32) {{
    const px = raw / (fieldWidth - 1) * (canvasWidth - 1) + .5;
    ctx.beginPath(); ctx.moveTo(px, 0); ctx.lineTo(px, canvasHeight); ctx.stroke();
  }}
  for (let raw = 0; raw <= fieldHeight; raw += 32) {{
    const py = raw / (fieldHeight - 1) * (canvasHeight - 1) + .5;
    ctx.beginPath(); ctx.moveTo(0, py); ctx.lineTo(canvasWidth, py); ctx.stroke();
  }}
}}
function coordinateX(value) {{ return Math.min(fieldWidth - 1, Number(value)) / (fieldWidth - 1) * (canvasWidth - 1); }}
function coordinateY(value) {{ return Math.min(fieldHeight - 1, Number(value)) / (fieldHeight - 1) * (canvasHeight - 1); }}
function drawPoint(sample, color, radius, outline) {{
  if (!sample || !sample.active || sample.visual_x == null || sample.visual_y == null) return;
  const x = coordinateX(sample.visual_x);
  const y = coordinateY(sample.visual_y);
  ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.fill();
  if (outline) {{ ctx.strokeStyle = outline; ctx.lineWidth = 2; ctx.stroke(); }}
}}
function drawOffPulse(sample) {{
  if (!sample || sample.visual_x == null || sample.visual_y == null) return;
  const x = coordinateX(sample.visual_x);
  const y = coordinateY(sample.visual_y);
  for (const [radius, alpha] of [[22, 0.22], [15, 0.48], [8, 0.92]]) {{
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = "#ff4f3d";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2); ctx.stroke();
  }}
  ctx.globalAlpha = 1;
  ctx.fillStyle = "#ff4f3d";
  ctx.beginPath(); ctx.arc(x, y, 3, 0, Math.PI * 2); ctx.fill();
}}
function drawCanvasLabel(label, x, y, color) {{
  ctx.font = "14px ui-monospace, SFMono-Regular, Menlo, monospace";
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#071116";
  ctx.strokeText(label, x, y);
  ctx.fillStyle = color;
  ctx.fillText(label, x, y);
}}
function drawHoverLabel(sample, color) {{
  if (!sample || !sample.active || sample.visual_x == null || sample.visual_y == null) return;
  const x = coordinateX(sample.visual_x);
  const y = coordinateY(sample.visual_y);
  let label = "#" + displayKind(sample, sample.frame) + "-" + sample.id + " V(" + sample.visual_x + ", " + sample.visual_y + ")";
  if (sample.kind === "bird") label += " A(" + sample.screen_x + ", " + sample.screen_y + ") G(" + sample.x + ", " + sample.y + ")";
  drawCanvasLabel(label, x + 9, y - 9, color);
}}
function drawCoordinatesOnGrid(sample, color) {{
  if (!showCoordinatesOnGrid.checked || !sample || !sample.active) return;
  if (sample.visual_x != null && sample.visual_y != null) {{
    drawCanvasLabel("V(" + sample.visual_x + "," + sample.visual_y + ")", coordinateX(sample.visual_x) + 8, coordinateY(sample.visual_y) + 16, color);
  }}
  if (showGridTrace.checked && sample.kind === "bird" && sample.x != null && sample.y != null) {{
    drawCanvasLabel("G(" + sample.x + "," + sample.y + ")", coordinateX(sample.x) + 8, coordinateY(sample.y) - 8, color);
  }}
}}
function drawTrail(points, color, selected) {{
  if (points.length < 2) return;
  ctx.globalAlpha = selected ? 0.32 : 0.20;
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  ctx.beginPath();
  points.forEach((point, index) => {{
    const x = coordinateX(point.visual_x);
    const y = coordinateY(point.visual_y);
    index ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }});
  ctx.stroke();

  const trail = points.slice(-trailLength);
  for (let index = 1; index < trail.length; index++) {{
    const fade = index / (trail.length - 1);
    ctx.globalAlpha = (0.25 + 0.72 * fade * fade) * (selected ? 1 : 0.65);
    ctx.strokeStyle = color;
    ctx.lineWidth = selected ? 1 + 2 * fade : 1;
    ctx.beginPath();
    ctx.moveTo(coordinateX(trail[index - 1].visual_x), coordinateY(trail[index - 1].visual_y));
    ctx.lineTo(coordinateX(trail[index].visual_x), coordinateY(trail[index].visual_y));
    ctx.stroke();
  }}
  ctx.globalAlpha = 1;
}}
function drawGridTrail(points, color, selected) {{
  if (!showGridTrace.checked || points[0]?.kind !== "bird") return;
  const gridPoints = points.filter(point => point.x != null && point.y != null);
  if (gridPoints.length < 2) return;
  ctx.setLineDash([5, 4]);
  ctx.globalAlpha = selected ? 0.42 : 0.28;
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  ctx.beginPath();
  gridPoints.forEach((point, index) => {{
    const x = coordinateX(point.x);
    const y = coordinateY(point.y);
    index ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  }});
  ctx.stroke();

  const trail = gridPoints.slice(-trailLength);
  for (let index = 1; index < trail.length; index++) {{
    const fade = index / (trail.length - 1);
    ctx.globalAlpha = (0.30 + 0.60 * fade * fade) * (selected ? 1 : 0.7);
    ctx.lineWidth = selected ? 1 + fade : 1;
    ctx.beginPath();
    ctx.moveTo(coordinateX(trail[index - 1].x), coordinateY(trail[index - 1].y));
    ctx.lineTo(coordinateX(trail[index].x), coordinateY(trail[index].y));
    ctx.stroke();
  }}
  ctx.setLineDash([]);
  ctx.globalAlpha = 1;
}}
function updateHoveredObject(event) {{
  const bounds = canvas.getBoundingClientRect();
  const x = (event.clientX - bounds.left) / bounds.width * canvasWidth;
  const y = (event.clientY - bounds.top) / bounds.height * canvasHeight;
  const frame = frames[Number(frameInput.value)] || 0;
  let nearest = null;
  let nearestDistance = 18;
  for (const key of visibleKeys) {{
    const sample = latestAtOrBefore(key, frame);
    if (!sample || !sample.active || sample.visual_x == null || sample.visual_y == null) continue;
    const distance = Math.hypot(coordinateX(sample.visual_x) - x, coordinateY(sample.visual_y) - y);
    if (distance <= nearestDistance) {{
      nearest = sample;
      nearestDistance = distance;
    }}
  }}
  const nextKey = nearest ? sampleKey(nearest) : "";
  if (nextKey !== hoveredKey) {{
    hoveredKey = nextKey;
    render();
  }}
}}
function latestAtOrBefore(key, frame, sourceSamples = samples) {{
  const keySamples = sourceSamples === samples ? samplesByKey.get(key) || [] : sourceSamples;
  let low = 0;
  let high = keySamples.length - 1;
  let latest = null;
  while (low <= high) {{
    const middle = Math.floor((low + high) / 2);
    if (keySamples[middle].frame <= frame) {{
      latest = keySamples[middle];
      low = middle + 1;
    }} else {{
      high = middle - 1;
    }}
  }}
  return latest;
}}
function offTransition(key, frame) {{
  const keySamples = samplesByKey.get(key) || [];
  let low = 0;
  let high = keySamples.length - 1;
  let index = -1;
  while (low <= high) {{
    const middle = Math.floor((low + high) / 2);
    if (keySamples[middle].frame <= frame) {{ index = middle; low = middle + 1; }}
    else {{ high = middle - 1; }}
  }}
  const current = keySamples[index];
  const previous = keySamples[index - 1];
  if (!current || current.frame !== frame || current.active || !previous?.active) return null;
  return current.kind === "alien" || current.kind === "bird" ? previous : null;
}}
function formatHex(value, width = 2) {{
  return value == null ? "" : "$" + Number(value).toString(16).toUpperCase().padStart(width, "0");
}}
function renderTimeline(frame) {{
  const maxTicks = Math.min(frames.length, 180);
  const step = Math.max(1, Math.ceil(frames.length / maxTicks));
  const children = [];
  for (let i = 0; i < frames.length; i += step) {{
    const chunk = frames.slice(i, i + step);
    const node = document.createElement("button");
    node.type = "button";
    node.className = "tick";
    if (chunk.some(value => eventFrames.has(value))) node.classList.add("event");
    if (chunk.some(value => diffFrames.has(value))) node.classList.add("diff");
    if (chunk.includes(frame)) node.classList.add("current");
    node.title = String(chunk[0]);
    node.addEventListener("click", () => {{ frameInput.value = i; render(); }});
    children.push(node);
  }}
  timeline.replaceChildren(...children);
}}
function renderObjects(frame) {{
  const rows = playerObjectKeys().map(key => {{
    const sample = latestAtOrBefore(key, frame);
    const other = compareSample(sample);
    const row = document.createElement("div");
    row.className = "object-row";
    row.setAttribute("role", "button");
    row.tabIndex = 0;
    row.setAttribute("aria-pressed", String(key === selectedKey));
    row.dataset.slotKey = key;
    row.style.setProperty("--slot-color", slotColor(key));
    if (key === selectedKey) row.classList.add("active");
    if (key === hoveredKey) row.classList.add("hovered");
    if (isDiff(sample, other)) row.classList.add("diff");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = visibleKeys.has(key);
    checkbox.title = "Toggle object visibility";
    checkbox.addEventListener("click", event => event.stopPropagation());
    checkbox.addEventListener("change", () => {{
      if (checkbox.checked) visibleKeys.add(key);
      else visibleKeys.delete(key);
      syncAllObjects();
      render();
    }});
    const swatch = document.createElement("span");
    swatch.className = "object-swatch";
    const label = document.createElement("span");
    label.textContent = displaySlotLabel(sample, frame);
    const state = document.createElement("span");
    state.textContent = sample?.active ? "active" : "off";
    row.append(checkbox, swatch, label, state);
    bindSlotSelection(row, key);
    return row;
  }});
  objects.replaceChildren(...rows);
}}
function selectSlot(key) {{
  setPlaying(false);
  selectedKey = key;
  hasExplicitSelection = true;
  render();
}}
function bindSlotSelection(element, key) {{
  element.addEventListener("click", () => selectSlot(key));
  element.addEventListener("keydown", event => {{
    if (event.key === "Enter" || event.key === " ") {{
      event.preventDefault();
      selectSlot(key);
    }}
  }});
}}
function slotFields(sample, frame) {{
  if (!sample) return [["state", "no record"]];
  if (sample.kind === "bird") {{
    const base = 0x4B70 + sample.id * 8;
    return [
      [formatHex(base, 4), "shape index: " + formatHex(sample.state) + " (" + sample.type + ")"],
      [formatHex(base + 1, 4) + "-" + formatHex(base + 2, 4), "draw screen anchor: " + formatHex(sample.screen_addr, 4)],
      [formatHex(base + 3, 4), "shape-table offset: " + formatHex(sample.vertical_offset)],
      [formatHex(base + 4, 4), "behaviour timer: " + formatHex(sample.timer)],
      [formatHex(base + 5, 4), "grid X: " + formatHex(sample.x)],
      [formatHex(base + 6, 4), "movement phase: " + formatHex(sample.movement_pattern)],
      [formatHex(base + 7, 4), "grid Y: " + formatHex(sample.y)],
    ];
  }}
  if (sample.kind === "player_ship") {{
    return [
      ["$43C0", "control state: " + formatHex(sample.state)],
      ["$43C1", "shape index: " + formatHex(sample.shape)],
      ["$43C2", "ship X: " + formatHex(sample.x)],
      ["$43C3", "ship Y: " + formatHex(sample.y)],
      ["$43E2-$43E3", "draw screen anchor: " + formatHex(sample.screen_addr, 4)],
    ];
  }}
  if (displayKind(sample, frame) === "bird-wave") {{
    return [
      ["role", "bird-wave object in the physical $4B70 wing-slot region"],
      ["state", formatHex(sample.state)], ["shape", formatHex(sample.shape)],
      ["X/Y", formatHex(sample.x) + ", " + formatHex(sample.y)],
      ["screen", formatHex(sample.screen_addr, 4)],
    ];
  }}
  return [
    ["state", formatHex(sample.state)], ["shape", formatHex(sample.shape)],
    ["X/Y", formatHex(sample.x) + ", " + formatHex(sample.y)],
    ["screen", formatHex(sample.screen_addr, 4)],
  ];
}}
function renderSlotData(frame) {{
  const cards = playerObjectKeys().map(key => {{
    const sample = latestAtOrBefore(key, frame);
    const card = document.createElement("article");
    card.className = "slot-card";
    card.setAttribute("role", "button");
    card.tabIndex = 0;
    card.setAttribute("aria-pressed", String(key === selectedKey));
    card.dataset.slotKey = key;
    card.style.setProperty("--slot-color", slotColor(key));
    if (key === selectedKey) card.classList.add("selected");
    const heading = document.createElement("h3");
    heading.textContent = "#" + displaySlotLabel(sample, frame).replace(" slot ", "-");
    const definitions = document.createElement("dl");
    for (const [address, meaning] of slotFields(sample, frame)) {{
      const term = document.createElement("dt"); term.textContent = address;
      const definition = document.createElement("dd"); definition.textContent = meaning;
      definitions.append(term, definition);
    }}
    card.append(heading, definitions);
    bindSlotSelection(card, key);
    return card;
  }});
  slotData.replaceChildren(...cards);
}}
function htmlEscape(value) {{
  return String(value).replace(/[&<>"']/g, char => ({{"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}}[char]));
}}
function render() {{
  const selectedFrameIndex = Number(frameInput.value);
  const frame = frames[selectedFrameIndex] || 0;
  const levelSegment = levelSegmentByFrameIndex.get(selectedFrameIndex);
  const traceStartIndex = showPreviousLevelTraces.checked || !levelSegment ? 0 : levelSegment.startIndex;
  const visibleObjectKeys = playerObjectKeys().filter(key => visibleKeys.has(key));
  const current = latestAtOrBefore(selectedKey, frame);
  const frameMetadata = frameMetadataByFrame.get(frame) || current;
  frameText.textContent = frame ? "$" + frame.toString(16).toUpperCase().padStart(4, "0") + " (" + frame + ")" : "no samples";
  const level = frameMetadata ? frameMetadata.level_and_round & 0x0F : null;
  const round = frameMetadata ? frameMetadata.level_and_round >> 4 : null;
  frameOverview.replaceChildren(...(frameMetadata ? [
    ["level", level + " - " + levelDescription(level)],
    ["round", round + " - completed mothership cycles"],
    ["game state", formatHex(frameMetadata.game_state) + " - " + gameStateDescription(frameMetadata.game_state)],
    ["scroll", formatHex(frameMetadata.scroll) + (isBirdLayer(frame) ? " (bird layer active)" : " (bird layer inactive)")],
  ] : []).map(([label, value]) => {{
    const item = document.createElement("span");
    item.textContent = label + ": ";
    const strong = document.createElement("strong"); strong.textContent = value;
    item.append(strong);
    return item;
  }}));
  drawGrid();
  visibleObjectKeys.forEach(key => {{
    const color = slotColor(key);
    const emphasized = key === selectedKey || key === hoveredKey;
    const sampleNow = sampleAtFrame(key, frame);
    const deathPosition = offTransition(key, frame);
    if (!showInactiveTraces.checked && (!sampleNow || !sampleNow.active)) {{
      if (deathPosition) drawOffPulse(deathPosition);
      return;
    }}
    const keySamples = samplesByKey.get(key) || [];
    const points = keySamples.filter(point => point.active && point.visual_x != null && point.visual_y != null && point.record_index >= traceStartIndex && point.record_index <= selectedFrameIndex);
    const gridPoints = keySamples.filter(point => point.active && point.record_index >= traceStartIndex && point.record_index <= selectedFrameIndex);
    // Projectile paths are visually noisy and do not represent persistent
    // game objects. Show their current position only; retain fading trails
    // for ships, aliens, birds, and other structural objects.
    if (!isProjectileKey(key)) {{
      drawTrail(points, color, emphasized);
      drawGridTrail(gridPoints, color, emphasized);
    }}
    const latest = latestAtOrBefore(key, frame);
    const other = compareSample(latest);
    const outline = isDiff(latest, other) ? "#ff4f3d" : key === hoveredKey ? "#ffcf4a" : key === selectedKey ? "#ffffff" : null;
    drawPoint(latest, color, emphasized ? 7 : 4, outline);
    if (other && isDiff(latest, other)) drawPoint(other, "#ff4f3d", 4, "#ffffff");
    if (deathPosition) drawOffPulse(deathPosition);
    drawCoordinatesOnGrid(latest, color);
    if (key === hoveredKey || (!hoveredKey && showSelectedObjectLabel.checked && hasExplicitSelection && key === selectedKey)) drawHoverLabel(latest, color);
  }});
  if (current) selectedKey = sampleKey(current);
  const other = compareSample(current);
  const diffRows = current && other && isDiff(current, other) ? normalizedFields(current).filter(([key, value], index) => value !== normalizedFields(other)[index][1]) : [];
  const fields = current ? [
    ["dump", payload.labels[0]], ["level", (current.level_and_round & 0x0F) + " - " + levelDescription(current.level_and_round & 0x0F) + " (round " + (current.level_and_round >> 4) + ", " + formatHex(current.level_and_round) + ")"],
    ["game state", formatHex(current.game_state) + " - " + gameStateDescription(current.game_state)], ["object", displayKind(current, frame)], ["active", current.active], ["x", current.x], ["y", current.y],
    ["V physical position", current.visual_x + "," + current.visual_y], ["A draw-anchor", current.screen_x + "," + current.screen_y], ["type", current.type],
    ["state", formatHex(current.state)], ["shape", formatHex(current.shape)], ["phase", current.phase],
    ["screen", formatHex(current.screen_addr, 4)], ["source", current.source],
    ["diffs", diffRows.length ? diffRows.map(([key]) => key).join(", ") : null]
  ] : [["state", "No record for this player/slot at this frame"]];
  if (other) {{
    fields.push(["compare dump", payload.labels[1]]);
    fields.push(["compare screen", formatHex(other.screen_addr, 4)]);
    fields.push(["compare x/y", [other.x, other.y].filter(value => value != null).join(",")]);
  }}
  details.replaceChildren(...fields.filter(([, value]) => value != null).flatMap(([key, value]) => {{
    const term = document.createElement("dt"); term.textContent = key;
    const definition = document.createElement("dd"); definition.textContent = value;
    return [term, definition];
  }}));
  objectCount.textContent = keys.length;
  eventCount.textContent = eventFrames.size;
  diffCount.textContent = diffFrames.size;
  unmatchedCount.textContent = unmatchedReferenceRecords + unmatchedPortRecords;
  unmatchedLabel.textContent = unmatchedReferenceRecords
    ? payload.labels[0] + " tail records"
    : unmatchedPortRecords ? payload.labels[1] + " tail records" : "unmatched records";
  prevDiffButton.disabled = diffFrames.size === 0;
  nextDiffButton.disabled = diffFrames.size === 0;
  prevLevelButton.disabled = levelSegments.length < 2;
  nextLevelButton.disabled = levelSegments.length < 2;
  renderTimeline(frame);
  renderObjects(frame);
  renderSlotData(frame);
  syncAllObjects();
}}
if (!samples.length) {{ document.querySelector("main").innerHTML = "<h1>No samples</h1><p>The selected player has no records in this dump.</p>"; }}
else {{
  options(playerSelect, [...new Set(samples.map(sample => sample.player))]);
  frameInput.min = 0; frameInput.max = Math.max(0, frames.length - 1); frameInput.value = 0;
  playerSelect.addEventListener("change", updateObjects);
  allObjects.addEventListener("change", () => {{
    const objectKeys = playerObjectKeys();
    if (allObjects.checked) objectKeys.forEach(key => visibleKeys.add(key));
    else objectKeys.forEach(key => visibleKeys.delete(key));
    render();
  }});
  showCoordinatesOnGrid.addEventListener("change", render);
  showGridTrace.addEventListener("change", render);
  showInactiveTraces.addEventListener("change", render);
  showPreviousLevelTraces.addEventListener("change", render);
  objects.addEventListener("pointerdown", () => setPlaying(false));
  slotData.addEventListener("pointerdown", () => setPlaying(false));
  canvas.addEventListener("mousemove", updateHoveredObject);
  canvas.addEventListener("mouseleave", () => {{
    if (hoveredKey) {{ hoveredKey = ""; render(); }}
  }});
  frameInput.addEventListener("input", () => {{ setPlaying(false); render(); }});
  playButton.addEventListener("click", () => setPlaying(!playing));
  bindStepButton(previousFrameButton, -1);
  bindStepButton(nextFrameButton, 1);
  prevLevelButton.addEventListener("click", () => jumpLevel(-1));
  nextLevelButton.addEventListener("click", () => jumpLevel(1));
  prevDiffButton.addEventListener("click", () => jumpDiff(-1));
  nextDiffButton.addEventListener("click", () => jumpDiff(1));
  updateObjects();
}}
</script>
</body>
</html>
"""


def main():
    args = parse_args()
    title = args.title or f"Phoenix {args.kind} path"
    kinds = selected_kinds(args.kind, args.include_kind)
    try:
        frames, samples, frame_metadata = snapshots_for_dump(
            args.ram_dump, kinds, args.player
        )
        compare_frames = []
        compare_samples = []
        compare_metadata = []
        if args.compare:
            compare_frames, compare_samples, compare_metadata = snapshots_for_dump(
                args.compare, kinds, args.player
            )
        pathlib.Path(args.output).write_text(
            html_document(
                title, args.kind, frames, samples, frame_metadata, compare_frames,
                compare_samples, compare_metadata, (args.reference_label, args.port_label),
            ),
            encoding="utf-8",
        )
    except (OSError, ValueError) as error:
        print(f"view_sprite_trace.py: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
