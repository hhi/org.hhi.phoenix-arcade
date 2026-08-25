#include "redot_c2_renderer.h"
#include "phoenix_state.h"
#include "../../../c-phoenix/phoenix_render_assets.h"
#include <string.h>

extern PhoenixState state;
extern uint8_t phoenix_redot_palette_bank(void);
extern uint8_t phoenix_redot_scroll_register(void);

enum { W = 208, H = 256, HW = 416, HH = 512, PIXELS = W * H, HPIXELS = HW * HH };
typedef struct { uint8_t red, green, blue; } Pixel;

static Pixel canvas[HPIXELS], source[PIXELS], layer[HPIXELS], blended[HPIXELS];
static uint8_t source_mask[PIXELS], layer_mask[HPIXELS];

static int source_index(int x, int y) { return (y & 255) * W + x; }
static int layer_index(int x, int y) { return y * HW + x; }
static int source_visible(int x, int y) { return x >= 0 && x < W && source_mask[source_index(x, y)]; }
static int layer_visible(int x, int y) { return x >= 0 && x < HW && y >= 0 && y < HH && layer_mask[layer_index(x, y)]; }
static Pixel black(void) { Pixel pixel = {0, 0, 0}; return pixel; }
static Pixel source_pixel(int x, int y) { return source_visible(x, y) ? source[source_index(x, y)] : black(); }

static int same_source(int ax, int ay, int bx, int by) {
    Pixel a, b;
    if (source_visible(ax, ay) != source_visible(bx, by)) return 0;
    if (!source_visible(ax, ay)) return 1;
    a = source_pixel(ax, ay); b = source_pixel(bx, by);
    return a.red == b.red && a.green == b.green && a.blue == b.blue;
}

static void rasterize(const uint8_t *screen, const uint8_t tiles[256][64], uint8_t foreground, uint8_t scroll) {
    memset(source_mask, 0, sizeof(source_mask));
    for (int column = 0; column < 26; column++) for (int row = 0; row < 32; row++) {
        uint8_t tile = screen[column * 32 + row];
        if (!tile) continue;
        for (int ty = 0; ty < 8; ty++) for (int tx = 0; tx < 8; tx++) {
            uint8_t colour_index = tiles[tile][ty * 8 + tx];
            if (!colour_index) continue;
            uint8_t prom = (uint8_t)((phoenix_redot_palette_bank() << 6) | foreground
                | (colour_index << 3) | ((tile >> 5) & 7));
            int x = (25 - column) * 8 + (7 - ty);
            int y = (row * 8 + (foreground ? 0 : 256 - scroll) + (7 - tx)) & 255;
            PhoenixRgb colour = phoenix_palette_rgb[prom & 0x7f];
            source[source_index(x, y)] = (Pixel){colour.red, colour.green, colour.blue};
            source_mask[source_index(x, y)] = 1;
        }
    }
}

static void scale2x(void) {
    memset(layer_mask, 0, sizeof(layer_mask));
    for (int y = 0; y < H; y++) for (int x = 0; x < W; x++) {
        Pixel e = source_pixel(x, y), d = source_pixel(x - 1, y), f = source_pixel(x + 1, y);
        Pixel output[4] = {e, e, e, e};
        uint8_t mask[4] = {source_visible(x, y), source_visible(x, y), source_visible(x, y), source_visible(x, y)};
        if (source_visible(x, y) && !same_source(x, y - 1, x, y + 1) && !same_source(x - 1, y, x + 1, y)) {
            if (same_source(x - 1, y, x, y - 1) && !same_source(x - 1, y, x, y + 1) && !same_source(x, y - 1, x + 1, y)) { output[0] = d; mask[0] = source_visible(x - 1, y); }
            if (same_source(x, y - 1, x + 1, y) && !same_source(x, y - 1, x - 1, y) && !same_source(x + 1, y, x, y + 1)) { output[1] = f; mask[1] = source_visible(x + 1, y); }
            if (same_source(x - 1, y, x, y + 1) && !same_source(x - 1, y, x, y - 1) && !same_source(x, y + 1, x + 1, y)) { output[2] = d; mask[2] = source_visible(x - 1, y); }
            if (same_source(x, y + 1, x + 1, y) && !same_source(x, y + 1, x - 1, y) && !same_source(x + 1, y, x, y - 1)) { output[3] = f; mask[3] = source_visible(x + 1, y); }
        }
        for (int oy = 0; oy < 2; oy++) for (int ox = 0; ox < 2; ox++) {
            int index = layer_index(x * 2 + ox, y * 2 + oy);
            layer[index] = output[oy * 2 + ox]; layer_mask[index] = mask[oy * 2 + ox];
        }
    }
}

static int same_layer(int ax, int ay, int bx, int by) {
    if (!layer_visible(ax, ay) || !layer_visible(bx, by)) return 0;
    Pixel a = layer[layer_index(ax, ay)], b = layer[layer_index(bx, by)];
    return a.red == b.red && a.green == b.green && a.blue == b.blue;
}

static void blend_colours(void) {
    static const int offsets[8][2] = {{1,0},{-1,0},{0,1},{0,-1},{1,1},{1,-1},{-1,1},{-1,-1}};
    for (int pass = 0; pass < 2; pass++) {
        memcpy(blended, layer, sizeof(blended));
        for (int y = 0; y < HH; y++) for (int x = 0; x < HW; x++) {
            if (!layer_visible(x, y)) continue;
            Pixel centre = layer[layer_index(x, y)]; long red = centre.red, green = centre.green, blue = centre.blue; int samples = 1;
            for (int n = 0; n < 8; n++) { int nx = x + offsets[n][0], ny = y + offsets[n][1]; if (!layer_visible(nx, ny) || same_layer(x, y, nx, ny)) continue; Pixel neighbour = layer[layer_index(nx, ny)]; red += neighbour.red; green += neighbour.green; blue += neighbour.blue; samples++; }
            blended[layer_index(x, y)] = (Pixel){(uint8_t)(red / samples), (uint8_t)(green / samples), (uint8_t)(blue / samples)};
        }
        memcpy(layer, blended, sizeof(layer));
    }
}

static uint32_t grain_hash(int x, int y, int channel) { uint32_t h = (uint32_t)x * 374761393u + (uint32_t)y * 668265263u + (uint32_t)channel * 2654435761u; h = (h ^ (h >> 13)) * 1274126177u; return h ^ (h >> 16); }
static uint8_t grain(uint8_t value, int x, int y, int channel) { int result = value + (int)(grain_hash(x, y, channel) % 13) - 6; return (uint8_t)(result < 0 ? 0 : result > 255 ? 255 : result); }
static void apply_grain(void) { for (int y = 0; y < HH; y++) for (int x = 0; x < HW; x++) if (layer_visible(x, y)) { Pixel *pixel = &layer[layer_index(x, y)]; pixel->red = grain(pixel->red, x, y, 0); pixel->green = grain(pixel->green, x, y, 1); pixel->blue = grain(pixel->blue, x, y, 2); } }

static uint8_t contour_alpha(int x, int y) {
    int left = !layer_visible(x - 1, y), right = !layer_visible(x + 1, y), top = !layer_visible(x, y - 1), bottom = !layer_visible(x, y + 1);
    if (!(x & 1) && !(y & 1) && left && top && !layer_visible(x - 1, y - 1)) return 160;
    if ((x & 1) && !(y & 1) && right && top && !layer_visible(x + 1, y - 1)) return 160;
    if (!(x & 1) && (y & 1) && left && bottom && !layer_visible(x - 1, y + 1)) return 160;
    if ((x & 1) && (y & 1) && right && bottom && !layer_visible(x + 1, y + 1)) return 160;
    return 255;
}

static void composite(void) {
    for (int index = 0; index < HPIXELS; index++) if (layer_mask[index]) { uint8_t alpha = contour_alpha(index % HW, index / HW); canvas[index].red = (uint8_t)((layer[index].red * alpha + canvas[index].red * (255 - alpha) + 127) / 255); canvas[index].green = (uint8_t)((layer[index].green * alpha + canvas[index].green * (255 - alpha) + 127) / 255); canvas[index].blue = (uint8_t)((layer[index].blue * alpha + canvas[index].blue * (255 - alpha) + 127) / 255); }
}

void phoenix_redot_c2_frame_rgba(uint8_t *out, uint32_t length) {
    if (!out || length < HPIXELS * 4u) return;
    memset(canvas, 0, sizeof(canvas));
    rasterize(state.BackgroundScreen, phoenix_background_tiles, 0, phoenix_redot_scroll_register()); scale2x(); blend_colours(); apply_grain(); composite();
    rasterize(state.ForegroundScreen, phoenix_foreground_tiles, 0x20, 0); scale2x(); blend_colours(); apply_grain(); composite();
    for (int index = 0; index < HPIXELS; index++) { out[index * 4] = canvas[index].red; out[index * 4 + 1] = canvas[index].green; out[index * 4 + 2] = canvas[index].blue; out[index * 4 + 3] = 255; }
}
