#!/usr/bin/env python3
"""Generate the local Phoenix tile/palette header from legally supplied ROMs.

The resulting header is a local build artifact: it is deliberately ignored by
Git and never needs to be committed with the Redot port.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def channel(bits: int) -> int:
    conductance = 1.0 / 100.0 + 1.0 / 270.0
    current = 5.0 / 100.0
    if not bits & 1:
        conductance += 1.0 / 270.0
        current += .05 / 270.0
    if not bits & 2:
        conductance += 1.0
        current += .05
    return int((current / conductance) * 255.0 / 5.0 + .4)


def trunc_div(numerator: int, denominator: int) -> int:
    return numerator // denominator if numerator >= 0 else -((-numerator) // denominator)


def palette(proms: bytes) -> list[tuple[int, int, int]]:
    low, high = proms[:0x100], proms[0x100:]
    raw: list[tuple[int, int, int]] = []
    luminance: list[int] = []
    for address in range(128):
        red = channel((low[address] & 1) | ((high[address] & 1) << 1))
        green = channel(((low[address] >> 2) & 1) | (((high[address] >> 2) & 1) << 1))
        blue = channel(((low[address] >> 1) & 1) | (((high[address] >> 1) & 1) << 1))
        raw.append((red, green, blue))
        luminance.append(299 * red + 587 * green + 114 * blue)
    low_luma, high_luma = min(luminance), max(luminance)
    result = []
    for (red, green, blue), value in zip(raw, luminance):
        u = trunc_div((blue - value // 1000) * 492, 1000)
        v = trunc_div((red - value // 1000) * 877, 1000)
        target = ((value - low_luma) * 256) // (high_luma - low_luma)
        result.append((max(0, min(255, target + trunc_div(1140 * v, 1000))),
                       max(0, min(255, target - trunc_div(395 * u, 1000) - trunc_div(581 * v, 1000))),
                       max(0, min(255, target + trunc_div(2032 * u, 1000)))))
    return result


def tiles(graphics: bytes, offset: int) -> list[list[int]]:
    return [[((graphics[offset + tile * 8 + row + 0x800] >> (7 - col) & 1) << 1)
             | (graphics[offset + tile * 8 + row] >> (7 - col) & 1)
             for row in range(8) for col in range(8)] for tile in range(256)]


def emit(name: str, data: list[list[int]]) -> list[str]:
    return [f"static const uint8_t {name}[256][64] = {{"] + [
        "    {" + ", ".join(map(str, tile)) + "}," for tile in data] + ["};"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphics", type=Path, required=True)
    parser.add_argument("--proms", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    graphics, proms = args.graphics.read_bytes(), args.proms.read_bytes()
    if len(graphics) != 0x2000 or len(proms) != 0x200:
        raise SystemExit("expected graphics.rom (8192 bytes) and proms.rom (512 bytes)")
    lines = ["/* Generated locally from legal ROM inputs; do not commit. */", "#pragma once", "#include <stdint.h>",
             "typedef struct { uint8_t red, green, blue; } PhoenixRgb;", "static const PhoenixRgb phoenix_palette_rgb[128] = {"]
    lines += [f"    {{{red}, {green}, {blue}}}," for red, green, blue in palette(proms)] + ["};"]
    lines += emit("phoenix_background_tiles", tiles(graphics, 0))
    lines += emit("phoenix_foreground_tiles", tiles(graphics, 0x1000))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
