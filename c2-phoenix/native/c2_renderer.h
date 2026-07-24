#ifndef C2_RENDERER_H
#define C2_RENDERER_H

#include <SDL2/SDL.h>
#include <stdint.h>

#include "phoenix_state.h"

/* Render original Phoenix sprites with the current hardware video registers. */
void c2_render_frame(SDL_Renderer *renderer, const PhoenixState *state,
                     uint8_t scroll, uint8_t palette_bank);

#endif
