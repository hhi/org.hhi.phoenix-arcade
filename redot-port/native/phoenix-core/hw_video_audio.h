#ifndef HW_VIDEO_AUDIO_H
#define HW_VIDEO_AUDIO_H

#include "phoenix_state.h"

void phoenix_main_loop(void); // Reset vector 0x0000
void phoenix_redot_step(void);
void vblank_nmi_interrupt(void); // 0x0066
void clear_background(void);
void render_sprites(void);
void update_audio_registers(void);

#endif // HW_VIDEO_AUDIO_H
