# Weapon Collision Declarations (`weapon_collision.h`) - C-Annotated Knowledge Graph Documentation

This document contains the annotated header declarations for [`weapon_collision.h`](../../weapon_collision.h).

---

## Declarations & Connections
- `process_enemy_bombs(void)`: Update loop for the 5 enemy bomb slots.
- `l0cc4_player_killed(void)`: Triggers the player explosion state.
- `l0e10(uint16_t bc, uint16_t hl)`: Player bullet collision scan against aliens.
- `check_player_ship_collision(void)`: Direct collision scan of aliens against the player ship or force field.

#### **Knowledge Graph Links**
* **Corresponding C Implementation:** [`weapon_collision.c`](../../weapon_collision.c) $\rightarrow$ [`weapon-collision.md`](weapon-collision.md)
