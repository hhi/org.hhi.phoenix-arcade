# Native C2 Original Sprites In Hi-Res

Dutch version: [NATIVE-ART.nl.md](NATIVE-ART.nl.md).

Native C2 preserves the original Phoenix sprite silhouettes, animation frames,
and colour assignment without reverting to unrelated vector figures. It uses a
separate 16x16 C2 glyph for every original foreground and background character,
instead of rendering the original 8x8 bitmap at runtime. Each glyph has flat,
fully opaque PROM-derived colour areas. Birds, aliens, the ship, and
projectiles therefore remain recognisably
Phoenix while becoming sharper and more legible on a modern display.

## Build Atlas, Not Runtime ROM

`make c2` runs [generate_hires_sprite_assets.py](tools/generate_hires_sprite_assets.py)
when its source data changes. The script reads the assembled `graphics.rom` and
`proms.rom` images and
generates `native/c2_hires_sprite_assets.h` containing:

- dedicated 16x16 C2 hi-res glyphs for each original foreground and background character;
- RGB values computed from the original colour PROMs.

The final C2 binary does not read `gfx_mem`, `palette_prom_a`, or
`palette_prom_b`. The generated atlas is a C2 build artifact containing the
derived sprite data. `make native-check` protects that runtime boundary.

## Rendering And Animation

| Family | C2 source | Hi-res rendering |
| --- | --- | --- |
| Player ship, aliens, bullets, text, and explosions | Current `ForegroundScreen` tile indices plus the C2 foreground glyph atlas | A dedicated 16x16 glyph per character. A field-wide pixel-art compositor joins adjacent characters before scaling, so curved or diagonal outlines do not break at character boundaries. |
| Birds | Current `BackgroundScreen` composition and the C2 background glyph atlas | The shared game core has already executed `DrawBirdObject`; C2 joins the resulting tiles before rendering. This retains the original per-frame animation, overlap, and clearing transitions while smoothing the bird contours. |
| Colour | Existing Phoenix colour-PROM formula during atlas generation | The same palette bank and tile colour role as the original renderer. |

The shared gamecore remains the only source for movement, timing, collision,
score, levels, and visible playfield data. This renderer does not add visual
objects or alter game state.

The compositor does not invent stars, vector figures, or new objects. It only
uses the visible foreground/background tile masks and their PROM-derived
colours. Its final one-hi-res-pixel contour coverage softens outer diagonal
corners while retaining opaque sprite interiors.

## Verification

`make native-check` verifies that the C2 binary contains no graphics or
colour-PROM symbols. `make native-compare` compares a headless C2 replay with
a JPhoenix reference dump. The sprite upgrade therefore remains separate from
the lockstep evidence for game state.
