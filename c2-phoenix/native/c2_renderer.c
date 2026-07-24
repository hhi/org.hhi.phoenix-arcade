#include "c2_renderer.h"
#include "c2_hires_sprite_assets.h"

#include <stdint.h>
#include <string.h>

/* hires3a (hires2's colour-transition blend plus a softened hires3 grain) is
 * the default C2 look. Build with C2_VARIANT=classic for the original,
 * unblended hard-edge rendering, or with any other C2_VARIANT to compare an
 * individual experiment in isolation. */
#if !defined(C2_VARIANT_CLASSIC) && !defined(C2_VARIANT_HIRES2) \
    && !defined(C2_VARIANT_HIRES2A) && !defined(C2_VARIANT_HIRES3) \
    && !defined(C2_VARIANT_HIRES3A)
#define C2_VARIANT_HIRES3A 1
#endif

enum {
    C2_SCALE = 4,
    FIELD_WIDTH = 208,
    FIELD_HEIGHT = 256,
    SCREEN_COLUMNS = 26,
    SCREEN_ROWS = 32,
    TILE_SIZE = 8,
    HIRES_GLYPH_SIZE = 16,
    FIELD_PIXELS = FIELD_WIDTH * FIELD_HEIGHT,
    HIRES_FIELD_WIDTH = FIELD_WIDTH * 2,
    HIRES_FIELD_HEIGHT = FIELD_HEIGHT * 2,
    HIRES_FIELD_PIXELS = HIRES_FIELD_WIDTH * HIRES_FIELD_HEIGHT,
};

typedef struct {
    uint8_t red;
    uint8_t green;
    uint8_t blue;
} C2CanvasPixel;

static SDL_Texture *frame_texture;
static C2CanvasPixel canvas[HIRES_FIELD_PIXELS];
static C2CanvasPixel source_layer[FIELD_PIXELS];
static uint8_t source_mask[FIELD_PIXELS];
static C2CanvasPixel layer[HIRES_FIELD_PIXELS];
static uint8_t layer_mask[HIRES_FIELD_PIXELS];

static int scale(int value) {
    return value * C2_SCALE;
}

static C2HiresColour tile_colour(uint8_t tile, uint8_t colour_index,
                                 uint8_t palette_bank, uint8_t foreground) {
    uint8_t index = (uint8_t)((palette_bank << 6) | foreground | (colour_index << 3)
                              | ((tile >> 5) & 0x07));
    return C2_HIRES_PROM_COLOURS[index];
}

static int pixel_index(int x, int y) {
    return y * HIRES_FIELD_WIDTH + x;
}

static int source_index(int x, int y) {
    return y * FIELD_WIDTH + x;
}

static int source_has_pixel(int x, int y) {
    if (x < 0 || x >= FIELD_WIDTH) {
        return 0;
    }
    return source_mask[source_index(x, y & (FIELD_HEIGHT - 1))] != 0;
}

static C2CanvasPixel source_pixel(int x, int y) {
    static const C2CanvasPixel black = {0, 0, 0};
    if (!source_has_pixel(x, y)) {
        return black;
    }
    return source_layer[source_index(x, y & (FIELD_HEIGHT - 1))];
}

static int same_source_pixel(int left_x, int left_y, int right_x, int right_y) {
    C2CanvasPixel left;
    C2CanvasPixel right;
    if (source_has_pixel(left_x, left_y) != source_has_pixel(right_x, right_y)) {
        return 0;
    }
    if (!source_has_pixel(left_x, left_y)) {
        return 1;
    }
    left = source_pixel(left_x, left_y);
    right = source_pixel(right_x, right_y);
    return left.red == right.red && left.green == right.green && left.blue == right.blue;
}

#if defined(C2_VARIANT_HIRES2) || defined(C2_VARIANT_HIRES2A) || defined(C2_VARIANT_HIRES3A)
static int same_layer_colour(int ax, int ay, int bx, int by);
static void blend_colour_transitions(void);
#endif

#if defined(C2_VARIANT_HIRES3) || defined(C2_VARIANT_HIRES3A)
static void apply_grain(void);
#endif

static int layer_has_pixel(int x, int y) {
    if (x < 0 || x >= HIRES_FIELD_WIDTH || y < 0 || y >= HIRES_FIELD_HEIGHT) {
        return 0;
    }
    return layer_mask[pixel_index(x, y)] != 0;
}

static void rasterize_tile_layer(const uint8_t *screen, const uint8_t glyphs[256][256],
                                 uint8_t palette_bank, uint8_t foreground, uint8_t scroll) {
    memset(source_mask, 0, sizeof(source_mask));
    for (int column = 0; column < SCREEN_COLUMNS; column++) {
        for (int row = 0; row < SCREEN_ROWS; row++) {
            uint8_t tile = screen[column * SCREEN_ROWS + row];
            if (tile == 0) {
                continue;
            }

            int origin_x = (SCREEN_COLUMNS - 1 - column) * TILE_SIZE;
            int origin_y = (row * TILE_SIZE - scroll) & (FIELD_HEIGHT - 1);
            for (int glyph_y = 0; glyph_y < TILE_SIZE; glyph_y++) {
                for (int glyph_x = 0; glyph_x < TILE_SIZE; glyph_x++) {
                    uint8_t encoded = glyphs[tile][(glyph_y * 2) * HIRES_GLYPH_SIZE
                                                    + glyph_x * 2];
                    uint8_t colour_index = C2_HIRES_PIXEL_COLOUR(encoded);
                    C2HiresColour colour;
                    if (C2_HIRES_PIXEL_OPACITY(encoded) == 0) {
                        continue;
                    }

                    int x = origin_x + glyph_x;
                    int y = (origin_y + glyph_y) & (FIELD_HEIGHT - 1);
                    int index = source_index(x, y);
                    colour = tile_colour(tile, colour_index, palette_bank, foreground);
                    source_layer[index].red = colour.red;
                    source_layer[index].green = colour.green;
                    source_layer[index].blue = colour.blue;
                    source_mask[index] = 1;
                }
            }
        }
    }
}

static void scale_source_layer(void) {
    memset(layer_mask, 0, sizeof(layer_mask));
    for (int y = 0; y < FIELD_HEIGHT; y++) {
        for (int x = 0; x < FIELD_WIDTH; x++) {
            C2CanvasPixel e = source_pixel(x, y);
            C2CanvasPixel d = source_pixel(x - 1, y);
            C2CanvasPixel f = source_pixel(x + 1, y);
            C2CanvasPixel output[4] = {e, e, e, e};
            int source_is_visible = source_has_pixel(x, y);
            uint8_t output_mask[4] = {
                source_is_visible, source_is_visible, source_is_visible, source_is_visible,
            };
            int b_equals_h = same_source_pixel(x, y - 1, x, y + 1);
            int d_equals_f = same_source_pixel(x - 1, y, x + 1, y);

            if (source_is_visible && !b_equals_h && !d_equals_f) {
                if (same_source_pixel(x - 1, y, x, y - 1)
                    && !same_source_pixel(x - 1, y, x, y + 1)
                    && !same_source_pixel(x, y - 1, x + 1, y)) {
                    output[0] = d;
                    output_mask[0] = source_has_pixel(x - 1, y);
                }
                if (same_source_pixel(x, y - 1, x + 1, y)
                    && !same_source_pixel(x, y - 1, x - 1, y)
                    && !same_source_pixel(x + 1, y, x, y + 1)) {
                    output[1] = f;
                    output_mask[1] = source_has_pixel(x + 1, y);
                }
                if (same_source_pixel(x - 1, y, x, y + 1)
                    && !same_source_pixel(x - 1, y, x, y - 1)
                    && !same_source_pixel(x, y + 1, x + 1, y)) {
                    output[2] = d;
                    output_mask[2] = source_has_pixel(x - 1, y);
                }
                if (same_source_pixel(x, y + 1, x + 1, y)
                    && !same_source_pixel(x, y + 1, x - 1, y)
                    && !same_source_pixel(x + 1, y, x, y - 1)) {
                    output[3] = f;
                    output_mask[3] = source_has_pixel(x + 1, y);
                }
            }

            for (int output_y = 0; output_y < 2; output_y++) {
                for (int output_x = 0; output_x < 2; output_x++) {
                    int output_index = pixel_index(x * 2 + output_x, y * 2 + output_y);
                    layer[output_index] = output[output_y * 2 + output_x];
                    layer_mask[output_index] = output_mask[output_y * 2 + output_x];
                }
            }
        }
    }
}

#if defined(C2_VARIANT_HIRES2) || defined(C2_VARIANT_HIRES2A) || defined(C2_VARIANT_HIRES3A)
#ifdef C2_VARIANT_HIRES2A
enum { C2_BLEND_PASSES = 2, C2_BLEND_NEIGHBOURS = 8 };
#else
enum { C2_BLEND_PASSES = 1, C2_BLEND_NEIGHBOURS = 4 };
#endif

static int same_layer_colour(int ax, int ay, int bx, int by) {
    C2CanvasPixel a;
    C2CanvasPixel b;
    if (!layer_has_pixel(ax, ay) || !layer_has_pixel(bx, by)) {
        return 0;
    }
    a = layer[pixel_index(ax, ay)];
    b = layer[pixel_index(bx, by)];
    return a.red == b.red && a.green == b.green && a.blue == b.blue;
}

/* Softens the hard colour step between adjacent opaque regions of two
 * different primary hardware colours (e.g. an alien's body/wing bands).
 * Runs only across already-opaque neighbours, so it never touches the
 * background-edge antialiasing that contour_opacity() applies afterwards.
 * hires2a widens and rounds the band by adding diagonal neighbours and a
 * second pass on top of hires2's single orthogonal pass. */
static void blend_colour_transitions_pass(void) {
    static C2CanvasPixel blended[HIRES_FIELD_PIXELS];
    static const int offsets[8][2] = {
        {1, 0}, {-1, 0}, {0, 1}, {0, -1},
        {1, 1}, {1, -1}, {-1, 1}, {-1, -1},
    };

    memcpy(blended, layer, sizeof(blended));
    for (int y = 0; y < HIRES_FIELD_HEIGHT; y++) {
        for (int x = 0; x < HIRES_FIELD_WIDTH; x++) {
            long red;
            long green;
            long blue;
            int samples;
            C2CanvasPixel centre;
            if (!layer_has_pixel(x, y)) {
                continue;
            }
            centre = layer[pixel_index(x, y)];
            red = centre.red;
            green = centre.green;
            blue = centre.blue;
            samples = 1;
            for (int n = 0; n < C2_BLEND_NEIGHBOURS; n++) {
                int nx = x + offsets[n][0];
                int ny = y + offsets[n][1];
                C2CanvasPixel neighbour;
                if (!layer_has_pixel(nx, ny) || same_layer_colour(x, y, nx, ny)) {
                    continue;
                }
                neighbour = layer[pixel_index(nx, ny)];
                red += neighbour.red;
                green += neighbour.green;
                blue += neighbour.blue;
                samples++;
            }
            if (samples == 1) {
                continue;
            }
            blended[pixel_index(x, y)].red = (uint8_t)(red / samples);
            blended[pixel_index(x, y)].green = (uint8_t)(green / samples);
            blended[pixel_index(x, y)].blue = (uint8_t)(blue / samples);
        }
    }
    memcpy(layer, blended, sizeof(blended));
}

static void blend_colour_transitions(void) {
    for (int pass = 0; pass < C2_BLEND_PASSES; pass++) {
        blend_colour_transitions_pass();
    }
}
#endif

#if defined(C2_VARIANT_HIRES3) || defined(C2_VARIANT_HIRES3A)
#ifdef C2_VARIANT_HIRES3A
enum { C2_GRAIN_AMPLITUDE = 6 };
#else
enum { C2_GRAIN_AMPLITUDE = 12 };
#endif

static uint32_t grain_hash(int x, int y, int channel) {
    uint32_t h = (uint32_t)x * 374761393u + (uint32_t)y * 668265263u
                 + (uint32_t)channel * 2654435761u;
    h = (h ^ (h >> 13)) * 1274126177u;
    return h ^ (h >> 16);
}

static uint8_t grain_channel(uint8_t value, int x, int y, int channel) {
    int offset = (int)(grain_hash(x, y, channel) % (2 * C2_GRAIN_AMPLITUDE + 1))
                 - C2_GRAIN_AMPLITUDE;
    int result = (int)value + offset;
    if (result < 0) {
        result = 0;
    } else if (result > 255) {
        result = 255;
    }
    return (uint8_t)result;
}

/* Perturbs each already-opaque hi-res pixel's colour within a small range of
 * its resolved hardware colour, using a fixed position-based hash so the
 * grain reads as a stable printed texture rather than per-frame flicker.
 * Runs on the Scale2x'd layer before contour_opacity()'s background-edge
 * blend, so silhouettes and opacity stay untouched. */
static void apply_grain(void) {
    for (int y = 0; y < HIRES_FIELD_HEIGHT; y++) {
        for (int x = 0; x < HIRES_FIELD_WIDTH; x++) {
            int index;
            if (!layer_has_pixel(x, y)) {
                continue;
            }
            index = pixel_index(x, y);
            layer[index].red = grain_channel(layer[index].red, x, y, 0);
            layer[index].green = grain_channel(layer[index].green, x, y, 1);
            layer[index].blue = grain_channel(layer[index].blue, x, y, 2);
        }
    }
}
#endif

/* A single partially covered hi-res corner rounds a 2x2 source-pixel block.
 * The mask spans the complete tile layer, so contours stay continuous across tiles. */
static uint8_t contour_opacity(int x, int y) {
    int left = !layer_has_pixel(x - 1, y);
    int right = !layer_has_pixel(x + 1, y);
    int top = !layer_has_pixel(x, y - 1);
    int bottom = !layer_has_pixel(x, y + 1);

    if ((x & 1) == 0 && (y & 1) == 0 && left && top && !layer_has_pixel(x - 1, y - 1)) {
        return 160;
    }
    if ((x & 1) != 0 && (y & 1) == 0 && right && top && !layer_has_pixel(x + 1, y - 1)) {
        return 160;
    }
    if ((x & 1) == 0 && (y & 1) != 0 && left && bottom && !layer_has_pixel(x - 1, y + 1)) {
        return 160;
    }
    if ((x & 1) != 0 && (y & 1) != 0 && right && bottom && !layer_has_pixel(x + 1, y + 1)) {
        return 160;
    }
    return 255;
}

static void composite_layer(void) {
    for (int index = 0; index < HIRES_FIELD_PIXELS; index++) {
        if (layer_mask[index] == 0) {
            continue;
        }

        int x = index % HIRES_FIELD_WIDTH;
        int y = index / HIRES_FIELD_WIDTH;
        uint8_t alpha = contour_opacity(x, y);
        canvas[index].red = (uint8_t)((layer[index].red * alpha
                                       + canvas[index].red * (255 - alpha) + 127) / 255);
        canvas[index].green = (uint8_t)((layer[index].green * alpha
                                         + canvas[index].green * (255 - alpha) + 127) / 255);
        canvas[index].blue = (uint8_t)((layer[index].blue * alpha
                                        + canvas[index].blue * (255 - alpha) + 127) / 255);
    }
}

static SDL_Texture *get_frame_texture(SDL_Renderer *renderer) {
    if (frame_texture != NULL) {
        return frame_texture;
    }

    frame_texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA8888,
                                      SDL_TEXTUREACCESS_STREAMING,
                                      HIRES_FIELD_WIDTH, HIRES_FIELD_HEIGHT);
    if (frame_texture != NULL) {
#if SDL_VERSION_ATLEAST(2, 0, 12)
        SDL_SetTextureScaleMode(frame_texture, SDL_ScaleModeNearest);
#endif
    }
    return frame_texture;
}

static void upload_canvas(SDL_Texture *texture) {
    void *pixels;
    int pitch;
    if (SDL_LockTexture(texture, NULL, &pixels, &pitch) != 0) {
        return;
    }

    for (int y = 0; y < HIRES_FIELD_HEIGHT; y++) {
        uint32_t *destination = (uint32_t *)((uint8_t *)pixels + y * pitch);
        for (int x = 0; x < HIRES_FIELD_WIDTH; x++) {
            C2CanvasPixel colour = canvas[pixel_index(x, y)];
            destination[x] = ((uint32_t)colour.red << 24) | ((uint32_t)colour.green << 16)
                             | ((uint32_t)colour.blue << 8) | 0xff;
        }
    }
    SDL_UnlockTexture(texture);
}

void c2_render_frame(SDL_Renderer *renderer, const PhoenixState *state,
                     uint8_t scroll, uint8_t palette_bank) {
    SDL_Texture *texture = get_frame_texture(renderer);
    if (texture == NULL) {
        return;
    }

    memset(canvas, 0, sizeof(canvas));
    rasterize_tile_layer(state->BackgroundScreen, C2_HIRES_BACKGROUND_GLYPHS,
                         palette_bank, 0x00, scroll);
    scale_source_layer();
#if defined(C2_VARIANT_HIRES2) || defined(C2_VARIANT_HIRES2A) || defined(C2_VARIANT_HIRES3A)
    blend_colour_transitions();
#endif
#if defined(C2_VARIANT_HIRES3) || defined(C2_VARIANT_HIRES3A)
    apply_grain();
#endif
    composite_layer();
    rasterize_tile_layer(state->ForegroundScreen, C2_HIRES_FOREGROUND_GLYPHS,
                         palette_bank, 0x20, 0);
    scale_source_layer();
#if defined(C2_VARIANT_HIRES2) || defined(C2_VARIANT_HIRES2A) || defined(C2_VARIANT_HIRES3A)
    blend_colour_transitions();
#endif
#if defined(C2_VARIANT_HIRES3) || defined(C2_VARIANT_HIRES3A)
    apply_grain();
#endif
    composite_layer();
    upload_canvas(texture);

    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_NONE);
    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
    SDL_RenderClear(renderer);
    SDL_Rect destination = {0, 0, scale(FIELD_WIDTH), scale(FIELD_HEIGHT)};
    SDL_RenderCopy(renderer, texture, NULL, &destination);
    SDL_SetRenderDrawColor(renderer, 47, 94, 125, 255);
    SDL_Rect border = {0, 0, scale(FIELD_WIDTH) - 1, scale(FIELD_HEIGHT) - 1};
    SDL_RenderDrawRect(renderer, &border);
    SDL_RenderPresent(renderer);
}
