#ifndef PHOENIX_REDOT_C2_RENDERER_H
#define PHOENIX_REDOT_C2_RENDERER_H

#include <stdint.h>

/* Rasterises the C2 hires3a presentation into a 416x512 RGBA8888 buffer. */
void phoenix_redot_c2_frame_rgba(uint8_t *out, uint32_t length);

#endif
