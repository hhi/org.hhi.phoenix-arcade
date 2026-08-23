#include "bird_logic.h"
#include "coverage.h"
#include "game_constants.h"

extern PhoenixState state;

extern void player_update(void); // 0876
extern void collision_detection_for_birds(void); // 3800
extern void birds_vertical_movement_update(void); // 2600
extern void check_bird_formation_player_collision(void); // 3980
extern void draw_first_4_bird_objects(void); // 3474
extern void draw_second_4_bird_objects(void); // 3486
extern void refresh_bird_flight_parameters(void); // 3560
extern void update_first_four_birds(void); // 3498
extern void update_second_four_birds(void); // 34AA
extern void handle_animations_for_killed_aliens(void); // 0FC0
extern void try_spawn_bird_dive_bomb(void); // 3930
extern void process_enemy_bombs(void); // 0C40
extern void finish_bird_wave_if_empty(void);
extern void update_second_bird_bank(void); // 3452

/*
 * Translates L3400
 * Coordinates one bird-wave frame. The collision pass brackets vertical
 * movement so both the old and new formation position are checked. Which
 * bank advances alternates with Counter9B; when fewer than four birds
 * remain, both banks run in the same frame.
 * [ASM: 3400-3436]
 * [ASM: 3438-344D]
 */
void process_birds(void) {
    coverage_hit("process_birds");
    player_update();
    collision_detection_for_birds();
    birds_vertical_movement_update();
    collision_detection_for_birds();
    check_bird_formation_player_collision();
    
    if (state.BirdsLeft == 0) {
        finish_bird_wave_if_empty();
        return;
    }
    
    if (state.BirdsLeft >= 4) {
        if ((state.Counter9B & 0x01) != 0) {
            // Odd frames prepare the second bank only.
            update_second_bird_bank();
        } else {
            // Even frames draw, move, then allow the first bank to attack.
            draw_first_4_bird_objects();
            refresh_bird_flight_parameters();
            update_first_four_birds();
            try_spawn_bird_dive_bomb();
            process_enemy_bombs(); 
        }
        return;
    }
    
    // A depleted wave keeps both four-bird banks visible and moving.
    draw_first_4_bird_objects();
    draw_second_4_bird_objects();
    refresh_bird_flight_parameters();
    update_first_four_birds();
    update_second_four_birds();
    
    if ((state.Counter9B & 0x01) != 0) {
        handle_animations_for_killed_aliens();
    } else {
        try_spawn_bird_dive_bomb();
        process_enemy_bombs();
    }

}


void bird_flight_path(void) {
    coverage_hit("bird_flight_path");
    // Calls L3800 to process complex geometric dive bombing
    collision_detection_for_birds();
}

extern void drawbirdobject(uint16_t bird_struct_addr);

/*
 * Draw bird objects 0 to 3.
 * [ASM: 3474-3485]
 */
void draw_first_4_bird_objects(void) {
    for (uint16_t bird_object_address = BIRD_OBJECT_BANK_ONE_START_ADDRESS;
         bird_object_address < BIRD_OBJECT_BANK_ONE_END_ADDRESS;
         bird_object_address += BIRD_OBJECT_RECORD_STRIDE) {
        drawbirdobject(bird_object_address);
    }
}

/*
 * Draw bird objects 4 to 7.
 * [ASM: 3486-3497]
 */
void draw_second_4_bird_objects(void) {
    for (uint16_t bird_object_address = BIRD_OBJECT_BANK_ONE_END_ADDRESS;
         bird_object_address < BIRD_OBJECT_BANK_TWO_END_ADDRESS;
         bird_object_address += BIRD_OBJECT_RECORD_STRIDE) {
        drawbirdobject(bird_object_address);
    }
}
