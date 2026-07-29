# Miscellaneous Logic (`misc_logic.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`misc_logic.c`](../misc_logic.c). Deze module bevat diverse hulplogica voor achtergrond-verversing, muntschermteksten, willekeurige bommen op het spelerschip en het initialiseren van de vogelgeheugenstructuren.

---

## Inhoudsopgave
1. [Achtergrond & Sterrenstelsels](#1-achtergrond--sterrenstelsels)
2. [Willekeurige Bom-drop Triggers](#2-willekeurige-bom-drop-triggers)
3. [Vogelgeheugen Initialisatie](#3-vogelgeheugen-initialisatie)

---

## 1. Achtergrond & Sterrenstelsels

### `l06f0`
#### **Beschrijving**
De functie [`l06f0`](../misc_logic.c#L12-L19) (Z80 ROM: `$06F0–$0701`) combineert de achtergrondverversing: sterren scrollen omlaag (`stars_scroll_down`), sterrenstelsels toevoegen (`add_galaxies_to_background`) en planeten toevoegen (`add_planets_to_background`).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `stars_scroll_down` — [`hw_video_audio.c`](../hw_video_audio.c)
  - `add_galaxies_to_background` — [`hw_video_audio.c`](../hw_video_audio.c)
  - `add_planets_to_background` — [`hw_video_audio.c`](../hw_video_audio.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`slow_print_scroll_register_update`](attract-mode.md#slow_print_scroll_register_update) — [`attract_mode.c#L244`](../attract_mode.c#L244)

---

### `l01e1`
#### **Beschrijving**
De functie [`l01e1`](../misc_logic.c#L24-L31) (Z80 ROM: `$01E1–$01EB`) wist voor- en achtergrondscherm en drukt de copyright-regels af.

---

## 2. Willekeurige Bom-drop Triggers

### `l24a0` & `l24f2`
#### **Beschrijving**
- [`l24a0`](../misc_logic.c#L37-L44) (Z80 ROM: `$24A0–$24BB`) activeert bij moederschip-levels (level >= 8) de moederschip-animatie en vuurt via [`l24f2`](../misc_logic.c#L55-L68) willekeurige bommen af op het spelerschip.
- [`l24f2`](../misc_logic.c#L55-L68) (Z80 ROM: `$24F2–$251C`) genereert een willekeurige X-positie (`get_random_number + 0x60`) en vuurt via `l25b7` een kogel af zodra deze positie de speler kruist.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l2351_mothership_animation`](mothership-impl.md#l2351_mothership_animation) — [`mothership_impl.c#L12`](../mothership_impl.c#L12)
  - [`get_random_number`](utilities.md#get_random_number) — [`utilities.c:L15`](../utilities.c#L15)
  - `l25b7` — [`weapon_collision.c#L100`](../weapon_collision.c#L100)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2000_alien_wave_main_loop`](alien-wave.md#l2000_alien_wave_main_loop) — [`alien_wave.c#L224`](../alien_wave.c#L224)

---

## 3. Vogelgeheugen Initialisatie

### `l32b0`
#### **Beschrijving**
De functie [`l32b0`](../misc_logic.c#L73-L98) (Z80 ROM: `$32B0–$32EB`) wist het RAM-bereik `$4350–$437F` en kopieert de initiële vogelgedragsstructuur uit ROM (`phoenix_bird_behaviour_scripts`) naar RAM-adres `0x4B00` op basis van `state.BirdsLeft`.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `phoenix_bird_behaviour_scripts` — [`phoenix_tables.c`](../phoenix_tables.c)
  - [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l0526`](state-init.md#l0526) — [`state_init.c#L61`](../state_init.c#L61)
