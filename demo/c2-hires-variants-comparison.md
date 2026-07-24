# C2 Rendering Variants: hires, hires2, hires2a, hires3, hires3a

Dutch version: [c2-hires-variants-comparison.nl.md](c2-hires-variants-comparison.nl.md).

Five builds of the same `c2-phoenix` native renderer, same replay
(`bird-investigation.txt`), same frame (945). Each build shares the same C
gamecore and the same ROM-derived hi-res glyph atlas; only the rendering
step differs, selected at build time with `C2_VARIANT`
(`c2-phoenix/native/c2_renderer.c` documents each one). `hires3a` is the
default (no `C2_VARIANT` needed); the others are opt-in comparisons.

## classic

`make c2-run C2_VARIANT=classic` -- the original, unblended rendering: a
flat PROM colour per tile, hard steps at colour boundaries.

| Detail | Full frame |
| --- | --- |
| <img src="c2-variant-classic-detail.png" alt="classic variant detail crop" width="360"> | <img src="c2-variant-classic-full.png" alt="classic variant full frame" width="240"> |

## hires2

`make c2-run C2_VARIANT=hires2` -- adds `blend_colour_transitions()`: one
pass over four orthogonal neighbours, softening the hard step between two
adjacent primary colours into a thin transition band.

| Detail | Full frame |
| --- | --- |
| <img src="c2-variant-hires2-detail.png" alt="hires2 variant detail crop" width="360"> | <img src="c2-variant-hires2-full.png" alt="hires2 variant full frame" width="240"> |

## hires2a

`make c2-run C2_VARIANT=hires2a` -- the same blend, widened: eight
neighbours (including diagonals) and two passes, producing a broader,
rounder transition band than `hires2`.

| Detail | Full frame |
| --- | --- |
| <img src="c2-variant-hires2a-detail.png" alt="hires2a variant detail crop" width="360"> | <img src="c2-variant-hires2a-full.png" alt="hires2a variant full frame" width="240"> |

## hires3

`make c2-run C2_VARIANT=hires3` -- adds `apply_grain()` instead of colour
blending: every opaque pixel's colour is perturbed by a fixed,
position-hashed offset (+/-12 per channel), giving a stable, printed-looking
grain texture rather than a smooth gradient. The hash is based on pixel
position, not frame number, so the grain does not flicker.

| Detail | Full frame |
| --- | --- |
| <img src="c2-variant-hires3-detail.png" alt="hires3 variant detail crop" width="360"> | <img src="c2-variant-hires3-full.png" alt="hires3 variant full frame" width="240"> |

## hires3a (default)

No `C2_VARIANT` needed -- combines `hires2`'s colour-transition blend (one
pass, four neighbours) with a softened version of `hires3`'s grain (half
amplitude, +/-6). The colour-transition band stays visible while the grain
reads as gentle shading rather than heavy texture.

| Detail | Full frame |
| --- | --- |
| <img src="c2-variant-hires3a-detail.png" alt="hires3a variant detail crop" width="360"> | <img src="c2-variant-hires3a-full.png" alt="hires3a variant full frame" width="240"> |

## Trying a variant yourself

```sh
make c2-run C2_VARIANT=hires2a
```

Each variant builds into its own binary (`c2-phoenix/build/native/<variant>/c2-phoenix`),
so switching does not require cleaning a previous build, and `make c2-run`
with no `C2_VARIANT` always rebuilds the `hires3a` default.
