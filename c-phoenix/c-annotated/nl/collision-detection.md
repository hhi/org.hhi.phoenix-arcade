# Collision Detection (`collision_detection.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`collision_detection.c`](../../collision_detection.c). Deze module implementeert de fijne tegel- en pixelmasker botsingsdetectie tussen spelerkogels, vogels en eieren tijdens de vogel-levels.

---

## Inhoudsopgave
1. [Vogel Botsingsdetectie Hoofdlus](#1-vogel-botsingsdetectie-hoofdlus)
2. [Tegel- & Pixelmasker Inslagen](#2-tegel--pixelmasker-inslagen)
3. [Explosieslots & Schermwissen](#3-explosieslots--schermwissen)
4. [Wave Completion](#4-wave-completion)

---

## 1. Vogel Botsingsdetectie Hoofdlus

### `collision_detection_for_birds`
#### **Beschrijving**
De functie [`collision_detection_for_birds`](../../collision_detection.c#L132-L165) (Z80 ROM: `$3800–$3841`, `$391C–$3922`) berekent per frame de exacte botsing tussen een actieve spelerkogel en het bewegende vogelraster.

#### **Context & Aanroep**
Aangeroepen vanuit de vogel-level update lussen:
```c
collision_detection_for_birds();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - `phoenix_bullet_pixel_masks` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - [`l3844_small_bird_hit`](#l3844_small_bird_hit) — [`collision_detection.c#L159`](../../collision_detection.c#L159)
  - [`l38bc_large_hit`](#l38bc_large_hit) — [`collision_detection.c#L163`](../../collision_detection.c#L163)
  - [`mem_read`](utilities.md#mem_read) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c#L30`](../../bird_logic.c#L30)
  - [`bird_flight_path`](bird-logic.md#bird_flight_path) — [`bird_logic.c#L72`](../../bird_logic.c#L72)
  - [`check_bird_formation_player_collision`](bird-wave-behavior.md#check_bird_formation_player_collision) — [`bird_wave_behavior.c#L428`](../../bird_wave_behavior.c#L428)

#### **Stap-voor-stap werking**
1. **Kogelcontrole:** Breek af als de spelerkogel inactief is (`PlayerBulletState & 0x08 == 0`).
2. **VRAM-cel berekenen:** Houdt rekening met de verticale scroll-positie van de vogel-laag (`state.B4BD2`) om de VRAM-cel op te zoeken.
3. **Vogel-tegel drempel:** Controleert of de tegelwaarde ≥ 0x90 is (tegelwaarden onder 0x90 zijn achtergrond).
4. **Pixelmasker:** Raadpleegt `phoenix_bullet_pixel_masks` op basis van de exacte X-pixeloffset binnen de cel.
5. **Inslag verwerken:** Roept [`l3844_small_bird_hit`](#l3844_small_bird_hit) aan voor kleine vogels en [`l38bc_large_hit`](#l38bc_large_hit) voor grote vogels/eieren.

---

## 2. Tegel- & Pixelmasker Inslagen

### `l3844_small_bird_hit`
#### **Beschrijving**
De functie [`l3844_small_bird_hit`](../../collision_detection.c#L56-L91) (Z80 ROM: `$3844–$388D`, `$3894–$389C`) verwerkt inslagen op kleine vogels.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l38a1_erase_bird`](#l38a1_erase_bird) — [`collision_detection.c#L61`](../../collision_detection.c#L61)
  - [`bird_explosion_slot`](#bird_explosion_slot) — [`collision_detection.c#L73`](../../collision_detection.c#L73)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`collision_detection_for_birds`](#collision_detection_for_birds) — [`collision_detection.c#L159`](../../collision_detection.c#L159)

#### **Stap-voor-stap werking**
Wist het vogel-object van het scherm via [`l38a1_erase_bird`](#l38a1_erase_bird), verlaagt `state.BirdsLeft`, berekent de scorepunten (50 punten voor gewone vogels, variabele bonusscore voor volgroeide vogels) en slaat de explosie op via [`bird_explosion_slot`](#bird_explosion_slot).

---

### `l38bc_large_hit`
#### **Beschrijving**
De functie [`l38bc_large_hit`](../../collision_detection.c#L99-L124) (Z80 ROM: `$38BC–$38F1`) verwerkt inslagen op eieren en grote vogels. Eieren transformeren bij een treffer direct in een vogel via `phoenix_egg_transformation_types`.

---

## 3. Explosieslots & Schermwissen

### `l38a1_erase_bird` & `bird_explosion_slot`
#### **Beschrijving**
- [`l38a1_erase_bird`](../../collision_detection.c#L20-L29) (Z80 ROM: `$38A1–$38B5`) wist een getroffen vogel door de lege 4x4 tegelvorm (`0x17F0`) te tekenen. Bevat de beroemde Arcade-beveiliging ("AMSTAR" copyright-code selector).
- [`bird_explosion_slot`](../../collision_detection.c#L38-L48) (Z80 ROM: `$38F8–$391B`) registreert een nieuwe explosie in een vrij geheugenslot (`0x4370` t/m `0x437C`).

---

## 4. Wave Completion

### `l3462_no_birds_left`
#### **Beschrijving**
De functie [`l3462_no_birds_left`](../../collision_detection.c#L174-L185) (Z80 ROM: `$3462–$346D`) wordt aangeroepen zodra alle vogels in een wave zijn uitgeschakeld (`BirdsLeft == 0`) en verzorgt de overgang naar de ronde-afronding via [`l2204`](alien-wave.md#l2204).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `process_enemy_bombs` — [`weapon_collision.c#L17`](../../weapon_collision.c#L17)
  - [`handle_animations_for_killed_aliens`](alien-logic.md#handle_animations_for_killed_aliens) — [`alien_logic.c#L195`](../../alien_logic.c#L195)
  - [`l2204`](alien-wave.md#l2204) — [`alien_wave.c#L80`](../../alien_wave.c#L80)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c#L36`](../../bird_logic.c#L36)
