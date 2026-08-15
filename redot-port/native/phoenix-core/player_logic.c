#include "player_logic.h"
#include "coverage.h"
#include "game_constants.h"
#include "phoenix_hw.h"
#include "phoenix_tables.h"

extern PhoenixState state;

// Hardware table (using extern since it's defined in the original ROM)
extern const uint8_t T1600[];

// Stubs for external logic routines
extern void player_data_controller(void); // L0700
extern void get_screen_ram_address_for_player_ship(void); // L09A0
extern void map_player_ship_position(void); // L097A
extern void draw_shields(void); // L0AA0
extern void update_player_bullet_y(uint8_t* bullet_state_ptr); // L0964
extern void spawn_player_bullet(uint8_t* bullet_state_ptr); // L093D
extern void get_player_ship_animation_frame_values(uint16_t bc, uint8_t* ptr_x); // L0926

/*
 * Game state 4 (already translated in state_endings.c, but this module covers the 
 * player core routines during normal gameplay).
 */

// Forward declarations
void move_player(void);
void get_assigned_player_bullet_tile(uint8_t* bullet_state_ptr);

/*
 * Translates L0876
 * Updates the player ship, player bullet and the shield.
 * [ASM: 0876-0885]
 */
void player_update(void) {
    coverage_hit("player_update");
    player_data_controller();
    copy_current_to_old_player_data();
    update_player_position_bullet_shield();
    get_screen_ram_address_for_player_ship();
    map_player_ship_position();
}

/*
 * Translates L0886
 * Copy current player data to old player data (Shifting history down)
 * [ASM: 0886-0897]
 */
void copy_current_to_old_player_data(void) {
    state.OldAbovePlayerBulletLSB = state.AbovePlayerBulletLSB;
    state.OldAbovePlayerBulletMSB = state.AbovePlayerBulletMSB;
    
    state.OldPlayerBulletLSB = state.PlayerBulletLSB;
    state.OldPlayerBulletMSB = state.PlayerBulletMSB;
    
    state.OldPlayerShipLSB = state.PlayerShipLSB;
    state.OldPlayerShipMSB = state.PlayerShipMSB;
}

/*
 * Translates L0900 & L0926
 * Reads the joystick and updates PlayerShipX, bounding between 0x0D and 0xC0.
 * [ASM: 0900-0921]
 * [ASM: 0926-092E]
 */
void update_player_ship_x(void) {
    uint8_t input = ~state.IN0Current;
    
    // Bit 5 = Right (0x20), Bit 6 = Left (0x40)
    if ((input & 0x60) == 0) {
        return; // No movement button pressed
    }
    
    if ((input & 0x40) == 0) {
        // Move right (Right is pressed, Left is not)
        if (state.PlayerShipX < 0xC0) {
            state.PlayerShipX++;
            state.PlayerMoved = 0xFF;
        }
    } else {
        // Move left (Left is pressed)
        if (state.PlayerShipX >= 0x0D) {
            state.PlayerShipX--;
            state.PlayerMoved = 0xFF;
        }
    }
}

/*
 * Translates L08A0
 * Update player position, bullet and shield
 * [ASM: 08A0-08B7]
 */
void update_player_position_bullet_shield(void) {
    move_player();
    
    // Check main bullet
    get_assigned_player_bullet_tile(&state.PlayerBulletState);
    
    // Check if level is 3 (index 3 in 0-15 mapped levels)
    if ((state.LevelAndRound & LEVEL_PATTERN_MASK) != LEVEL_PATTERN_ALIENS_ACTIVE_3) {
        return;
    }
    
    // If game level 3, process second player bullet as well
    get_assigned_player_bullet_tile(&state.AbovePlayerBulletState);
}

/*
 * Translates L08C4
 * Player ship, shield and bullets handler.
 * [ASM: 08C4-08F3]
 */
void move_player(void) {
    coverage_hit("move_player");
    uint8_t ps = state.PlayerState;
    if ((ps & PLAYER_STATE_MOVEMENT_ENABLED) == 0) {
        draw_shields(); // L0AA0
        return;
    }
    
    if (state.ShieldCount != 0) {
        state.ShieldCount--;
    } else {
        // 08D6: CALL $00BB CheckInputBits -- een FLANK-detectie (nu
        // ingedrukt en vorige frame niet), geen niveau-test. Een eerdere
        // vertaling las alleen IN0Current, waardoor een vastgehouden
        // schildknop direct opnieuw activeerde (o.a. op respawn-frames).
        // Gevonden via scripted lockstep (mutated_rank_04_score_1279551,
        // record 1852).
        extern uint8_t check_input_bits(uint8_t mask);
        if (check_input_bits(BTN_SHIELD) != 0) {
            coverage_hit("player_shield_pressed");
            // 08DE: LD (HL),$40 -- overschrijft M4362, geen OR
            state.M4362 = 0x40;
            state.PlayerState &= (uint8_t)~PLAYER_STATE_MOVEMENT_ENABLED;
            state.ShieldCount = SHIELD_DURATION_INITIAL;
            state.ShieldCount--;
        }
    }
    
    update_player_ship_x(); // L0900
    
    // L08F0 - L08F3: Update animation frame (shape) based on X position
    get_player_ship_animation_frame_values(0x1600, &state.PlayerShipX); // L0926
}

/*
 * Translates L097A
 * Player ship X position mapping.
 * [ASM: 097A-0995]
 */
void map_player_ship_position(void) {
    uint8_t a = state.PlayerShipX;
    uint8_t b = a;
    a &= 0x07;
    a <<= 1;
    
    state.M439E = b - phoenix_player_x_position_mapping[a];
    state.M439F = b + phoenix_player_x_position_mapping[a + 1];
}

/*
 * Translates L0930
 * Get the assigned player bullet tile if fire button was pressed.
 * [ASM: 0930-093C]
 */
void get_assigned_player_bullet_tile(uint8_t* bullet_state_ptr) {
    if ((*bullet_state_ptr & 0x08) != 0) {
        update_player_bullet_y(bullet_state_ptr); // L0964
        return;
    }
    
    // 0937-093C: CheckInputBits($10) -- fire only on a 1->0 edge of bit 4,
    // not while the button is merely held down
    extern uint8_t check_input_bits(uint8_t mask);
    if (check_input_bits(BTN_FIRE) == 0) {
        return;
    }
    extern void spawn_player_bullet(uint8_t* bullet_state_ptr); // L093D
    spawn_player_bullet(bullet_state_ptr);
}

/*
 * Translates L0926
 * Get player ship animation frame values, mapped with T1600/T1620.
 * [ASM: 0926-092E]
 */
void get_player_ship_animation_frame_values(uint16_t bc, uint8_t* ptr_x) {
    uint8_t a = *ptr_x & 0x07;
    bc += a;

    extern const uint8_t phoenix_alien_shape_offset_page[0x100];
    uint8_t shape = phoenix_alien_shape_offset_page[bc - 0x1600];
    *(ptr_x - 1) = shape;
}

/*
 * Translates L093D
 * Spawn player bullet.
 * [ASM: 093D-0961]
 */
void spawn_player_bullet(uint8_t* bullet_state_ptr) {
    coverage_hit("spawn_player_bullet");
    // 093D-0940: NOT bullet_state_ptr -- CheckInputBits (called just before
    // this, from L0930) leaves HL pointing at IN0Previous ($43A1), and that
    // stale HL is what L093D's first three instructions operate on. This
    // clears the fire bit in IN0Previous, "consuming" the press edge so a
    // second call to get_assigned_player_bullet_tile in the same frame (the
    // dual-fire sub-level's AbovePlayerBulletState check) does NOT see the
    // same edge and spawn a second bullet stacked on the first -- it has to
    // wait for a fresh press. Without this, both bullet slots fire on the
    // same edge, at the same position, indistinguishable from a single shot.
    state.IN0Previous &= 0xEF;
    bullet_state_ptr[0] |= 0x08; // set bit 3 at PlayerBulletState
    
    uint8_t a = state.PlayerShipX;
    a += 0x04;
    bullet_state_ptr[2] = a; // PlayerBulletX
    
    a = state.PlayerShipY;
    a -= 0x08;
    bullet_state_ptr[3] = a; // PlayerBulletY
    
    // 0956: LD BC, $1620; CALL L0926
    get_player_ship_animation_frame_values(0x1620, &bullet_state_ptr[2]);
    
    state.BulletTriggered = 0x30;
}

/*
 * Translates L0964
 * Update PlayerBulletY (grid) and PlayerBulletState.
 * [ASM: 0964-0975]
 */
void update_player_bullet_y(uint8_t* bullet_state_ptr) {
    uint8_t a = bullet_state_ptr[3];
    a -= 0x08;
    bullet_state_ptr[3] = a;
    
    if (a >= 0x1F) return; // top of screen reached?
    
    bullet_state_ptr[0] &= 0xF7; // del bit 3 at PlayerBulletState
}

/*
 * Translates PlayerDataController
 * [ASM: 0700-0717]
 */
void player_data_controller(void) {
    uint16_t bc = 0x43C0;
    uint16_t de = 0x43E0;
    while (1) {
        extern void update_screen_objects(uint16_t bc, uint16_t de); // 0718
        update_screen_objects(bc, de);
        
        uint8_t c = bc & 0xFF;
        c += 4;
        bc = (bc & 0xFF00) | c;
        
        de = (de & 0xFF00) | (c + 0x20);
        
        if (c == 0xEC) {
            break;
        }
    }
}

/*
 * Translates ShieldsExpired
 * The player shield is expired.
 * Shield and player gets removed from screen.
 * PlayerShipX position is reset.
 * [ASM: 0B48-0B5A]
 */
void shields_expired(uint16_t de, uint8_t b, uint8_t c) {
    extern void draw_image_c_by_b(uint16_t hl, uint16_t de, uint8_t b, uint8_t c);
    draw_image_c_by_b(0x17F0, de, b, c);
    
    state.PlayerState = 0x0C;
    state.PlayerShape = 0x0C;
    
    uint8_t a = state.PlayerShipX;
    a &= 0xF8;
    a |= 0x03;
    state.PlayerShipX = a;
}

/*
 * Translates L0AA0
 * Draw shields.
 * [ASM: 0AA0-0AC1]
 */
void draw_shields(void) {
    uint8_t d = state.PlayerShipMSB;
    uint8_t e = state.PlayerShipLSB;
    uint16_t de = (d << 8) | e;
    
    extern uint16_t left_one_column(uint16_t de); // L0210
    de = left_one_column(de);
    de--; // One row above
    
    uint8_t b = 4;
    uint8_t c = 4;
    
    state.ShieldCount--;
    uint8_t a = state.ShieldCount;
    
    if (a == 0xC0) {
        shields_expired(de, b, c);
        return;
    }
    
    a &= 0x0C;
    a <<= 2; // Multiply by 4
    
    uint16_t hl = 0x1770 + a;
    extern void draw_image_c_by_b(uint16_t hl, uint16_t de, uint8_t b, uint8_t c);
    draw_image_c_by_b(hl, de, b, c);
}
