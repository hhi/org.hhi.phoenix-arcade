# Weapon Collision (`weapon_collision.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`weapon_collision.c`](../weapon_collision.c). Deze module beheert de botsingsdetectie voor spelerkogels, vijandelijke kogels, schilden en directe botsingen tussen het spelerschip en vliegende aliens.

---

## Inhoudsopgave
1. [Spelerkogels versus Aliens](#1-spelerkogels-versus-aliens)
2. [Vijandelijke Bommen & Kogels](#2-vijandelijke-bommen--kogels)
3. [Alien-Speler Directe Botsingen](#3-alien-speler-directe-botsingen)
4. [Speler Dood- & Status-routines](#4-speler-dood--status-routines)

---

## 1. Spelerkogels versus Aliens

### `l0e10`
#### **Beschrijving**
De functie [`l0e10`](../weapon_collision.c#L233-L294) (Z80 ROM: `$0E10–$0E9D`) voert de botsingsdetectie uit van spelerkogels tegen aliens (zowel binnen de formatie als in vrije duikvlucht).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../coverage.c#L12)
  - `phoenix_formation_hit_window` — [`phoenix_tables.c`](../phoenix_tables.c)
  - [`l0c00_kill_score`](#l0c00_kill_score) — [`weapon_collision.c#L214`](../weapon_collision.c#L214)
  - [`l0ea4_with_score`](#l0ea4_with_score) — [`weapon_collision.c#L301`](../weapon_collision.c#L301)
  - [`mem_read`](utilities.md#mem_read) — [`utilities.c:L22`](../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`check_enemy_bullet_to_player_collision`](#check_enemy_bullet_to_player_collision) — [`weapon_collision.c#L191-L192`](../weapon_collision.c#L191-L192)

#### **Stap-voor-stap werking**
1. **Kogel active check:** Controleert of de spelerkogel actief is (`mem_read(bc) & 0x08 != 0`).
2. **Tegelinspectie:** Leest de VRAM-cel direct boven de kogel. Verwerkt alleen alien-tegels (`$60` t/m `$BF`).
3. **Alien buiten formatie (`chr >= 0x68`):** Scant de 16 alien-records. Als het kogelkader overlap toont met een duikende alien, roept [`l0c00_kill_score`](#l0c00_kill_score) aan en vernietigt de alien via [`l0ea4_with_score`](#l0ea4_with_score).
4. **Alien in formatie (`chr < 0x68`):** Raadpleegt de raakvenster-tabel `phoenix_formation_hit_window` voor de specifieke tegelvorm. Bij een treffer wordt 20 punten toegekend (`score = 0x0C02`) en [`l0ea4_with_score`](#l0ea4_with_score) aangeroepen.

---

### `l0ea4_with_score`
#### **Beschrijving**
De functie [`l0ea4_with_score`](../weapon_collision.c#L301-L345) (Z80 ROM: `$0EA4–$0EE5`) registreert het doden van een alien, update kogel- en alien-controlestates, kent score toe en initialiseert een explosieslot.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../coverage.c#L12)
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l0e10`](#l0e10) — [`weapon_collision.c#L265`](../weapon_collision.c#L265), [`L291`](../weapon_collision.c#L291)
  - [`l0f00_check_alien_with_player_collision`](#l0f00_check_alien_with_player_collision) — [`weapon_collision.c#L411`](../weapon_collision.c#L411), [`L446`](../weapon_collision.c#L446)

---

## 2. Vijandelijke Bommen & Kogels

### `process_enemy_bombs`
#### **Beschrijving**
De functie [`process_enemy_bombs`](../weapon_collision.c#L163-L169) (Z80 ROM: `$0C40–$0C51`) beheert het per-frame bijwerken van alle 5 de vijandelijke bom-slots.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l0c84_enemy_bullet_movement`](#l0c84_enemy_bullet_movement) — [`weapon_collision.c#L63`](../weapon_collision.c#L63)
  - `update_screen_objects` — [`hw_video_audio.c`](../hw_video_audio.c)
  - `get_screen_ram_address` — [`hw_video_audio.c`](../hw_video_audio.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2160`](alien-wave.md#l2160) — [`alien_wave.c#L145`](../alien_wave.c#L145)
  - [`l2180`](alien-wave.md#l2180) — [`alien_wave.c#L163`](../alien_wave.c#L163)
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c#L48`](../bird_logic.c#L48)

---

### `l0c84_enemy_bullet_movement`
#### **Beschrijving**
De functie [`l0c84_enemy_bullet_movement`](../weapon_collision.c#L63-L98) (Z80 ROM: `$0C84–$0CB3`) beweegt een vijandelijke kogel omlaag (`Y += 4`), wisselt diens animatieframe en controleert inslagen op het spelerschip of het speler-krachtveld.

---

## 3. Alien-Speler Directe Botsingen

### `l0f00_check_alien_with_player_collision`
#### **Beschrijving**
De functie [`l0f00_check_alien_with_player_collision`](../weapon_collision.c#L380-L454) (Z80 ROM: `$0F00–$0FB9`) controleert fysieke botsingen tussen dalende aliens en het spelerschip (of het speler-krachtveld).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../coverage.c#L12)
  - [`l0f56_screen_ram_collision`](#l0f56_screen_ram_collision) — [`weapon_collision.c#L352`](../weapon_collision.c#L352)
  - [`l0cc4_player_killed`](#l0cc4_player_killed) — [`weapon_collision.c#L442`](../weapon_collision.c#L442)
  - [`l0ea4_with_score`](#l0ea4_with_score) — [`weapon_collision.c#L411`](../weapon_collision.c#L411), [`L446`](../weapon_collision.c#L446)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2150`](alien-wave.md#l2150) — [`alien_wave.c#L137`](../alien_wave.c#L137)
  - [`l2190`](alien-wave.md#l2190) — [`alien_wave.c#L174`](../alien_wave.c#L174)

#### **Stap-voor-stap werking**
1. **Actief krachtveld (`ShieldCount >= 0xC0`):** Controleert via [`l0f56_screen_ram_collision`](#l0f56_screen_ram_collision) of er een alien het schild raakt. Zo ja: vernietigt de alien zonder dat de speler schade oploopt (`l0ea4_with_score(0x0D02, ...)`).
2. **Geen krachtveld:** Als een alien het schip raakt: vernietigt het spelerschip via [`l0cc4_player_killed`](#l0cc4_player_killed) en vernietigt de alien via [`l0ea4_with_score`](#l0ea4_with_score).

---

## 4. Speler Dood- & Status-routines

### `l0cc4_player_killed`
#### **Beschrijving**
De functie [`l0cc4_player_killed`](../weapon_collision.c#L51-L56) (Z80 ROM: `$0CC4–$0CD3`) wordt aangeroepen bij een dodelijke treffer op het spelerschip.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../coverage.c#L12)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l0cb4_check_bullet_hit_player`](#l0cb4_check_bullet_hit_player) — [`weapon_collision.c#L43`](../weapon_collision.c#L43)
  - [`l0f00_check_alien_with_player_collision`](#l0f00_check_alien_with_player_collision) — [`weapon_collision.c#L442`](../weapon_collision.c#L442)
  - [`check_bird_formation_player_collision`](bird-wave-behavior.md#check_bird_formation_player_collision) — [`bird_wave_behavior.c#L434`](../bird_wave_behavior.c#L434)

#### **Stap-voor-stap werking**
Schakelt de gamestatus om naar `GAME_STATE_PLAYER_EXPLODING`, stelt de explosieduur in op `state.CounterA5 = 0x60` en start de deeltjes-explosie via `state.ParticleExplosion = 0x10`.
