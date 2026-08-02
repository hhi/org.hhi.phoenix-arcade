#!/usr/bin/env python3
"""Generate sprite-sequence SVGs from the decoded character set and colour table.

Everything drawn here comes from two tracked, generated sources:

  * ``phoenix_render_assets.h`` - the 256 foreground and 256 background 8x8
    characters plus the 128-entry RGB palette, decoded from the graphics ROM
    and the colour PROMs by ``generate_classic_render_assets.py``.
  * ``phoenix_tables.c``        - the program-ROM tables that say which
    characters make up which sprite, and in what order they animate.

No pixel or composition in the output is hand-authored. Rendering follows
``platform_sdl.c`` exactly, including the palette index derivation

    prom_index = (bank << 6) | (0x20 if foreground) | (colour << 3) | (tile >> 5)

and the 90-degree display rotation ``(tx, ty) -> (7 - ty, 7 - tx)``.

Usage:  python3 tools/generate_sprite_sheets.py [--outdir DIR]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

ASSETS_H = PROJECT / "phoenix_render_assets.h"
TABLES_C = PROJECT / "phoenix_tables.c"


# ── reading the generated sources ──────────────────────────────────────────

def read_palette(text: str) -> list[tuple[int, int, int]]:
    body = text[text.index("phoenix_palette_rgb"):]
    body = body[body.index("{") + 1:]
    out: list[tuple[int, int, int]] = []
    for m in re.finditer(r"\{\s*(\d+),\s*(\d+),\s*(\d+)\s*\}", body):
        out.append((int(m[1]), int(m[2]), int(m[3])))
        if len(out) == 128:
            break
    if len(out) != 128:
        raise SystemExit("palette: expected 128 entries, got %d" % len(out))
    return out


def read_tiles(text: str, name: str) -> list[list[int]]:
    body = text[text.index(name):]
    body = body[body.index("= {") + 3:]
    tiles: list[list[int]] = []
    depth, cur = 0, ""
    for ch in body:
        if ch == "{":
            depth += 1
            cur = ""
        elif ch == "}":
            if depth == 1:
                tiles.append([int(v) for v in re.findall(r"\d+", cur)])
                if len(tiles) == 256:
                    break
            depth -= 1
        elif depth == 1:
            cur += ch
    if len(tiles) != 256 or any(len(t) != 64 for t in tiles):
        raise SystemExit("%s: unexpected shape" % name)
    return tiles


def read_table(text: str, name: str) -> list[int]:
    """Read one initialiser by name.

    Anchored on the declaration itself - `name[...] = { ... };` - because the
    same identifier also appears in the doc comments above other tables, and a
    plain search would silently return the wrong array.
    """
    m = re.search(r"\b" + re.escape(name) + r"\s*\[[^\]]*\]\s*=\s*\{(.*?)\};",
                  text, re.S)
    if not m:
        raise SystemExit(f"table {name} not found in phoenix_tables.c")
    return [int(v, 0) for v in re.findall(r"0x[0-9A-Fa-f]+|\b\d+\b", m.group(1))]


# ── reading sprites out of a recorded session ──────────────────────────────

DUMP_GZ = (PROJECT / "context" / "traces" / "two_player_last_grown_bird_compare"
           / "c-last-grown-bird.bin.gz")

RECORD = 3076          # 4-byte big-endian frame number + RAM $4000-$4BFF
ALIEN_LO, ALIEN_HI = 0x60, 0xBF     # the three alien colour groups


def _read_dump(path):
    """Read a RAM dump, gzipped or not."""
    import gzip
    data = open(path, "rb").read()
    return gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data


def scan_recording_sprites(path, *, step=7, max_side=3, min_seen=3,
                           lo=ALIEN_LO, hi=ALIEN_HI, base=0x000):
    """Find the sprites the game actually drew, by clustering screen memory.

    Some objects have no fixed size in any table: sprite_rendering.c chooses
    1x1, 2x1, 1x2 or 2x2 at runtime from the object's control byte. The only
    honest way to know what is drawn is to look at what ended up in the
    foreground screen RAM of a real session.

    Returns {(cols, rows): [(character codes in column-major order), ...]},
    ordered by how often each variant was observed.
    """
    import gzip
    from collections import Counter, defaultdict

    raw = _read_dump(path)
    total = len(raw) // RECORD
    seen_counts = Counter()

    for i in range(200, total, step):
        mem = raw[i * RECORD + 4:(i + 1) * RECORD]
        cells = {}
        for off in range(0x400):        # base 0x000 = foreground, 0x800 = background
            code = mem[base + off]
            if lo <= code <= hi:
                gx, gy = off // 32, off % 32
                if gx < 26:                         # columns 26-31 are off-screen
                    cells[(gx, gy)] = code
        visited = set()
        for start in cells:
            if start in visited:
                continue
            stack, comp = [start], []
            while stack:
                p = stack.pop()
                if p in visited or p not in cells:
                    continue
                visited.add(p)
                comp.append(p)
                x, y = p
                stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            xs = [p[0] for p in comp]
            ys = [p[1] for p in comp]
            x0, y0 = min(xs), min(ys)
            w, h = max(xs) - x0 + 1, max(ys) - y0 + 1
            if w > max_side or h > max_side or len(comp) != w * h:
                continue        # ragged clusters are two sprites touching
            # column-major, and screen x runs opposite to the memory column
            frame = tuple(cells[(x0 + (w - 1 - c), y0 + r)]
                          for c in range(w) for r in range(h))
            seen_counts[(w, h, frame)] += 1

    out = defaultdict(list)
    for (w, h, frame), n in seen_counts.most_common():
        if n >= min_seen:
            out[(w, h)].append(frame)
    return out


def _frame_at(path, i):
    """The small foreground sprites present in one recorded frame."""
    import gzip
    global _RAW
    try:
        raw = _RAW
    except NameError:
        raw = _RAW = _read_dump(path)
    mem = raw[i * RECORD + 4:(i + 1) * RECORD]
    cells = {}
    for off in range(0x400):
        code = mem[off]
        if ALIEN_LO <= code <= ALIEN_HI:
            gx, gy = off // 32, off % 32
            if gx < 26:
                cells[(gx, gy)] = code
    visited, out = set(), []
    for start in cells:
        if start in visited:
            continue
        stack, comp = [start], []
        while stack:
            p = stack.pop()
            if p in visited or p not in cells:
                continue
            visited.add(p)
            comp.append(p)
            x, y = p
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        xs = [p[0] for p in comp]
        ys = [p[1] for p in comp]
        x0, y0 = min(xs), min(ys)
        w, h = max(xs) - x0 + 1, max(ys) - y0 + 1
        if w > 2 or h > 2 or len(comp) != w * h:
            continue
        frame = tuple(cells[(x0 + (w - 1 - c), y0 + r)]
                      for c in range(w) for r in range(h))
        out.append((25 - x0 - w + 1, y0, w, h, frame))
    return out


def find_best_dive(path, length=90, reach=3, step=25, limit=6000):
    """Search the recording for a dive instead of trusting a fixed start frame.

    An earlier version took a hard-coded start frame, tuned to one particular
    dump. Pointed at a different recording it silently produced nothing, so the
    sheet just disappeared from the output. Scanning is slower but always
    returns the best dive the recording actually contains.
    """
    total = len(_read_dump(path)) // RECORD
    best, best_len = [], 0
    for start in range(400, min(total - length, limit), step):
        poses = track_one_dive(path, start, length=length, reach=reach)
        sizes = {(len(p[2]), p[0], p[1]) for p in poses}
        if len(poses) > best_len and len({(p[0], p[1]) for p in poses}) >= 2:
            best, best_len = poses, len(poses)
    return best


def track_one_dive(path, first, length=90, reach=3):
    """Follow single objects frame by frame and return the best dive seen.

    Grouping poses by block size says what shapes exist, but not the order the
    game shows them in. Following one object through consecutive frames does:
    the poses come out in the sequence the dive actually plays.
    """
    chains = [[s] for s in _frame_at(path, first)]
    for f in range(first + 1, first + length):
        cur = _frame_at(path, f)
        used = set()
        for ch in chains:
            lx, ly = ch[-1][0], ch[-1][1]
            near = [(abs(c[0] - lx) + abs(c[1] - ly), k)
                    for k, c in enumerate(cur) if k not in used]
            near = [c for c in near if c[0] <= reach]
            if near:
                _, k = min(near)
                used.add(k)
                ch.append(cur[k])
    best, score = None, 0
    for ch in chains:
        drop = ch[-1][1] - ch[0][1]
        sizes = {(s[2], s[3]) for s in ch}
        if len(ch) >= 60 and drop >= 8 and len(sizes) >= 2 and drop * len(sizes) > score:
            best, score = ch, drop * len(sizes)
    if best is None:
        return []
    poses, last = [], None
    for s in best:
        key = (s[2], s[3], s[4])
        if key != last:
            poses.append(key)
            last = key
    return poses


def pad_into_2x2(w, h, frame):
    """Place a 1x1 / 2x1 / 1x2 / 2x2 sprite into a common 2x2 cell."""
    grid = {}
    for c in range(w):
        for r in range(h):
            grid[(c, r)] = frame[c * h + r]
    return tuple(grid.get((c, r), 0) for c in range(2) for r in range(2))


# ── rendering one 8x8 character ────────────────────────────────────────────

def tile_rects(tiles, index: int, *, foreground: bool, bank: int = 0):
    """Yield (x, y, '#rrggbb') for every non-transparent pixel, already rotated."""
    for ty in range(8):
        for tx in range(8):
            colour = tiles[index][ty * 8 + tx]
            if colour == 0:            # colour 0 is transparent, always
                continue
            prom = ((bank & 1) << 6) | (0x20 if foreground else 0) \
                   | (colour << 3) | ((index >> 5) & 0x07)
            yield 7 - ty, 7 - tx, prom & 0x7F


def svg_tile(tiles, index, palette, *, foreground, px, ox=0, oy=0, bank=0):
    """Emit one rect per vertical run of identical colour, not per pixel."""
    grid = {(x, y): prom for x, y, prom
            in tile_rects(tiles, index, foreground=foreground, bank=bank)}
    out = []
    for x in range(8):
        y = 0
        while y < 8:
            prom = grid.get((x, y))
            if prom is None:
                y += 1
                continue
            run = 1
            while y + run < 8 and grid.get((x, y + run)) == prom:
                run += 1
            r, g, b = palette[prom]
            out.append(
                f'<rect x="{ox + x * px}" y="{oy + y * px}" width="{px}" '
                f'height="{px * run}" fill="#{r:02x}{g:02x}{b:02x}"/>'
            )
            y += run
    return "".join(out)


HEAD = (
    '<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
    'xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{alt}">\n'
    "<title>{title}</title>\n<style>\n"
    "  .bg{{fill:#050510}} .cell{{fill:#0C0C1E;stroke:#242440;stroke-width:1}}\n"
    "  .h1{{fill:#E8E8FF;font-family:'Segoe UI',system-ui,sans-serif;font-size:17px;font-weight:600}}\n"
    "  .sub{{fill:#8888AA;font-family:'Segoe UI',system-ui,sans-serif;font-size:11.5px}}\n"
    "  .idx{{fill:#FFFF66;font-family:monospace;font-size:9.5px}}\n"
    "  .lbl{{fill:#AAAACC;font-family:'Segoe UI',system-ui,sans-serif;font-size:10.5px}}\n"
    "  .note{{fill:#777799;font-family:'Segoe UI',system-ui,sans-serif;font-size:11px}}\n"
    "  .grp{{fill:#66DDFF;font-family:monospace;font-size:10.5px}}\n"
    "  .src{{fill:#C9A24A;font-family:monospace;font-size:10px}}\n"
    "</style>\n"
)


def xesc(s):
    """Escape text that ends up inside SVG markup."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def wrap(w, h, title, alt, body):
    return HEAD.format(w=w, h=h, title=title, alt=alt) + \
        f'<rect class="bg" x="0" y="0" width="{w}" height="{h}" rx="8"/>\n' + \
        body + "\n</svg>\n"


# ── sheet 1: the character set, grouped by colour group ────────────────────

def sheet_character_set(tiles, palette, *, foreground, strings):
    px, cols = 3, 32
    cw, ch = 8 * px + 10, 8 * px + 16
    x0, y0 = 20, 78
    w = x0 * 2 + cols * cw
    rows = 256 // cols
    h = y0 + rows * ch + 78
    b = [f'<text class="h1" x="20" y="30">{strings["title"]}</text>',
         f'<text class="sub" x="20" y="50">{strings["sub1"]}</text>',
         f'<text class="sub" x="20" y="66">{strings["sub2"]}</text>']
    for i in range(256):
        cx = x0 + (i % cols) * cw
        cy = y0 + (i // cols) * ch
        if i % 32 == 0:
            b.append(f'<text class="grp" x="{x0 - 4}" y="{cy - 3}">'
                     f'{strings["group"]} {i >> 5} · {i:02X}–{i + 31:02X}</text>')
        b.append(f'<rect class="cell" x="{cx}" y="{cy}" width="{8*px+6}" height="{8*px+6}" rx="2"/>')
        b.append(svg_tile(tiles, i, palette, foreground=foreground,
                          px=px, ox=cx + 3, oy=cy + 3))
    ny = y0 + rows * ch + 22
    for k, line in enumerate(strings["notes"]):
        b.append(f'<text class="note" x="20" y="{ny + k * 17}">{line}</text>')
    return wrap(w, h, strings["title"], strings["alt"], "\n".join(b))


# ── sheet 2: an animation sequence with its tile decomposition ─────────────

def sheet_sequence(tiles, palette, *, foreground, frames, layout, strings):
    """frames: list of tuples of tile indices. layout: (cols, rows) of each frame."""
    px = 4
    fcols, frows = layout
    fw, fh = fcols * 8 * px, frows * 8 * px
    gap = 18
    src_line = strings.get("source")
    x0, y0 = 20, (108 if src_line else 92)
    # the sheet must also be wide enough for its longest line of prose
    longest = max([strings["sub1"], strings["sub2"], *strings["notes"]]
                  + ([src_line] if src_line else []), key=len)
    w = max(560, x0 * 2 + len(frames) * (fw + gap), int(len(longest) * 6.1) + 40)
    h = y0 + fh + 30 + frows * 14 + 76
    b = [f'<text class="h1" x="20" y="30">{strings["title"]}</text>',
         f'<text class="sub" x="20" y="50">{strings["sub1"]}</text>',
         f'<text class="sub" x="20" y="66">{strings["sub2"]}</text>',
         f'<text class="grp" x="20" y="84">{strings["routine"]}</text>']
    if src_line:
        b.append(f'<text class="src" x="20" y="100">{xesc(src_line)}</text>')
    for fi, frame in enumerate(frames):
        fx = x0 + fi * (fw + gap)
        b.append(f'<rect class="cell" x="{fx-3}" y="{y0-3}" width="{fw+6}" height="{fh+6}" rx="3"/>')
        for k, t in enumerate(frame):
            ox = fx + (k // frows) * 8 * px
            oy = y0 + (k % frows) * 8 * px
            b.append(svg_tile(tiles, t, palette, foreground=foreground,
                              px=px, ox=ox, oy=oy))
        # decomposition: which character code sits where
        ty = y0 + fh + 22
        b.append(f'<text class="lbl" x="{fx}" y="{ty}">#{fi}</text>')
        for k, t in enumerate(frame):
            col, row = k // frows, k % frows
            b.append(f'<text class="idx" x="{fx + col * 8 * px}" '
                     f'y="{ty + 14 + row * 13}">{t:02X}</text>')
    ny = y0 + fh + 30 + frows * 14 + 24
    for k, line in enumerate(strings["notes"]):
        b.append(f'<text class="note" x="20" y="{ny + k * 17}">{line}</text>')
    return wrap(w, h, strings["title"], strings["alt"], "\n".join(b))


# ── sheet 3: the sequence actually playing ─────────────────────────────────

def sheet_animation(tiles, palette, *, foreground, frames, layout, ms_per_frame, strings):
    """One SVG that plays the whole sequence as an animation.

    The pace is given per frame, not per loop: a sixteen-frame sequence should
    not run twice as fast as an eight-frame one just because both were given
    the same total duration.

    Frame i is shown for one Nth of the loop. Frame 0 stays visible when
    animation is unavailable, so a static renderer still shows something real.
    """
    seconds = round(len(frames) * ms_per_frame / 1000, 2)
    px = 10
    fcols, frows = layout
    fw, fh = fcols * 8 * px, frows * 8 * px
    src_line = strings.get("source")
    x0, y0 = 24, (90 if src_line else 74)
    longest = max([strings["sub1"], *strings["notes"]], key=len)
    w = max(320, x0 * 2 + fw, int(len(longest) * 6.1) + 40)
    h = y0 + fh + 30 + 17 * len(strings["notes"]) + 16
    n = len(frames)

    css = []
    for i in range(n):
        a, b = 100.0 * i / n, 100.0 * (i + 1) / n
        # visible for its own slice of the loop, hidden otherwise
        if i == 0:
            css.append(f"@keyframes fr{i}{{0%{{opacity:1}}{b - 0.01:.2f}%{{opacity:1}}"
                       f"{b:.2f}%{{opacity:0}}100%{{opacity:0}}}}")
        else:
            css.append(f"@keyframes fr{i}{{0%{{opacity:0}}{a - 0.01:.2f}%{{opacity:0}}"
                       f"{a:.2f}%{{opacity:1}}{b - 0.01:.2f}%{{opacity:1}}"
                       f"{b:.2f}%{{opacity:0}}100%{{opacity:0}}}}")
        css.append(f".f{i}{{animation:fr{i} {seconds}s infinite steps(1);"
                   + ("" if i == 0 else "opacity:0;") + "}")
    css.append("@media (prefers-reduced-motion: reduce){"
               + ",".join(f".f{i}" for i in range(n))
               + "{animation:none}"
               + ",".join(f".f{i}" for i in range(1, n)) + "{opacity:0}}")

    b = [f'<text class="h1" x="24" y="30">{strings["title"]}</text>',
         f'<text class="sub" x="24" y="50">{strings["sub1"]}</text>',
         f'<text class="grp" x="24" y="66">{strings["routine"]}</text>']
    if src_line:
        b.append(f'<text class="src" x="24" y="82">{xesc(src_line)}</text>')
    b += [
         f'<rect class="cell" x="{x0-4}" y="{y0-4}" width="{fw+8}" height="{fh+8}" rx="4"/>']
    for fi, frame in enumerate(frames):
        parts = []
        for k, t in enumerate(frame):
            ox = x0 + (k // frows) * 8 * px
            oy = y0 + (k % frows) * 8 * px
            parts.append(svg_tile(tiles, t, palette, foreground=foreground,
                                  px=px, ox=ox, oy=oy))
        b.append(f'<g class="f{fi}">' + "".join(parts) + "</g>")
    ny = y0 + fh + 28
    for k, line in enumerate(strings["notes"]):
        b.append(f'<text class="note" x="24" y="{ny + k * 17}">{line}</text>')

    head = HEAD.format(w=w, h=h, title=strings["title"], alt=strings["alt"])
    head = head.replace("</style>", "\n  " + "\n  ".join(css) + "\n</style>")
    return head + f'<rect class="bg" x="0" y="0" width="{w}" height="{h}" rx="8"/>\n' \
                + "\n".join(b) + "\n</svg>\n"


# ── main ───────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", type=Path, default=PROJECT / "animations" / "sprites")
    ap.add_argument("--dump", type=Path, default=DUMP_GZ,
                    help="RAM dump to read runtime sprites from (.bin or .bin.gz). "
                         "The committed default is the last-grown-bird session, which "
                         "contains no mothership. For the mothership and the shield, "
                         "produce the bird-investigation dump first:\n"
                         "  make -C c-phoenix tracerun "
                         "COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt "
                         "COMPARE_FRAMES=13935 COMPARE_NAME=bird-investigation "
                         "COMPARE_STOP_AFTER=999999\n"
                         "then re-run with --dump /tmp/port_bird-investigation.bin")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    assets = ASSETS_H.read_text()
    tables = TABLES_C.read_text()
    palette = read_palette(assets)
    fg = read_tiles(assets, "phoenix_foreground_tiles")
    bg = read_tiles(assets, "phoenix_background_tiles")

    blocks = read_table(tables, "phoenix_sprite_character_block_shapes")
    alien = read_table(tables, "phoenix_alien_wave_animation_shapes")
    boom = read_table(tables, "phoenix_alien_explosion_frames")
    nx2 = read_table(tables, "phoenix_shield_and_drawnx2_shapes")

    # drawNx2 (attract_mode.c) walks a shape table two characters at a time -
    # one column pair - and then steps to the next column. alien_logic.c turns
    # an explosion frame byte into an address with 0x1700 | img, which indexes
    # phoenix_shield_and_drawnx2_shapes at addr - 0x17B8.
    NX2_BASE = 0x17B8

    def draw_nx2(addr: int, n: int) -> tuple[int, ...]:
        start = addr - NX2_BASE
        if not (0 <= start <= len(nx2) - 2 * n):
            raise SystemExit(f"drawNx2: address {addr:#06x} outside the shape table")
        return tuple(nx2[start:start + 2 * n])

    # -- birds ---------------------------------------------------------------
    # attract_mode.c:drawbirdobject resolves a bird in three steps:
    #   entry  = phoenix_bird_draw_entries[type]      -> width, via
    #            rows = 7 - ((entry - 0x20) >> 3)     (draw_bird_shape_350c)
    #   a      = ((type << 3) + frame) & 0x7E         -> pointer slot
    #   shape  = big-endian pointer at that slot      -> character data
    # The pointer stride between a type's frames equals 2 * rows exactly,
    # which independently confirms the width formula.
    bird_entries = read_table(tables, "phoenix_bird_draw_entries")
    bird_ptrs = read_table(tables, "phoenix_bird_shape_pointers")
    bird_page = read_table(tables, "phoenix_bird_shape_data_page")
    BIRD_PAGE_BASE = 0x3C00

    def bird_byte(addr: int) -> int:
        if addr >= BIRD_PAGE_BASE:
            return bird_page[addr - BIRD_PAGE_BASE]
        return nx2[addr - NX2_BASE]

    def bird_width(bird_type: int) -> int:
        return 7 - ((bird_entries[bird_type] - 0x20) >> 3)

    def bird_frame(bird_type: int, frame: int) -> tuple[int, ...]:
        cols = bird_width(bird_type)
        a = (((bird_type << 3) | (bird_type >> 5)) + frame) & 0x7E
        shape = (bird_ptrs[a] << 8) | bird_ptrs[a + 1]
        return tuple(bird_byte(shape + i) for i in range(2 * cols))

    def bird_frames(bird_type: int) -> list[tuple[int, ...]]:
        return [bird_frame(bird_type, f) for f in (0, 2, 4, 6)]

    def pad_to(frame: tuple[int, ...], cols: int, width: int) -> tuple[int, ...]:
        """Centre a narrower sprite inside a wider frame using blank characters."""
        lead = ((width - cols) // 2) * 2
        tail = (width - cols) * 2 - lead
        return (0,) * lead + frame + (0,) * tail

    written = []
    anim_extra = []

    def emit(name, text):
        p = args.outdir / name
        p.write_text(text)
        written.append(p)

    # -- character set, both banks, both languages ---------------------------
    cs = {
        "en": dict(
            title="The Phoenix character set and its colour table",
            sub1="Every sprite in the game is built from these 8x8 characters. Nothing is drawn freely.",
            sub2="A character's own index picks its colours: bits 5-7 select one of eight colour groups in the PROM table.",
            group="group",
            alt="All 256 characters of the Phoenix character set, arranged in eight colour groups of 32.",
            notes=[
                "That is why each block of 32 looks like one family: letters, digits, the player ship, the birds, explosions, the shield.",
                "Colour 0 in a character is always transparent; colours 1-3 index into the group's palette entries.",
                "Generated from phoenix_render_assets.h by tools/generate_sprite_sheets.py - do not edit by hand.",
            ]),
        "nl": dict(
            title="De Phoenix-karakterset en de bijbehorende kleurtabel",
            sub1="Elke sprite in het spel is opgebouwd uit deze 8x8-karakters. Er wordt niets vrij getekend.",
            sub2="Het karakternummer bepaalt zelf de kleur: bit 5-7 kiezen een van de acht kleurgroepen in de PROM-tabel.",
            group="groep",
            alt="Alle 256 karakters van de Phoenix-karakterset, in acht kleurgroepen van 32.",
            notes=[
                "Daarom lijkt elk blok van 32 op een familie: letters, cijfers, het spelerschip, de vogels, explosies, het schild.",
                "Kleur 0 in een karakter is altijd transparant; kleur 1-3 verwijzen naar de paletregels van de groep.",
                "Gegenereerd uit phoenix_render_assets.h door tools/generate_sprite_sheets.py - niet met de hand aanpassen.",
            ]),
    }
    for lang, s in cs.items():
        suffix = "" if lang == "en" else ".nl"
        emit(f"character-set-foreground{suffix}.svg",
             sheet_character_set(fg, palette, foreground=True, strings=s))
        s2 = dict(s)
        if lang == "en":
            s2["title"] = "The background character set"
            s2["sub1"] = ("Stars, planets, the mothership and the aliens live in a second, "
                          "independent set of 256 characters.")
            s2["alt"] = ("All 256 characters of the Phoenix background set, arranged in "
                         "eight colour groups of 32.")
            s2["notes"] = [
                "Here the families are the starfield, the planet, the aliens and the mothership hull - drawn behind everything the foreground set draws.",
                "Background characters skip the 0x20 foreground bit in the palette index, which is why the same colour numbers give different colours.",
                "Generated from phoenix_render_assets.h by tools/generate_sprite_sheets.py - do not edit by hand.",
            ]
        else:
            s2["title"] = "De achtergrond-karakterset"
            s2["sub1"] = ("Sterren, planeten, het moederschip en de aliens zitten in een tweede, "
                          "onafhankelijke set van 256 karakters.")
            s2["alt"] = ("Alle 256 karakters van de Phoenix-achtergrondset, in acht "
                         "kleurgroepen van 32.")
            s2["notes"] = [
                "Hier zijn de families het sterrenveld, de planeet, de aliens en de romp van het moederschip - getekend achter alles wat de voorgrondset tekent.",
                "Achtergrondkarakters slaan de 0x20-voorgrondbit in de paletindex over; daarom geven dezelfde kleurnummers hier andere kleuren.",
                "Gegenereerd uit phoenix_render_assets.h door tools/generate_sprite_sheets.py - niet met de hand aanpassen.",
            ]
        emit(f"character-set-background{suffix}.svg",
             sheet_character_set(bg, palette, foreground=False, strings=s2))

    # -- player ship: Draw2x2, four characters per pose ----------------------
    ship_frames = [tuple(blocks[4 * i:4 * i + 4]) for i in range(8)]
    ship = {
        "en": dict(
            title="The player ship, pose by pose",
            sub1="Eight poses. Each is four characters from phoenix_sprite_character_block_shapes, drawn as a 2x2 block.",
            sub2="The codes are read two at a time: each pair fills one column top to bottom, then the routine steps to the next column.",
            routine="drawn by the 2x2 routine · 4 characters · 16 x 16 pixels",
            source="sprite_rendering.c: execute_bit3_function() case 4 reads phoenix_sprite_character_block_shapes[b]",
            alt="The eight poses of the Phoenix player ship, each composed of four 8x8 characters in a 2x2 block, with the character codes listed.",
            notes=[
                "The game never draws a ship. It writes character codes into screen memory and the hardware fetches the pixels.",
                "Block size is chosen at runtime from the object's control byte, not stored in the table; 2x2 is the size these four entries render coherently as.",
                "All four come from colour groups 1 and 2, which is why the ship is always red, white and yellow.",
            ]),
        "nl": dict(
            title="Het spelerschip, pose voor pose",
            sub1="Acht poses. Elk vier karakters uit phoenix_sprite_character_block_shapes, getekend als een 2x2-blok.",
            sub2="De codes worden per twee gelezen: elk paar vult een kolom van boven naar beneden, daarna stapt de routine naar de volgende kolom.",
            routine="getekend door de 2x2-routine · 4 karakters · 16 x 16 pixels",
            source="sprite_rendering.c: execute_bit3_function() case 4 leest phoenix_sprite_character_block_shapes[b]",
            alt="De acht poses van het Phoenix-spelerschip, elk opgebouwd uit vier 8x8-karakters in een 2x2-blok, met de karaktercodes erbij.",
            notes=[
                "Het spel tekent nooit een schip. Het schrijft karaktercodes naar het schermgeheugen en de hardware haalt de pixels op.",
                "De blokgrootte kiest het spel tijdens runtime uit het control-byte, hij staat niet in de tabel; 2x2 is de maat waarin deze vier regels samenhangend renderen.",
                "Alle vier komen uit kleurgroep 1 en 2, en daarom is het schip altijd rood, wit en geel.",
            ]),
    }
    for lang, s in ship.items():
        suffix = "" if lang == "en" else ".nl"
        emit(f"sequence-player-ship{suffix}.svg",
             sheet_sequence(fg, palette, foreground=True,
                            frames=ship_frames, layout=(2, 2), strings=s))

    # -- mothership pilot/antenna: 8 frames of 4 rows x 2 columns ------------
    # phoenix_tables.h documents this as the mothership pilot/antenna frames
    # for alien_wave.c's mothership_animation, drawn by
    # draw_image_c_by_b(src, ..., 4, 2) - eight 8-byte blocks, not 2x2 sprites.
    pilot_frames = [tuple(alien[8 * i:8 * i + 8]) for i in range(8)]

    # -- formation aliens: the block-shape quads that follow the ship --------
    # Quads 0-7 are the player ship. The entries after it are the formation
    # aliens; which quad is on screen at a given moment is chosen by the
    # animation descriptor table at 0x16A0, which is not traced here.
    alien_frames = [tuple(blocks[4 * q:4 * q + 4]) for q in range(8, 20)]
    # -- formation alien: taken from a recorded session, not from a table ----
    # The block size is chosen at runtime from the object's control byte
    # (sprite_rendering.c: control & 0x07 -> 1x1 / 2x1 / 1x2 / 2x2), so the
    # shape table alone cannot tell us what the game draws. These pairs were
    # read out of the foreground screen RAM of the committed recording
    # context/traces/two_player_last_grown_bird_compare/c-last-grown-bird.bin.gz
    # by clustering adjacent non-zero characters across the session. The four
    # 2x1 pairs below are the recurring formation-alien poses; the same scan
    # also produced the 3x2 explosion blocks generated further down, which is
    # an independent check on this method.
    dump = args.dump
    alien_by_size = scan_recording_sprites(dump)
    alien_single = tuple(f[0] for f in alien_by_size.get((1, 1), [])[:6])

    ALIEN_SHEETS = (
        ("level", (2, 1), 6,
         ("flying level", "in horizontale vlucht"),
         ("This is the pose you see while the formation drifts left and right.",
          "Dit is de pose die je ziet terwijl de formatie heen en weer schuift.")),
        ("climb", (1, 2), 6,
         ("climbing", "klimmend"),
         ("One character wide and two tall: the alien seen head-on as it pulls up.",
          "Een karakter breed en twee hoog: de alien recht van voren terwijl hij optrekt.")),
        ("dive", (2, 2), 8,
         ("diving and banking", "duikend en zwenkend"),
         ("The widest of its poses, used while it breaks formation and dives at you.",
          "De breedste van zijn poses, gebruikt terwijl hij uit de formatie breekt en op je duikt.")),
    )
    for tag, size, count, names, blurb in ALIEN_SHEETS:
        frames = alien_by_size.get(size, [])[:count]
        if not frames:
            continue
        cols, rows = size
        s = {
            "en": dict(
                title=f"The formation alien, {names[0]}",
                sub1=f"{len(frames)} poses of {cols}x{rows} characters, read out of the screen memory of a recorded session.",
                sub2="No table holds this size: sprite_rendering.c picks 1x1, 2x1, 1x2 or 2x2 at runtime from the object's control byte.",
                routine=f"{cols}x{rows} block · {cols * rows} characters · foreground set",
                source="sprite_rendering.c: bit3_controller() calls execute_bit3_function(control & 0x07), which picks the size",
                alt=f"Poses of the Phoenix formation alien {names[0]}, each {cols} by {rows} characters, with the character codes listed.",
                notes=[blurb[0],
                       "One alien uses all these sizes as it moves, which is why no single sheet can show the whole creature."]),
            "nl": dict(
                title=f"De formatie-alien, {names[1]}",
                sub1=f"{len(frames)} poses van {cols}x{rows} karakters, afgelezen uit het schermgeheugen van een opgenomen sessie.",
                sub2="Geen tabel bevat deze maat: sprite_rendering.c kiest tijdens runtime 1x1, 2x1, 1x2 of 2x2 uit het control-byte van het object.",
                routine=f"{cols}x{rows}-blok · {cols * rows} karakters · voorgrondset",
                source="sprite_rendering.c: bit3_controller() roept execute_bit3_function(control & 0x07) aan, die de maat kiest",
                alt=f"Poses van de Phoenix-formatie-alien {names[1]}, elk {cols} bij {rows} karakters, met de karaktercodes erbij.",
                notes=[blurb[1],
                       "Eén alien gebruikt al deze maten terwijl hij beweegt; daarom kan geen enkel vel het hele beest tonen."]),
        }
        for lang, ss in s.items():
            suffix = "" if lang == "en" else ".nl"
            emit(f"sequence-alien-{tag}{suffix}.svg",
                 sheet_sequence(fg, palette, foreground=True,
                                frames=frames, layout=size, strings=ss))
        anim_extra.append((f"alien-{tag}", size, frames, names))

    # -- one alien through one dive, in the order it happened ---------------
    dive_poses = find_best_dive(dump)[:12]
    if not dive_poses:
        print("note: no usable dive found in this recording - dive-order sheet skipped")
    if dive_poses:
        dive_frames = [pad_into_2x2(w, h, f) for w, h, f in dive_poses]
        sizes = " → ".join(f"{w}x{h}" for w, h, _ in dive_poses)
        dv = {
            "en": dict(
                title="One alien, one dive, in order",
                sub1="The same object followed frame by frame as it leaves the formation and drops on the player.",
                sub2=f"Its block size changes mid-dive: {sizes}. Narrower poses are padded into a 2x2 cell here so they line up.",
                routine="tracked through a recorded session · sizes change per pose",
                source="sprite_rendering.c: execute_bit3_function() handles cases 0/1/3/4 — 1x1, 2x1, 1x2, 2x2",
                alt="One Phoenix alien followed through a dive, showing its pose and block size changing in sequence.",
                notes=[
                    "Grouping poses by size tells you what shapes exist; following one object tells you the order the game shows them in.",
                    "The object was matched between frames by proximity, over 84 frames of the recording as it fell fourteen rows.",
                ]),
            "nl": dict(
                title="Eén alien, één duik, op volgorde",
                sub1="Hetzelfde object frame voor frame gevolgd terwijl het de formatie verlaat en op de speler duikt.",
                sub2=f"De blokgrootte wisselt tijdens de duik: {sizes}. Smallere poses zijn hier in een 2x2-cel gezet zodat ze uitlijnen.",
                routine="gevolgd door een opgenomen sessie · maten wisselen per pose",
                source="sprite_rendering.c: execute_bit3_function() kent de gevallen 0/1/3/4 — 1x1, 2x1, 1x2, 2x2",
                alt="Eén Phoenix-alien gevolgd door een duik, met wisselende pose en blokgrootte op volgorde.",
                notes=[
                    "Poses groeperen op maat zegt welke vormen bestaan; één object volgen zegt in welke volgorde het spel ze toont.",
                    "Het object is tussen frames gekoppeld op nabijheid, over 84 frames van de opname waarin het veertien rijen zakte.",
                ]),
        }
        for lang, ss in dv.items():
            suffix = "" if lang == "en" else ".nl"
            emit(f"sequence-alien-dive-order{suffix}.svg",
                 sheet_sequence(fg, palette, foreground=True,
                                frames=dive_frames, layout=(2, 2), strings=ss))
            ss2 = dict(ss); ss2["notes"] = ss["notes"][:1]
            emit(f"animation-alien-dive-order{suffix}.svg",
                 sheet_animation(fg, palette, foreground=True, frames=dive_frames,
                                 layout=(2, 2), ms_per_frame=400, strings=ss2))

    # -- shield and mothership, if the recording reaches those states --------
    # Both only exist in a recording that actually gets that far. Rather than
    # assume, ask the dump: scan the wider colour range and emit a sheet only
    # for the block sizes that really turn up.
    for tag, lo, hi, base, tiles_, is_fg, names, blurb in (
        ("shield", 0xE0, 0xFF, 0x000, fg, True,
         ("The player shield", "Het spelerschild"),
         ("Only appears while a shield is on screen.",
          "Verschijnt alleen zolang er een schild op het scherm staat.")),
        # No mothership entry. Scanning background RAM by colour group alone
        # cannot tell a mothership hull from a grown bird - both live in the
        # same upper groups, and on the last-grown-bird recording this scan
        # produced birds labelled as a hull, twice. Identifying the object
        # needs its RAM slot, not its colours; use the visual tracer for that.
    ):
        found = scan_recording_sprites(dump, step=11, max_side=4, min_seen=3,
                                       lo=lo, hi=hi, base=base)
        # the largest block size that actually occurred, so nothing is invented
        sizes = [s for s in found if s[0] * s[1] >= 4]
        if not sizes:
            print(f"note: no multi-character {tag} in this recording - sheet skipped")
            continue
        size = max(sizes, key=lambda s: (s[0] * s[1], len(found[s])))
        frames = found[size][:8]
        cols, rows = size
        st = {
            "en": dict(
                title=f"{names[0]}, as drawn in the recording",
                sub1=f"{len(frames)} blocks of {cols}x{rows} characters, clustered out of the recorded screen memory.",
                sub2="Read from a session rather than a table, because the block size is decided at runtime.",
                routine=f"{cols}x{rows} block · {cols * rows} characters · "
                        + ("foreground" if is_fg else "background") + " set",
                source=("player_logic.c: move_player() calls draw_shields() (b=4, c=4) — "
                        "shapes from phoenix_shield_table") if tag == "shield" else
                       ("scan of " + Path(dump).name + " — see scan_recording_sprites()"),
                alt=f"{names[0]} as drawn in a recorded Phoenix session, with the character codes listed.",
                notes=[blurb[0],
                       "Only what this recording contains; a session reaching further into the game may show more."]),
            "nl": dict(
                title=f"{names[1]}, zoals getekend in de opname",
                sub1=f"{len(frames)} blokken van {cols}x{rows} karakters, geclusterd uit het opgenomen schermgeheugen.",
                sub2="Afgelezen uit een sessie in plaats van een tabel, omdat de blokgrootte tijdens runtime wordt bepaald.",
                routine=f"{cols}x{rows}-blok · {cols * rows} karakters · "
                        + ("voorgrond" if is_fg else "achtergrond") + "set",
                source=("player_logic.c: move_player() roept draw_shields() aan (b=4, c=4) — "
                        "vormen uit phoenix_shield_table") if tag == "shield" else
                       ("scan van " + Path(dump).name + " — zie scan_recording_sprites()"),
                alt=f"{names[1]} zoals getekend in een opgenomen Phoenix-sessie, met de karaktercodes erbij.",
                notes=[blurb[1],
                       "Alleen wat deze opname bevat; een sessie die verder in het spel komt laat mogelijk meer zien."]),
        }
        for lang, ss in st.items():
            suffix = "" if lang == "en" else ".nl"
            emit(f"sequence-{tag}{suffix}.svg",
                 sheet_sequence(tiles_, palette, foreground=is_fg,
                                frames=frames, layout=size, strings=ss))

    # The default recording has no shield or mothership sheet.  A recording
    # supplied with --dump may contain a shield, which the scan above emits.
    # Scanning the background RAM for large blocks turned up 4x2 clusters that
    # render as birds, not as a hull: this session is the "last grown bird"
    # scenario and appears to contain no mothership at all. The shield only
    # ever appeared as single characters E0, E1 and E2, never as a block.
    # Both would need a recording that actually reaches those game states.
    # (The bird blocks found this way do match the bird sheets generated from
    # the tables above, which is a useful cross-check on both.)

    # NOTE: the shape table alone is not enough.
    # phoenix_sprite_character_block_shapes is indexed by an object's control
    # byte, and sprite_rendering.c's bit3 dispatcher picks 1x1, 2x1, 1x2 or
    # 2x2 from (control & 0x07) at runtime. The table is therefore not a list
    # of fixed-size sprites, and reading it as uniform quads produces poses
    # the game never draws. Rendering the aliens correctly needs the control
    # bytes from a real session, not the table alone.

    # -- mothership pilot / antenna -----------------------------------------
    pl = {
        "en": dict(
            title="The mothership's pilot, frame by frame",
            sub1="Eight frames from phoenix_alien_wave_animation_shapes, eight characters each.",
            sub2="Drawn by draw_image_c_by_b with four rows and two columns - a taller block than anything else here.",
            routine="draw_image_c_by_b · 4 rows x 2 columns · 8 characters · background set",
            source="alien_wave.c calls draw_image_c_by_b(src, 0x49A6, 4, 2), src = 0x1B00 | a",
            alt="The eight animation frames of the Phoenix mothership pilot and antenna, each eight background characters in a 2x4 block.",
            notes=[
                "This table is easy to mistake for an alien animation; phoenix_tables.h identifies it as the mothership pilot and antenna.",
                "The frame is picked from the animation counter, which is why the eight blocks are evenly spaced eight bytes apart.",
            ]),
        "nl": dict(
            title="De piloot van het moederschip, frame voor frame",
            sub1="Acht frames uit phoenix_alien_wave_animation_shapes, elk acht karakters.",
            sub2="Getekend door draw_image_c_by_b met vier rijen en twee kolommen - een hoger blok dan al het andere hier.",
            routine="draw_image_c_by_b · 4 rijen x 2 kolommen · 8 karakters · achtergrondset",
            source="alien_wave.c roept draw_image_c_by_b(src, 0x49A6, 4, 2) aan, src = 0x1B00 | a",
            alt="De acht animatieframes van de piloot en antenne van het Phoenix-moederschip, elk acht achtergrondkarakters in een 2x4-blok.",
            notes=[
                "Deze tabel is makkelijk aan te zien voor een alien-animatie; phoenix_tables.h benoemt hem als de piloot en antenne van het moederschip.",
                "Het frame komt uit de animatieteller, en daarom liggen de acht blokken netjes acht bytes uit elkaar.",
            ]),
    }
    for lang, s in pl.items():
        suffix = "" if lang == "en" else ".nl"
        emit(f"sequence-mothership-pilot{suffix}.svg",
             sheet_sequence(bg, palette, foreground=False,
                            frames=pilot_frames, layout=(2, 4), strings=s))

    # -- explosion: Draw3x2, reached through an address indirection ----------
    # alien_logic.c: img = phoenix_alien_explosion_frames[offset];
    #                drawNx2(0x1700 | img, screen, 0xFFDF, 3);
    # so the table holds addresses, not character codes.
    boom_frames = [draw_nx2(0x1700 | img, 3) for img in boom]
    bo = {
        "en": dict(
            title="An explosion, frame by frame",
            sub1="Eight frames from phoenix_alien_explosion_frames. Those bytes are not characters - they are addresses.",
            sub2="alien_logic.c turns each byte into 0x1700 | byte and hands it to the 3x2 routine, which reads six characters from there.",
            routine="drawNx2 with n=3 · 6 characters · 24 x 16 pixels",
            source="alien_logic.c calls attract_mode.c: drawNx2(0x1700 | img, de, 0xFFDF, 3)",
            alt="The eight explosion frames of Phoenix, each a 3x2 block of six characters resolved through an address table, with the character codes listed.",
            notes=[
                "Frame 0 resolves to six zero bytes: that is the erase step, not a missing frame. Then one spark, then debris, then the full burst.",
                "The last frames alternate between two full bursts, which is the flicker you see on screen.",
                "The characters all come from colour group 6, the red explosion family.",
            ]),
        "nl": dict(
            title="Een explosie, frame voor frame",
            sub1="Acht frames uit phoenix_alien_explosion_frames. Die bytes zijn geen karakters - het zijn adressen.",
            sub2="alien_logic.c maakt er 0x1700 | byte van en geeft dat aan de 3x2-routine, die daar zes karakters ophaalt.",
            routine="drawNx2 met n=3 · 6 karakters · 24 x 16 pixels",
            source="alien_logic.c roept attract_mode.c: drawNx2(0x1700 | img, de, 0xFFDF, 3) aan",
            alt="De acht explosieframes van Phoenix, elk een 3x2-blok van zes karakters via een adrestabel, met de karaktercodes erbij.",
            notes=[
                "Frame 0 wijst naar zes nulbytes: dat is de wisstap, geen ontbrekend frame. Daarna een vonk, dan puin, dan de volle explosie.",
                "De laatste frames wisselen tussen twee volle explosies; dat is het flikkeren dat je op het scherm ziet.",
                "De karakters komen allemaal uit kleurgroep 6, de rode explosiefamilie.",
            ]),
    }
    for lang, s in bo.items():
        suffix = "" if lang == "en" else ".nl"
        emit(f"sequence-explosion{suffix}.svg",
             sheet_sequence(fg, palette, foreground=True,
                            frames=boom_frames, layout=(3, 2), strings=s))

    # -- bonus explosion: two fixed halves, also Draw3x2 ---------------------
    bonus_frames = [draw_nx2(0x17D0, 3), draw_nx2(0x17D6, 3)]
    bn = {
        "en": dict(
            title="The bonus explosion, left half and right half",
            sub1="Two fixed addresses in alien_logic.c - 0x17D0 and 0x17D6 - each drawn with the same 3x2 routine.",
            sub2="Neither half is a sprite on its own; the game places them side by side to make one wide explosion.",
            routine="drawNx2 with n=3, twice · 12 characters total",
            source="alien_logic.c: l3796_bonus_explosion_left/l3758_bonus_explosion_right call drawNx2(0x17D0 and 0x17D6, hl, 0xFFDF, 3)",
            alt="The two halves of the Phoenix bonus explosion, each a 3x2 block of six characters, with the character codes listed.",
            notes=[
                "Unlike the alien explosion these addresses are literals in the code, not entries in a frame table.",
                "Splitting a wide object into two calls is how the ROM avoids a wider drawing routine.",
            ]),
        "nl": dict(
            title="De bonusexplosie, linkerhelft en rechterhelft",
            sub1="Twee vaste adressen in alien_logic.c - 0x17D0 en 0x17D6 - elk getekend met dezelfde 3x2-routine.",
            sub2="Geen van beide helften is op zichzelf een sprite; het spel zet ze naast elkaar tot één brede explosie.",
            routine="drawNx2 met n=3, twee keer · 12 karakters totaal",
            source="alien_logic.c: l3796_bonus_explosion_left/l3758_bonus_explosion_right roepen drawNx2(0x17D0 resp. 0x17D6, hl, 0xFFDF, 3) aan",
            alt="De twee helften van de Phoenix-bonusexplosie, elk een 3x2-blok van zes karakters, met de karaktercodes erbij.",
            notes=[
                "Anders dan bij de alien-explosie zijn deze adressen literals in de code, geen regels in een frametabel.",
                "Een breed object in twee aanroepen splitsen is hoe de ROM een bredere tekenroutine vermijdt.",
            ]),
    }
    for lang, s in bn.items():
        suffix = "" if lang == "en" else ".nl"
        emit(f"sequence-bonus-explosion{suffix}.svg",
             sheet_sequence(fg, palette, foreground=True,
                            frames=bonus_frames, layout=(3, 2), strings=s))

    # -- birds: the growth series, and two flap cycles -----------------------
    GROWTH = [2, 3, 4, 5, 6, 7, 10, 11]          # narrow egg through widest bird
    SMALL, GROWN = 7, 11
    growth_frames = [pad_to(bird_frame(t, 0), bird_width(t), 7) for t in GROWTH]
    small_frames = bird_frames(SMALL)
    grown_frames = bird_frames(GROWN)

    gw = {
        "en": dict(
            title="From egg to full wingspan",
            sub1="One frame from each bird shape type, in the order their widths grow: three characters wide, then four, up to seven.",
            sub2="A type's width comes from phoenix_bird_draw_entries; narrower shapes are centred here so the growth is easy to see.",
            routine="drawn by draw_bird_shape_350c · 2 to 7 columns x 2 rows · background set",
            source="attract_mode.c: drawbirdobject() calls draw_bird_shape_350c(entry, hl, shape)",
            alt="Eight bird shape types side by side, from a small round egg through a hatching bird to a grown bird with a full wingspan.",
            notes=[
                "The egg is not a separate object with its own code: it is the same draw routine with fewer columns.",
                "Widths are read from the table, not measured from the picture - the pointer stride between a type's frames is exactly two per column, which confirms it.",
            ]),
        "nl": dict(
            title="Van ei tot volledige spanwijdte",
            sub1="Eén frame per vogelvormtype, op volgorde van breedte: drie karakters breed, dan vier, tot zeven.",
            sub2="De breedte van een type komt uit phoenix_bird_draw_entries; smallere vormen staan hier gecentreerd zodat de groei zichtbaar is.",
            routine="getekend door draw_bird_shape_350c · 2 tot 7 kolommen x 2 rijen · achtergrondset",
            source="attract_mode.c: drawbirdobject() roept draw_bird_shape_350c(entry, hl, shape) aan",
            alt="Acht vogelvormtypes naast elkaar, van een klein rond ei via een uitkomende vogel tot een volgroeide vogel met volle spanwijdte.",
            notes=[
                "Het ei is geen apart object met eigen code: het is dezelfde tekenroutine met minder kolommen.",
                "De breedtes komen uit de tabel, niet uit het plaatje - de pointerstap tussen de frames van een type is precies twee per kolom, en dat bevestigt het.",
            ]),
    }
    for lang, s in gw.items():
        suffix = "" if lang == "en" else ".nl"
        emit(f"sequence-bird-growth{suffix}.svg",
             sheet_sequence(bg, palette, foreground=False,
                            frames=growth_frames, layout=(7, 2), strings=s))

    for tag, frames_, cols, ttl in (
            ("small", small_frames, bird_width(SMALL),
             ("The small bird, frame by frame", "De kleine vogel, frame voor frame")),
            ("grown", grown_frames, bird_width(GROWN),
             ("The grown bird, frame by frame", "De volgroeide vogel, frame voor frame"))):
        bt = SMALL if tag == "small" else GROWN
        strs = {
            "en": dict(
                title=ttl[0],
                sub1=f"Shape type {bt} has four frames, each {cols} characters wide and two tall.",
                sub2="The four pointers sit consecutively in phoenix_bird_shape_pointers, one stride of two per column apart.",
                routine=f"draw_bird_shape_350c · {cols} columns x 2 rows · {cols * 2} characters",
                source=f"attract_mode.c: drawbirdobject() calls draw_bird_shape_350c() for type {bt}; width from phoenix_bird_draw_entries[{bt}]",
                alt=f"The four animation frames of Phoenix bird shape type {bt}, with the character codes listed.",
                notes=[
                    "Compare the codes between frames: the wing characters change while the body stays put.",
                ]),
            "nl": dict(
                title=ttl[1],
                sub1=f"Vormtype {bt} heeft vier frames, elk {cols} karakters breed en twee hoog.",
                sub2="De vier pointers staan achter elkaar in phoenix_bird_shape_pointers, telkens twee per kolom uit elkaar.",
                routine=f"draw_bird_shape_350c · {cols} kolommen x 2 rijen · {cols * 2} karakters",
                source=f"attract_mode.c: drawbirdobject() roept voor type {bt} draw_bird_shape_350c() aan; breedte uit phoenix_bird_draw_entries[{bt}]",
                alt=f"De vier animatieframes van Phoenix-vogelvormtype {bt}, met de karaktercodes erbij.",
                notes=[
                    "Vergelijk de codes tussen de frames: de vleugelkarakters wisselen terwijl het lijf blijft staan.",
                ]),
        }
        for lang, s in strs.items():
            suffix = "" if lang == "en" else ".nl"
            emit(f"sequence-bird-{tag}{suffix}.svg",
                 sheet_sequence(bg, palette, foreground=False,
                                frames=frames_, layout=(cols, 2), strings=s))

    # -- the same sequences, playing ----------------------------------------
    # Pace is deliberately slow: these are for studying a sequence, not for
    # reproducing the speed the arcade board runs it at.
    anim = {
        "player-ship": dict(
            tiles=fg, foreground=True, frames=ship_frames, layout=(2, 2), ms_per_frame=600,
            en=dict(sub1="The eight poses, one after another.",
                    notes=["In play these are selected by game state, not run as a loop; the cycle here is only to show them all."]),
            nl=dict(sub1="De acht poses, een voor een.",
                    notes=["In het spel kiest de spelsituatie de pose; de cyclus hier is er alleen om ze allemaal te tonen."])),
        "mothership-pilot": dict(
            tiles=bg, foreground=False, frames=pilot_frames, layout=(2, 4), ms_per_frame=500,
            en=dict(sub1="The eight pilot frames, slowed down to be readable.",
                    notes=["Four rows tall - the tallest block any of these routines draws."]),
            nl=dict(sub1="De acht pilootframes, vertraagd zodat je ze kunt volgen.",
                    notes=["Vier rijen hoog - het hoogste blok dat een van deze routines tekent."])),
        "explosion": dict(
            tiles=fg, foreground=True, frames=boom_frames, layout=(3, 2), ms_per_frame=650,
            en=dict(sub1="All eight frames, in table order, slowed down to be readable.",
                    notes=["It starts on the erase frame, so the loop opens with a blank - that is in the data, not a gap.",
                           "The arcade board steps through these far faster; this pace is for studying them."]),
            nl=dict(sub1="Alle acht frames, in tabelvolgorde, vertraagd zodat je ze kunt volgen.",
                    notes=["Hij begint op het wisframe, dus de lus opent met niets - dat zit zo in de data, het is geen gat.",
                           "Het arcade-board loopt hier veel sneller doorheen; dit tempo is om te bestuderen."])),
        "bird-growth": dict(
            tiles=bg, foreground=False, frames=growth_frames, layout=(7, 2), ms_per_frame=700,
            en=dict(sub1="The bird shape types in width order, so the growth plays as one sequence.",
                    notes=["This is a tour of the types, not an animation the game plays; a real bird changes type on a game event."]),
            nl=dict(sub1="De vogelvormtypes op volgorde van breedte, zodat de groei als een reeks afspeelt.",
                    notes=["Dit is een rondgang langs de types, geen animatie die het spel afspeelt; een echte vogel wisselt van type bij een spelgebeurtenis."])),
        "bird-small": dict(
            tiles=bg, foreground=False, frames=small_frames, layout=(bird_width(SMALL), 2), ms_per_frame=450,
            en=dict(sub1="The four frames of the small bird, slowed down to be readable.",
                    notes=["The wing characters change while the body stays put - that is the flap."]),
            nl=dict(sub1="De vier frames van de kleine vogel, vertraagd zodat je ze kunt volgen.",
                    notes=["De vleugelkarakters wisselen terwijl het lijf blijft staan - dat is de vleugelslag."])),
        "bird-grown": dict(
            tiles=bg, foreground=False, frames=grown_frames, layout=(bird_width(GROWN), 2), ms_per_frame=450,
            en=dict(sub1="The four frames of the grown bird, slowed down to be readable.",
                    notes=["Seven characters wide: the widest sprite the bird routine draws."]),
            nl=dict(sub1="De vier frames van de volgroeide vogel, vertraagd zodat je ze kunt volgen.",
                    notes=["Zeven karakters breed: de breedste sprite die de vogelroutine tekent."])),
        "bonus-explosion": dict(
            tiles=fg, foreground=True, frames=bonus_frames, layout=(3, 2), ms_per_frame=1400,
            en=dict(sub1="The two halves shown in turn, which is not how the game shows them.",
                    notes=["On screen these are drawn side by side at the same moment; showing them in turn here just makes both visible."]),
            nl=dict(sub1="De twee helften om beurten getoond, wat niet is hoe het spel ze toont.",
                    notes=["Op het scherm staan ze tegelijk naast elkaar; hier komen ze om beurten zodat beide zichtbaar zijn."])),
    }
    titles = {
        "player-ship": ("The player ship, playing", "Het spelerschip, in beweging"),
        "alien": ("The formation alien, playing", "De formatie-alien, in beweging"),
        "mothership-pilot": ("The mothership pilot, playing", "De piloot van het moederschip, in beweging"),
        "explosion": ("An explosion, playing", "Een explosie, in beweging"),
        "bonus-explosion": ("The bonus explosion, playing", "De bonusexplosie, in beweging"),
        "bird-growth": ("From egg to full wingspan, playing", "Van ei tot volle spanwijdte, in beweging"),
        "bird-small": ("The small bird, playing", "De kleine vogel, in beweging"),
        "bird-grown": ("The grown bird, playing", "De volgroeide vogel, in beweging"),
    }
    routines = {
        "player-ship": ("2x2 block · 4 characters", "2x2-blok · 4 karakters"),
        "alien": ("2x1 block · 2 characters", "2x1-blok · 2 karakters"),
        "mothership-pilot": ("draw_image_c_by_b · 4 rows x 2 columns", "draw_image_c_by_b · 4 rijen x 2 kolommen"),
        "explosion": ("drawNx2 with n=3 · 6 characters", "drawNx2 met n=3 · 6 karakters"),
        "bonus-explosion": ("drawNx2 with n=3 · 6 characters per half", "drawNx2 met n=3 · 6 karakters per helft"),
        "bird-growth": ("draw_bird_shape_350c · 2 to 7 columns", "draw_bird_shape_350c · 2 tot 7 kolommen"),
        "bird-small": (f"draw_bird_shape_350c · {bird_width(SMALL)} columns x 2",
                       f"draw_bird_shape_350c · {bird_width(SMALL)} kolommen x 2"),
        "bird-grown": (f"draw_bird_shape_350c · {bird_width(GROWN)} columns x 2",
                       f"draw_bird_shape_350c · {bird_width(GROWN)} kolommen x 2"),
    }
    for tag, size, frames, names in anim_extra:
        cols, rows = size
        for li, lang in enumerate(("en", "nl")):
            suffix = "" if lang == "en" else ".nl"
            ss = dict(
                title=(f"The formation alien {names[0]}, playing" if lang == "en"
                       else f"De formatie-alien {names[1]}, in beweging"),
                sub1=(f"{len(frames)} poses of {cols}x{rows} characters." if lang == "en"
                      else f"{len(frames)} poses van {cols}x{rows} karakters."),
                routine=(f"{cols}x{rows} block" if lang == "en" else f"{cols}x{rows}-blok"),
                notes=(["Read out of a recorded session, not from a shape table."] if lang == "en"
                       else ["Afgelezen uit een opgenomen sessie, niet uit een vormtabel."]))
            ss["alt"] = ss["sub1"]
            emit(f"animation-{tag}{suffix}.svg",
                 sheet_animation(fg, palette, foreground=True, frames=frames,
                                 layout=size, ms_per_frame=450, strings=ss))

    for name, cfg in anim.items():
        for li, lang in enumerate(("en", "nl")):
            suffix = "" if lang == "en" else ".nl"
            s = dict(cfg[lang])
            s["title"] = titles[name][li]
            s["routine"] = routines[name][li]
            s["alt"] = s["sub1"]
            emit(f"animation-{name}{suffix}.svg",
                 sheet_animation(cfg["tiles"], palette, foreground=cfg["foreground"],
                                 frames=cfg["frames"], layout=cfg["layout"],
                                 ms_per_frame=cfg["ms_per_frame"], strings=s))

    # -- the mothership hull -------------------------------------------------
    # Not found by scanning a recording: the hull shares its colour groups with
    # a grown bird, and that scan produced birds labelled as a hull, twice. The
    # hull is table-defined after all - phoenix_mothership_tile_page is a whole
    # 26x9 page, stored upside down because the ship scrolls in from the top.
    # The low-numbered characters around the ship are the starfield the same
    # page carries; that is exactly why a colour scan could not isolate it.
    HULL_W, HULL_H = 26, 9
    page = read_table(tables, "phoenix_mothership_tile_page")
    hull = [page[(HULL_H - 1 - (k % HULL_H)) * HULL_W + (k // HULL_H)]
            for k in range(HULL_W * HULL_H)]        # flip rows, column-major
    hs = {
        "en": dict(
            title="The mothership hull",
            sub1="One 26 x 9 page of characters - the largest object in the game, and the only one stored as a whole screen page.",
            sub2="Stored upside down and flipped back here: the ship scrolls in from the top of the screen, so the ROM holds it bottom row first.",
            routine="draw_image_c_by_b · 26 columns x 9 rows · 234 characters · background set",
            source="hw_video_audio.c: stars_scroll_down() reads the page through phoenix_starfield_or_mothership_byte(); utilities.c: draw_image_c_by_b() draws it",
            alt="The Phoenix mothership hull, twenty-six characters wide and nine tall, surrounded by the starfield characters carried on the same ROM page.",
            notes=[
                "The scattered single characters around the hull are stars, not ship: this page is one of the three the starfield scroller can point at.",
                "Because the stars share the hull's colour groups, scanning a recording by colour cannot separate them - the shape had to come from the table.",
            ]),
        "nl": dict(
            title="De romp van het moederschip",
            sub1="Eén pagina van 26 x 9 karakters - het grootste object in het spel, en het enige dat als hele schermpagina is opgeslagen.",
            sub2="Ondersteboven opgeslagen en hier teruggedraaid: het schip komt van bovenaf binnenscrollen, dus de ROM bewaart de onderste rij eerst.",
            routine="draw_image_c_by_b · 26 kolommen x 9 rijen · 234 karakters · achtergrondset",
            source="hw_video_audio.c: stars_scroll_down() leest de pagina via phoenix_starfield_or_mothership_byte(); utilities.c: draw_image_c_by_b() tekent hem",
            alt="De romp van het Phoenix-moederschip, zesentwintig karakters breed en negen hoog, omringd door de sterrenveldkarakters op dezelfde ROM-pagina.",
            notes=[
                "De losse karakters rondom de romp zijn sterren, geen schip: deze pagina is een van de drie waar de sterrenveldscroller naar kan wijzen.",
                "Omdat die sterren dezelfde kleurgroepen delen als de romp, kan een kleurenscan van een opname ze niet scheiden - de vorm moest uit de tabel komen.",
            ]),
    }
    for lang, s in hs.items():
        emit(f"sequence-mothership-hull{'' if lang == 'en' else '.nl'}.svg",
             sheet_sequence(bg, palette, foreground=False, frames=[hull],
                            layout=(HULL_W, HULL_H), strings=s))

    print(f"runtime sprites read from {dump.name}")
    for p in written:
        label = p.relative_to(PROJECT) if PROJECT in p.parents else p
        print("wrote", label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
