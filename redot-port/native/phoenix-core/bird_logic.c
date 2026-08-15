#include "bird_logic.h"
#include "coverage.h"

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
extern void l3462_no_birds_left(void);
extern void update_second_bird_bank(void); // 3452

/*
 * Translates L3400
 * Handles bird egg hatching, spawning, and flight paths.
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
        l3462_no_birds_left();
        return;
    }
    
    if (state.BirdsLeft >= 4) {
        if ((state.Counter9B & 0x01) != 0) {
            update_second_bird_bank();
        } else {
            draw_first_4_bird_objects();
            refresh_bird_flight_parameters();
            update_first_four_birds();
            try_spawn_bird_dive_bomb();
            process_enemy_bombs(); 
        }
        return;
    }
    
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
    uint16_t addr = 0x4B70;
    while (addr < 0x4B90) {
        drawbirdobject(addr);
        addr += 0x08;
    }
}

/*
 * Draw bird objects 4 to 7.
 * [ASM: 3486-3497]
 */
void draw_second_4_bird_objects(void) {
    uint16_t addr = 0x4B90;
    while (addr < 0x4BB0) {
        drawbirdobject(addr);
        addr += 0x08;
    }
}
