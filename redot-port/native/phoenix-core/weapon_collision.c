#include "weapon_collision.h"
#include "phoenix_hw.h"
#include "z80_core.h"
#include "coverage.h"
#include "game_constants.h"
#include "phoenix_tables.h"
#include <stdint.h>

extern void l0e10(uint16_t bc, uint16_t hl);

extern PhoenixState state;

extern void update_screen_objects(uint16_t state_addr, uint16_t screen_ram_addr);
extern void get_screen_ram_address(uint16_t state_addr, uint16_t screen_ram_addr);

/*
 * Translates L096E
 * Clears the bullet state (deletes bit 3).
 * [ASM: 096E-0975]
 */
static void l096e_clear_bullet(uint16_t bullet_state_addr) {
    mem_write(bullet_state_addr, mem_read(bullet_state_addr) & 0xF7);
}

/*
 * Translates L0CB4
 * The player ship was hit by an enemy bullet.
 * [ASM: 0CB4-0CD4]
 */
static void l0cb4_check_bullet_hit_player(uint16_t bullet_x_offset) {
    uint8_t y = mem_read(bullet_x_offset + 1); // y is at offset + 1

    if (y < 0xDC) return; // not reached lower part of screen
    if (y >= 0xE9) return;

    uint8_t x = mem_read(bullet_x_offset);
    if (state.M439F < x) return; // Right mapped bound
    if (state.M439E >= x) return; // Left mapped bound
    
    // Player hit! (L0CC4)
    coverage_hit("enemy_bullet_hit_player");
    extern void l0cc4_player_killed(void);
    l0cc4_player_killed();
}

/*
 * Translates L0CC4
 * Player killed.
 * [ASM: 0CC4-0CD3]
 */
void l0cc4_player_killed(void) {
    coverage_hit("player_killed");
    state.GameState = GAME_STATE_PLAYER_EXPLODING;
    state.CounterA5 = PLAYER_EXPLOSION_INITIAL_DURATION;
    state.ParticleExplosion = 0x10;
}

/*
 * Translates L0C84
 * Movement and animation of enemy bullet.
 * [ASM: 0C84-0CB3]
 */
void l0c84_enemy_bullet_movement(uint16_t bullet_state_addr) {
    coverage_hit("enemy_bullet_movement");
    uint16_t base = bullet_state_addr;

    if ((mem_read(base) & 0x08) == 0) {
        return; // Inactive
    }

    // Toggle shape animation
    mem_write(base + 1, mem_read(base + 1) ^ 0x04);

    // Move bullet down
    mem_write(base + 3, mem_read(base + 3) + 0x04);

    if (mem_read(base + 3) >= 0xF9) {
        l096e_clear_bullet(bullet_state_addr);
        return;
    }

    // Check hit player
    l0cb4_check_bullet_hit_player(bullet_state_addr + 2);

    // Check hit player shield
    uint16_t msb_addr = (bullet_state_addr + 2) + 0x20;
    uint8_t msb = mem_read(msb_addr);
    uint8_t lsb = mem_read(msb_addr + 1);
    uint16_t screen_ram_addr = (msb << 8) | lsb;

    if (screen_ram_addr >= 0x4000 && screen_ram_addr < 0x4400) {
        uint8_t tile = mem_read(screen_ram_addr);
        if (tile >= 0xE8) {
            l096e_clear_bullet(bullet_state_addr);
            return;
        }
    }
}

static void copy_current_to_old_enemy_bullet_data(void) {
    state.OldEnemyBullet4LSB = state.EnemyBullet4LSB;
    state.OldEnemyBullet4MSB = state.EnemyBullet4MSB;
    state.OldEnemyBullet3LSB = state.EnemyBullet3LSB;
    state.OldEnemyBullet3MSB = state.EnemyBullet3MSB;
    state.OldEnemyBullet2LSB = state.EnemyBullet2LSB;
    state.OldEnemyBullet2MSB = state.EnemyBullet2MSB;
    state.OldEnemyBullet1LSB = state.EnemyBullet1LSB;
    state.OldEnemyBullet1MSB = state.EnemyBullet1MSB;
    state.OldEnemyBullet0LSB = state.EnemyBullet0LSB;
    state.OldEnemyBullet0MSB = state.EnemyBullet0MSB;
}

/*
 * Translates L0C56
 * Enemy bullets movement and animation.
 * Handles all 5 bullet slots.
 * [ASM: 0C56-0C67]
 */
static void enemy_bullet_movement_and_animation(void) {
    uint16_t bc = 0x43CC; // EnemyBullet0State
    for (int i = 0; i < 5; i++) {
        l0c84_enemy_bullet_movement(bc);
        bc += 4;
    }
}

/*
 * Translates L0C6B
 * Get the screen ram address for all enemy bullets.
 * [ASM: 0C6B-0C80]
 */
static void get_screen_ram_address_for_enemy_bullets(void) {
    uint16_t bc = 0x43CE; // EnemyBullet0X
    uint16_t de = 0x43EE; // EnemyBullet0MSB
    for (int i = 0; i < 5; i++) {
        get_screen_ram_address(bc, de);
        bc += 4;
        de += 4;
    }
}

/*
 * Translates EnemyBulletDataController
 * Handle enemy bullet control states for 5 bullet slots,
 * and draw or delete the screen object.
 * [ASM: 0CD8-0CEF]
 */
static void enemy_bullet_data_controller(void) {
    uint16_t bc = 0x43CC; // EnemyBullet0State
    uint16_t de = 0x43EC; // OldEnemyBullet0MSB
    for (int i = 0; i < 5; i++) {
        update_screen_objects(bc, de);
        bc += 4;
        de += 4;
    }
}

/*
 * Translates L0C40
 * Updates the enemy bullets.
 * [ASM: 0C40-0C51]
 */
void process_enemy_bombs(void) {
    coverage_hit("process_enemy_bombs");
    copy_current_to_old_enemy_bullet_data(); // 088B
    enemy_bullet_movement_and_animation();   // 0C56
    get_screen_ram_address_for_enemy_bullets(); // 0C6B
    enemy_bullet_data_controller();          // 0CD8
}

extern void l0f56_alien_with_player_ship_collision(void);

void check_player_ship_collision(void) {
    // Calls L0F00: Alien with player collision check
    extern void l0f00_check_alien_with_player_collision(void);
    l0f00_check_alien_with_player_collision();
}

// l0cf4 (L0CF4, $0CF4-0CF6: POP DE/POP BC/RET) was een dode
// duplicaat-stub; verwijderd 11 juli 2026. De $0FC0-0FFD-range
// (L0FC0, 'player destroyed'-animaties) leeft als
// handle_animations_for_killed_aliens in alien_logic.c.

/*
 * Translates L0DF0
 * Enemy bullet to player ship, collision detection.
 * [ASM: 0DF0-0E01]
 */
void check_enemy_bullet_to_player_collision(void) {
    coverage_hit("check_enemy_bullet_to_player_collision");
    l0e10(0x43C4, 0x43E6);
    l0e10(0x43C8, 0x43EA);
}

/*
 * Translates unused code block
 * [ASM: 0E02-0E0B]
 */
void l0e02_unused(void) {
    l0e10(0x43CC, 0x43EE);
}
/*
 * Translates L0C00
 * Score for killing an out-of-formation alien: 040 normally, 200 (plus
 * the bonus explosion flag) when its movement pattern is in step 7-8
 * (the dive right above the player).
 * [ASM: 0C00-0C23]
 */
static uint16_t l0c00_kill_score(uint16_t alien_x_addr) {
    uint8_t l = (uint8_t)(((uint8_t)((alien_x_addr & 0xFF) - 0x72) >> 1) + 0x50);
    uint16_t pat = (mem_read(0x4B00 | l) << 8)
                 | mem_read(0x4B00 | (uint8_t)(l + 1));
    uint8_t v = phoenix_alien_movement_byte(pat);
    if (v >= 7 && v < 9) {
        state.M4369 = 0xFF;
        return 0x1020; // bonus explosion, score 200
    }
    return 0x0C04; // score 040
}

/*
 * Translates L0E10
 * Player bullet (or the cell above it) versus alien collision. The
 * screen character above the bullet routes to the in-formation window
 * test (T1740) or the out-of-formation box test.
 * [ASM: 0E10-0E36] [ASM: 0E39-0E6B] [ASM: 0E58-0E6B] [ASM: 0E70-0EA0]
 */
void l0e10(uint16_t bc, uint16_t hl) {
    coverage_hit("player_bullet_collision_scan");
    extern void l0ea4_with_score(uint16_t, uint16_t, uint16_t);

    // 0E10-0E13: bullet must be active
    if ((mem_read(bc) & 0x08) == 0) return;

    // 0E14-0E17: character at the tracked screen cell. An out-of-range de
    // reads as 0 via mem_read, which the chr<0x60 check just below
    // rejects the same way the old explicit range guard did.
    uint16_t de = (mem_read(hl) << 8) | mem_read(hl + 1);
    uint8_t chr = mem_read(de);

    // 0E18-0E1D: only alien tiles $60-$BF
    if (chr >= 0xC0 || chr < 0x60) return;

    if (chr >= 0x68) {
        // L0E39: alien out of formation. D = bullet X, E = bullet Y & F8
        uint8_t d = mem_read(bc + 2);
        uint8_t e = mem_read(bc + 3) & 0xF8;

        for (uint16_t a = 0x4B70; a < 0x4BB0; a += 4) {
            if ((mem_read(a) & 0x08) == 0) continue;
            uint8_t ax = mem_read(a + 2);
            // 0E58-0E5F: alien_x <= D <= alien_x + 8
            if (d < ax) continue;
            if ((uint8_t)(ax + 8) < d) continue;
            uint8_t ay = mem_read(a + 3);
            // 0E60-0E6A: alien_y - 8 < E <= alien_y + 4
            if ((uint8_t)(ay + 4) < e) continue;
            if ((uint8_t)(ay - 8) >= e) continue;
            // 0E6B: JP L0C00, falls through into L0EA4
            l0ea4_with_score(l0c00_kill_score(a + 2), a + 2, bc + 3);
            return;
        }
        return;
    }

    // 0E23-0E35: in formation, hit window from T1740 (4 bytes per tile)
    uint8_t tp = (chr & 0x07) * 4;
    uint8_t x7 = mem_read(bc + 2) & 0x07;
    if (x7 >= phoenix_formation_hit_window[tp]) return;
    if (x7 < phoenix_formation_hit_window[tp + 1]) return;

    // L0E70: D = (bullet X & F8) + 3rd table byte, E = bullet Y & F8
    uint8_t dv = (uint8_t)((mem_read(bc + 2) & 0xF8) + phoenix_formation_hit_window[tp + 2]);
    uint8_t ev = mem_read(bc + 3) & 0xF8;

    for (uint16_t a = 0x4B70; a < 0x4BB0; a += 4) {
        if ((mem_read(a) & 0x08) == 0) continue;
        uint8_t ax = mem_read(a + 2);
        // 0E90-0E98: alien_x - 3 < D <= alien_x + 2
        if ((uint8_t)(ax + 2) < dv) continue;
        if ((uint8_t)(ax - 3) >= dv) continue;
        uint8_t ay = mem_read(a + 3);
        // 0E99-0E9F: same 8-pixel row
        if ((ay & 0xF8) != ev) continue;
        // 0EA0: score 020
        l0ea4_with_score(0x0C02, a + 2, bc + 3);
        return;
    }
}

/*
 * Translates L0EA4
 * Registers an alien kill by updating bullet/alien states and scoring.
 * [ASM: 0EA4-0EE5]
 */
void l0ea4_with_score(uint16_t score, uint16_t hl, uint16_t bc) {
    coverage_hit("alien_killed_with_score");
    // DEC HL x2 -> hl_alien
    hl -= 2;

    // L0EA4 entry: DEC BC x3 -> PlayerBulletState, clear its active bit.
    // Callers that enter at L0EAD (alien-vs-player collision, no bullet)
    // pass bc=0 and must skip this write.
    if (bc >= 0x4003) {
        bc -= 3;
        mem_write(bc, mem_read(bc) & 0xF7);
    }

    // L0EAD: AlienState &= 0xF7
    mem_write(hl, mem_read(hl) & 0xF7);

    // 0EB1-0EB7: A=L; ADD $42 -- stays in the $4B page: the alien's
    // screen RAM address entry at $4BB2 + alien*4
    uint16_t alien_msb_addr = 0x4B00 | (uint8_t)((hl & 0xFF) + 0x42);
    uint8_t msb = mem_read(alien_msb_addr);
    uint8_t lsb = mem_read(alien_msb_addr + 1);

    uint16_t counter_ptr = 0x4378; // Animation counter for the bonus explosion
    if ((score >> 8) != 0x10) {
        counter_ptr = 0x4370; // Different explosion array
    }

    if (mem_read(counter_ptr) != 0) {
        counter_ptr += 4;
        if (mem_read(counter_ptr) != 0) {
            counter_ptr += 4;
        }
    }

    uint8_t d = score >> 8;
    uint8_t e = score & 0xFF;

    mem_write(counter_ptr, d);
    mem_write(counter_ptr + 1, e); // score
    mem_write(counter_ptr + 2, msb);
    mem_write(counter_ptr + 3, lsb);

    state.M4364 = 0xFF; // Set flag
    state.AliensLeft--; // Decrement aliens left
}

/*
 * Translates L0F56
 * Screen RAM collision check
 * [ASM: 0F56-0F71]
 */
uint8_t l0f56_screen_ram_collision(uint8_t screen_high_byte, uint8_t screen_low_byte,
                                    uint8_t width_in_tiles, uint8_t height_in_tiles) {
    uint16_t row_start_address = (uint16_t)((screen_high_byte << 8) | screen_low_byte);
    for (int row_index = 0; row_index < height_in_tiles; row_index++) {
        uint16_t tile_address = row_start_address;
        for (int column_index = 0; column_index < width_in_tiles; column_index++) {
            if (tile_address >= 0x4000 && tile_address < 0x4400) {
                uint8_t tile = mem_read(tile_address);
                if (tile >= 0x60 && tile < 0xC0) {
                    return 1; // Collision
                }
            }
            tile_address++; // INC DE
        }
        // 0F6A: CALL RightOneColumn ($0217) on the restored row start:
        // DE -= 0x20, the next row of the rotated screen. (A previous
        // version did `d++`, i.e. DE += 0x100 -- off-screen, silently
        // swallowed by the bounds guard, so rows past the first were
        // never scanned. Found via scripted lockstep vs jphoenix.)
        row_start_address -= 0x20;
    }
    return 0; // No collision
}

/*
 * Translates L0F00
 * Alien with player collision check
 * [ASM: 0F00-0F33] and [ASM: 0F38-0F4E] and [ASM: 0F74-0FB9]
 */
void l0f00_check_alien_with_player_collision(void) {
    coverage_hit("alien_with_player_collision_scan");
    // NB: geen 436C/436D-guards -- de asm (L0F00 zelf en zijn callers
    // L2150/L2190) heeft die niet; een eerdere versie sloeg hierdoor de
    // hele check over zodra M436D (vogel-scrollpositie) niet-nul was.

    if (state.ShieldCount >= 0xC0) {
        // Shield active (L0F74)
        // 0F79-0F7C: CALL RightOneColumn; DEC DE -- the 4x4 shield window
        // starts one screen row right and one tile up from the ship's
        // screen address.
        uint16_t de16 = (uint16_t)(((state.PlayerShipMSB << 8) | state.PlayerShipLSB) - 0x21);
        uint8_t d = (uint8_t)(de16 >> 8);
        uint8_t e = (uint8_t)de16;

        if (l0f56_screen_ram_collision(d, e, 4, 4)) {
            // Check bounding box
            uint8_t pb_x = state.PlayerShipX;
            uint8_t min_x = pb_x - 0x0E;
            uint8_t max_x = min_x + 0x2D;

            uint16_t hl = 0x4B70;
            for (int i = 0; i < 16; i++) {
                if (mem_read(hl) & 0x08) {
                    uint8_t alien_y = mem_read(hl + 3);
                    if (alien_y >= 0xCA && alien_y < 0xEF) {
                        uint8_t alien_x = mem_read(hl + 2);
                        if (alien_x >= min_x && alien_x < max_x) {
                            // Kill alien, no player kill
                            coverage_hit("shield_killed_alien");
                            extern void l0ea4_with_score(uint16_t, uint16_t, uint16_t);
                            l0ea4_with_score(0x0D02, hl + 2, 0); // BC is ignored if it's < 0x4000
                            return;
                        }
                    }
                }
                hl += 4;
            }
        }
        return;
    }

    // Shield not active (L0F09)
    uint8_t d = state.PlayerShipMSB;
    uint8_t e = state.PlayerShipLSB;

    if (l0f56_screen_ram_collision(d, e, 2, 2)) {
        // L0F17
        uint8_t mapped_x = state.M439E - 0x06;
        uint8_t min_x = mapped_x;
        uint8_t max_x = state.M439F;

        uint16_t hl = 0x4B70;
        for (int i = 0; i < 16; i++) {
            if (mem_read(hl) & 0x08) {
                uint8_t alien_y = mem_read(hl + 3);
                if (alien_y >= 0xD2 && alien_y < 0xE7) {
                    uint8_t alien_x = mem_read(hl + 2);
                    if (alien_x >= min_x && alien_x < max_x) {
                        // Kill player
                        coverage_hit("alien_hit_player");
                        extern void l0cc4_player_killed(void);
                        l0cc4_player_killed();

                        // Kill alien
                        extern void l0ea4_with_score(uint16_t, uint16_t, uint16_t);
                        l0ea4_with_score(0x0D04, hl + 2, 0);
                        return;
                    }
                }
            }
            hl += 4;
        }
    }
}
