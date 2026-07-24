#include "bird_logic.h"
#include "z80_core.h"
#include <stdint.h>
#include <stdbool.h>

extern PhoenixState state;

extern void draw_second_4_bird_objects(void);
extern void handle_animations_for_killed_aliens(void);
extern void refresh_bird_flight_parameters(void);
extern void update_second_four_birds(void);

/* [ASM: 3452-345B] Updates and renders bird structures 4-7. */
void update_second_bird_bank(void) {
    draw_second_4_bird_objects();
    refresh_bird_flight_parameters();
    update_second_four_birds();
    handle_animations_for_killed_aliens();
}

extern void drawNx2(uint16_t de, uint16_t screen_addr, uint16_t bc, int n);

// BM(off) reads relative to `base`; BM_SET writes. Both route through
// the bounds-checked mem_read/mem_write instead of raw pointer offsets.
#define BM(off) mem_read((uint16_t)(base + (off)))
#define BM_SET(off, val) mem_write((uint16_t)(base + (off)), (uint8_t)(val))

/*
 * Translates L3744 (from L3628 when the phase nibble hits 0)
 * Restart a climb phase: phase $11, step X back, reset the frame.
 * [ASM: 3744-3754]
 */
static void l3744_restart(uint16_t base) {
    BM_SET(6, 0x11);
    BM_SET(5, BM(5) - 1);
    BM_SET(3, 0x07);
    uint8_t old = BM(2);
    BM_SET(2, old + 0x20);
    if ((uint16_t)old + 0x20 > 0xFF) BM_SET(1, BM(1) + 1);
}

/*
 * Translates L3672 (descent target reached)
 * Aim the next descent at the player: new Y target at struct+7.
 * [ASM: 3672-3692]
 */
static void l3672_aim(uint16_t base) {
    uint8_t b = BM(5);
    uint8_t px = state.PlayerShipX & 0xF8;
    if (px < b) b = px;
    uint8_t c = state.M436D;
    state.M436D = (uint8_t)(c + 8);
    uint8_t a = (uint8_t)(b - c);
    BM_SET(7, 0x08);
    if (b < c) return;   // SUB borrow
    if (a < 0x08) return;
    BM_SET(7, a);
}

/*
 * Translates L3695 (climb completed a full row)
 * When the climb reached its target, aim a new descent target.
 * [ASM: 3695-36BB]
 */
static void l3695_aim_up(uint16_t base) {
    uint8_t b = BM(5);
    if (BM(7) != b) return;
    BM_SET(6, 0);
    uint8_t px = state.PlayerShipX & 0xF8;
    if (px >= b) b = px;
    uint8_t a = (uint8_t)(state.M436D + 8);
    state.M436D = a;
    uint16_t sum = a + b;
    BM_SET(7, 0xC8);
    if (sum > 0xFF) return;      // RET C from ADD
    if ((sum & 0xFF) >= 0xC8) return;
    BM_SET(7, (uint8_t)sum);
}

/*
 * Translates L3628 (phase >= $10: climbing)
 * Move the bird up-left; phase low nibble is the per-frame step.
 * [ASM: 3628-3666]
 */
static void l3628_climb(uint16_t base, uint8_t phase) {
    uint8_t b = phase & 0x0F;
    if (b == 0) { l3744_restart(base); return; }

    BM_SET(5, BM(5) - b);
    uint8_t old3 = BM(3);
    uint8_t a = (uint8_t)(old3 - b);
    BM_SET(3, a);
    if (old3 >= b) { l3695_aim_up(base); return; } // JP NC

    BM_SET(3, a & 0x07);
    uint8_t old2 = BM(2);
    BM_SET(2, old2 + 0x20);
    if ((uint16_t)old2 + 0x20 > 0xFF) BM_SET(1, BM(1) + 1);

    // 3648-3666: new phase from the distance still to climb
    a = (uint8_t)(BM(5) - BM(7));
    a = (uint8_t)((a >> 3) | (a << 5)) & 0x1F; // RRCA x3
    uint8_t carry = (a < b);
    a++;
    if (!carry) {
        uint8_t t = state.M436E;
        if (t == b) a = t;
        else a = (uint8_t)(b + 1);
    }
    BM_SET(6, a | 0x10);
}

/*
 * Translates L366A (descent step stalled at the top rows)
 * [ASM: 366A-3671]
 */
static void l366a_stall(uint16_t base, uint8_t b) {
    if (b != 0) return;
    BM_SET(6, BM(6) + 1);
}

/*
 * Translates L35E0 (phase < $10: descending)
 * Move the bird down-right by the phase value; on target, aim again.
 * [ASM: 35E0-3624]
 */
static void l35e0_descend(uint16_t base) {
    uint8_t phase = BM(6);
    if (phase >= 0x10) { l3628_climb(base, phase); return; }

    uint8_t b = phase;
    BM_SET(5, BM(5) + b);
    uint8_t a = (uint8_t)(b + BM(3));
    BM_SET(3, a);
    if (a < 0x08) { l366a_stall(base, b); return; }
    BM_SET(3, a & 0x07);

    // one screen row down: LSB -0x20 with borrow into the MSB
    uint8_t old2 = BM(2);
    BM_SET(2, old2 - 0x20);
    if (old2 < 0x20) BM_SET(1, BM(1) - 1);

    uint8_t c = BM(5);
    a = BM(7);
    BM_SET(6, 0x10);
    a = (uint8_t)(a - c);
    if (a == 0) { l3672_aim(base); return; }

    a--;
    a = (uint8_t)((a >> 3) | (a << 5)) & 0x1F; // RRCA x3
    uint8_t carry = (a < b);
    a++;
    BM_SET(6, a);
    if (carry) return;
    a = state.M436E;
    BM_SET(6, a);
    if (a == b) return;
    BM_SET(6, (uint8_t)(b + 1));
}

/*
 * Translates L36C0: advance the animation frame on even timer values.
 * [ASM: 36C0-36C9]
 */
static void l36c0_animate(uint16_t base) {
    if (BM(4) & 0x01) return;
    BM_SET(3, (uint8_t)(BM(3) + 1) & 0x07);
}

/*
 * Translates L36D2/L36EA/L370A: the growth/transform continuations.
 * When the timer expires (and for EA/0A the phase nibble is clear) the
 * bird becomes the next type with a new timer; L370A can additionally
 * roll a dive-transform gated by the random M436F.
 * L36D2-L36E6, L36EA-L3706 and L370A-L373E.
 */
/* [ASM: 36D2-36E6] */
static void l36d2_grow(uint16_t base, uint8_t d1h, uint8_t d2h) {
    if (BM(4) != 0) return;
    BM_SET(4, d1h);
    BM_SET(0, d2h);
    state.M4368 |= 0x01;
}

/* [ASM: 36EA-3706] */
static void l36ea_grow(uint16_t base, uint8_t d1h, uint8_t d2h) {
    if (BM(4) != 0) return;
    if (BM(6) & 0x0F) return;
    BM_SET(4, d1h);
    BM_SET(0, d2h);
    state.M4368 |= 0x02;
}

/* [ASM: 370A-373E] */
static void l370a_grow_or_dive(uint16_t base, uint8_t d1h, uint8_t d1l,
                               uint8_t d2h, uint8_t d2l) {
    if (BM(4) != 0) return;
    if (BM(6) & 0x0F) return;
    BM_SET(4, d1h);
    BM_SET(0, d2h);
    state.M4368 |= 0x04;
    // 3726-372C: random gate on the dive transform
    if (state.M436F & d2l & 0xF0) return;
    BM_SET(0, d2l & 0x0F);
    BM_SET(4, d1l);
    state.M4368 |= 0x08;
}

/*
 * Translates L35B0
 * Per-bird behaviour step. T3F00 holds, per bird type, two data words
 * and two routine addresses that the original chains together with
 * four PUSHes and a RET (a continuation trampoline): the second
 * address runs first, then control falls into the first address which
 * pops the data words as parameters.
 * [ASM: 35B0-35DB]
 */
void update_bird_behavior(uint16_t base) {
    uint8_t type = BM(0);
    if (type == 0) return;

    // 35B4-35BD: tick the type timer
    if (BM(4) != 0) BM_SET(4, BM(4) - 1);

    extern const uint8_t phoenix_bird_behaviour_scripts[0x80];
    uint16_t tab = type * 8;
    uint8_t d1h = phoenix_bird_behaviour_scripts[tab];
    uint8_t d1l = phoenix_bird_behaviour_scripts[tab + 1];
    uint8_t d2h = phoenix_bird_behaviour_scripts[tab + 2];
    uint8_t d2l = phoenix_bird_behaviour_scripts[tab + 3];
    uint16_t a1 = (phoenix_bird_behaviour_scripts[tab + 4] << 8)
                | phoenix_bird_behaviour_scripts[tab + 5];
    uint16_t a2 = (phoenix_bird_behaviour_scripts[tab + 6] << 8)
                | phoenix_bird_behaviour_scripts[tab + 7];

    // second address runs first
    if (a2 == 0x35E0) l35e0_descend(base);
    else if (a2 == 0x36C0) l36c0_animate(base);

    // then the continuation with the data words
    if (a1 == 0x36D2) l36d2_grow(base, d1h, d2h);
    else if (a1 == 0x36EA) l36ea_grow(base, d1h, d2h);
    else if (a1 == 0x370A) l370a_grow_or_dive(base, d1h, d1l, d2h, d2l);
    // 0x36CC: no continuation
}

/*
 * Translates L3498: updates bird structures 0-3.
 * [ASM: 3498-34A9]
 */
void update_first_four_birds(void) {
    for (uint16_t hl = 0x4B70; hl < 0x4B90; hl += 8) {
        update_bird_behavior(hl);
    }
}

/*
 * Translates L34AA: updates bird structures 4-7.
 * [ASM: 34AA-34BB]
 */
void update_second_four_birds(void) {
    for (uint16_t hl = 0x4B90; hl < 0x4BB0; hl += 8) {
        update_bird_behavior(hl);
    }
}

extern uint8_t get_random_number(void);

/* [ASM: 3560-359F] Refreshes shared flight parameters for the bird wave. */
void refresh_bird_flight_parameters(void) {
    uint8_t a = get_random_number();
    uint8_t b = a;
    a <<= 2;
    uint8_t c = a;
    a <<= 2;
    a |= b;
    state.M436F = a;
    
    a = state.LevelAndRound;
    if (a >= 0x40) {
        a = 0x30;
    }
    a &= 0x30;
    a >>= 1;
    b = a;
    
    a = state.BirdsLeft - 1;
    if (a >= 4) {
        a = 3;
    }
    a <<= 1;
    a |= b;
    b = a;
    
    a = state.Counter9A;
    a <<= 2;
    a &= 0x20;
    a |= b;
    a += 0x80;
    
    extern const uint8_t phoenix_bird_formation_params[0x40];
    uint8_t param_idx = (uint8_t)(a - 0x80);
    state.M436E = phoenix_bird_formation_params[param_idx];
    param_idx++;
    a = phoenix_bird_formation_params[param_idx];
    a += c;
    a &= 0xF8;
    state.M436D = a;
}

/* [ASM: 3A00-3A0F] */
static bool l3a00(uint8_t* out_d) {
    uint8_t a = state.BirdsLeft;
    a -= 0x0C;
    a = (~a) + 1;
    *out_d = a;
    
    a = state.Counter9B; // 439B
    if (a & 0x02) {
        return true; 
    }
    return false;
}

/*
 * Translates L395C
 * Tests one bird as a dive-bomb candidate. Returns false to let the
 * caller's loop continue trying the next bird; returns true once a
 * candidate passes and L25B7 is reached -- in the original this is a
 * tail jump whose double POP unconditionally aborts all the way back
 * to try_spawn_bird_dive_bomb's own caller, whether or not L25B7 actually found
 * a free bullet slot.
 */
/*
 * [ASM: 395C-397B]
 */
static bool l395c(uint16_t* hl_ptr, uint8_t b, uint8_t c) {
    uint16_t hl = *hl_ptr;

    uint8_t a = mem_read(hl);
    if (a < 5) return false;

    hl += 5;
    a = mem_read(hl);
    if (a < b) return false;
    if (a >= c) return false;

    a -= 4;
    b = a;
    hl -= 3;

    a = (uint8_t)(state.B4BD2 + mem_read(hl));
    a &= 0x1F;
    a <<= 3;
    a += 8;
    c = a;

    extern void l25b7(uint8_t b, uint8_t c);
    l25b7(b, c);
    return true;
}

/* [ASM: 3930-395B] Attempts to allocate one bird dive-bomb. */
void try_spawn_bird_dive_bomb(void) {
    uint8_t a = state.B4BD2 & 0x1E;
    extern const uint8_t phoenix_bird_dive_spawn_positions[0x20];

    uint8_t e = phoenix_bird_dive_spawn_positions[a];
    uint8_t l = phoenix_bird_dive_spawn_positions[a + 1];
    uint8_t h = 0x4B;
    uint16_t hl = (h << 8) | l;
    
    uint8_t d;
    if (!l3a00(&d)) {
        return; 
    }
    
    a = state.M439F + d;
    uint8_t c = a;
    
    a = state.M439E - d;
    uint8_t b = a;
    
    while (e != 0) {
        if (l395c(&hl, b, c)) return; // L25B7 always ends the search
        hl += 8;
        e--;
    }
}

/*
 * Translates L3980
 * Low-flying bird versus player: when the bird layer scroll (B4BD2) is
 * in the low band, park the real bullet struct and sweep a fake bullet
 * across the player ship, reusing the bird collision test. A hit kills
 * the player (or drains the shield).
 * [ASM: 3980-39FD]
 */
void check_bird_formation_player_collision(void) {
    uint8_t a = state.B4BD2;
    if (a < 0x0C || (uint8_t)(a - 0x0C) >= 0x10) return;

    // 3989-39A7: save the bullet struct, aim a fake bullet at the ship
    state.B4BC0 = state.PlayerBulletState;
    state.B4BC1 = state.PlayerBulletShape;
    state.B4BC2 = state.PlayerBulletX;
    state.B4BC3 = state.PlayerBulletY;
    state.B4BC4 = state.PlayerBulletMSB;
    state.B4BC5 = state.PlayerBulletLSB;
    state.PlayerBulletMSB = state.PlayerShipMSB;
    state.PlayerBulletLSB = state.PlayerShipLSB;
    state.PlayerBulletState = 0x08;

    // 39A9-39C0: odd frames test the ship's left edge, even frames the
    // right edge one column back
    uint16_t de = 0x439E;
    if ((state.Counter9B & 0x01) == 0) {
        de++;
        uint16_t scr = (uint16_t)(((state.PlayerBulletMSB << 8)
                                   | state.PlayerBulletLSB) - 0x20);
        state.PlayerBulletMSB = scr >> 8;
        state.PlayerBulletLSB = scr & 0xFF;
    }
    state.PlayerBulletX = mem_read(de);

    extern void collision_detection_for_birds(void);
    // 39C3-39D8: walk the test cell down the ship rows
    while (1) {
        collision_detection_for_birds();
        if ((state.PlayerBulletState & 0x08) == 0) {
            // L39F0: a bird occupies the cell -> it hit the player
            if (state.ShieldCount < 0xC0) {
                extern void l0cc4_player_killed(void);
                l0cc4_player_killed();
                return; // JP $0CC4 -- no restore on a kill
            }
            state.ShieldCount--;
            break; // JP L39DB
        }
        state.PlayerBulletLSB++;
        if ((state.PlayerBulletLSB & 0x1F) >= 0x1D) break;
    }

    // L39DB: restore the real bullet struct
    state.PlayerBulletState = state.B4BC0;
    state.PlayerBulletShape = state.B4BC1;
    state.PlayerBulletX = state.B4BC2;
    state.PlayerBulletY = state.B4BC3;
    state.PlayerBulletMSB = state.B4BC4;
    state.PlayerBulletLSB = state.B4BC5;
}
