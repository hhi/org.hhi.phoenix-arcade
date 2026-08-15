#include <stdint.h>

#include "phoenix_state.h"

extern PhoenixState state;

/* [ASM: 00B6-00B7] Dead code: no callers in the original ROM. */
void l00b6(void) {}

/*
 * [ASM: 14E0-14FD]
 * Coin-check continuation of the slow-print path. It is centrally handled by
 * wait_vblank_coin in the C port, so this compatibility entry point is empty.
 */
void l14e0(void) {}

/*
 * [ASM: 1DF0-1DFF]
 * Anti-piracy check for the just-printed "AMSTAR" copyright text. On an
 * unmodified ROM it returns immediately; do not reduce this to a no-op.
 */
void l1df0(void) {
    uint8_t a = (uint8_t)(state.ForegroundScreen[0x31D] - 1);
    if (a == 0) return;
    state.CoinCount = a;
}
