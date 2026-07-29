#!/usr/bin/env python3
"""Capture the six initial alien layouts with live RAM-coordinate overlays."""

import argparse
import json
import os
import struct
import subprocess
import zlib
from pathlib import Path


RAM_BASE = 0x4000
RAM_SIZE = 0x0C00
FRAME_SIZE = 4 + RAM_SIZE
LAYOUTS = (
    (0x1540, "layout-01"),
    (0x1560, "layout-02"),
    (0x1580, "layout-03"),
    (0x15A0, "layout-04"),
    (0x15C0, "layout-05"),
    (0x15E0, "layout-06"),
)

# Compact enough to keep labels readable on the 3x SDL captures.
FONT = {
    "#": ("01010", "11111", "01010", "11111", "01010", "00000", "00000"),
    "$": ("01110", "10100", "01110", "00101", "01110", "00100", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00110", "00100", "01000"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00110", "00001", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "11100"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
}


def read_ppm(path):
    with path.open("rb") as image:
        magic = image.readline().strip()
        if magic != b"P6":
            raise ValueError(f"{path} is not a binary PPM")
        tokens = []
        while len(tokens) < 3:
            line = image.readline()
            if not line:
                raise ValueError(f"incomplete PPM header in {path}")
            if not line.startswith(b"#"):
                tokens.extend(line.split())
        width, height, maximum = map(int, tokens[:3])
        if maximum != 255:
            raise ValueError(f"unsupported PPM maximum {maximum}")
        pixels = bytearray(image.read())
    if len(pixels) != width * height * 3:
        raise ValueError(f"unexpected pixel count in {path}")
    return width, height, pixels


def png_chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path, width, height, pixels):
    rows = b"".join(b"\0" + pixels[row * width * 3:(row + 1) * width * 3] for row in range(height))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(rows, level=9))
        + png_chunk(b"IEND", b"")
    )


def write_svg_wrapper(path, png_name, width, height, layout):
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
        f'<title id="title">Phoenix initial alien layout ${layout:04X}</title>'
        '<desc id="desc">Live SDL capture with alien number and RAM coordinate overlays.</desc>'
        f'<image href="{png_name}" width="{width}" height="{height}"/>'
        '</svg>\n',
        encoding="utf-8",
    )


def set_pixel(pixels, width, height, x, y, colour):
    if 0 <= x < width and 0 <= y < height:
        offset = (y * width + x) * 3
        pixels[offset:offset + 3] = bytes(colour)


def draw_box(pixels, width, height, x, y, colour):
    for delta in range(-5, 6):
        set_pixel(pixels, width, height, x + delta, y - 5, colour)
        set_pixel(pixels, width, height, x + delta, y + 5, colour)
        set_pixel(pixels, width, height, x - 5, y + delta, colour)
        set_pixel(pixels, width, height, x + 5, y + delta, colour)


def draw_text(pixels, width, height, x, y, text, colour):
    for char in text:
        glyph = FONT.get(char, FONT["#"])
        for row, bits in enumerate(glyph):
            for column, bit in enumerate(bits):
                if bit == "1":
                    set_pixel(pixels, width, height, x + column, y + row, colour)
        x += 6


def last_ram_frame(path):
    data = path.read_bytes()
    if len(data) < FRAME_SIZE or len(data) % FRAME_SIZE:
        raise ValueError(f"invalid RAM dump: {path}")
    offset = len(data) - FRAME_SIZE
    frame = struct.unpack(">I", data[offset:offset + 4])[0]
    return frame, data[offset + 4:offset + FRAME_SIZE]


def ram_byte(ram, address):
    return ram[address - RAM_BASE]


def ram_word(ram, address):
    return (ram_byte(ram, address) << 8) | ram_byte(ram, address + 1)


def alien_records(ram):
    records = []
    for alien in range(16):
        grid = 0x4B70 + alien * 4
        screen = 0x4BB0 + alien * 4
        records.append({
            "id": alien,
            "active": bool(ram_byte(ram, grid) & 0x08),
            "x": ram_byte(ram, grid + 2),
            "y": ram_byte(ram, grid + 3),
            "screen_address": ram_word(ram, screen + 2),
        })
    return records


def screen_position(address):
    if not 0x4000 <= address < 0x4400:
        return None
    offset = address - 0x4000
    return (25 - offset // 32) * 8, (offset % 32) * 8


def overlay_records(ppm_path, png_path, records):
    width, height, pixels = read_ppm(ppm_path)
    scale_x = width // 208
    scale_y = height // 256
    marker = (255, 238, 0)
    for record in records:
        if not record["active"]:
            continue
        position = screen_position(record["screen_address"])
        if position is None:
            continue
        x, y = position
        x *= scale_x
        y *= scale_y
        draw_box(pixels, width, height, x, y, marker)
        draw_text(pixels, width, height, x + 7, y - 8, f'#{record["id"]:X}', marker)
        draw_text(pixels, width, height, x + 7, y, f'${record["x"]:02X},{record["y"]:02X}', marker)
    write_png(png_path, width, height, pixels)
    return width, height


def capture(binary, output_dir, layout, name):
    ppm_path = output_dir / f"{name}.ppm"
    ram_path = output_dir / f"{name}.ram"
    png_path = output_dir / f"{name}.png"
    svg_path = output_dir / f"{name}.svg"
    environment = os.environ | {"SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}
    subprocess.run(
        [
            str(binary), f"--capture-initial-alien-layout={layout:04X}",
            "--run-frames=2", f"--screenshot={ppm_path}", f"--ram-dump={ram_path}",
        ],
        check=True,
        env=environment,
    )
    frame, ram = last_ram_frame(ram_path)
    records = alien_records(ram)
    width, height = overlay_records(ppm_path, png_path, records)
    write_svg_wrapper(svg_path, png_path.name, width, height, layout)
    ppm_path.unlink()
    ram_path.unlink()
    return {
        "layout": f"${layout:04X}",
        "name": name,
        "frame": frame,
        "level_and_round": f"0x{ram_byte(ram, 0x43B8):02X}",
        "image": png_path.name,
        "svg": svg_path.name,
        "aliens": records,
    }


def write_index(output_dir, captures):
    items = "\n".join(
        f'<figure><img src="{capture["image"]}" alt="Initial alien layout {capture["layout"]}">'
        f'<figcaption>{capture["layout"]} — level/round {capture["level_and_round"]}</figcaption></figure>'
        for capture in captures
    )
    output_dir.joinpath("index.html").write_text(
        "<!doctype html><meta charset=\"utf-8\"><title>Phoenix initial alien waves</title>"
        "<style>body{font-family:system-ui;margin:2rem;background:#111;color:#eee}"
        "main{display:grid;grid-template-columns:repeat(auto-fit,minmax(30rem,1fr));gap:1.5rem}"
        "figure{margin:0;border:1px solid #555;padding:.5rem}img{width:100%;image-rendering:pixelated}"
        "figcaption{padding:.5rem}</style><h1>Initial alien-wave captures</h1>"
        "<p>Yellow labels are live RAM coordinates from $4B70+i×4; markers use the live screen-RAM address.</p>"
        f"<main>{items}</main>",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, default=Path("build/c-phoenix"))
    parser.add_argument("--output", type=Path, default=Path("context/wave-screenshots"))
    args = parser.parse_args()
    binary = args.binary.resolve()
    if not binary.is_file():
        parser.error(f"binary not found: {binary}")
    args.output.mkdir(parents=True, exist_ok=True)
    captures = [capture(binary, args.output, layout, name) for layout, name in LAYOUTS]
    args.output.joinpath("metadata.json").write_text(json.dumps(captures, indent=2) + "\n", encoding="utf-8")
    write_index(args.output, captures)
    print(f"Wrote {len(captures)} live initial-wave captures to {args.output}")


if __name__ == "__main__":
    main()
