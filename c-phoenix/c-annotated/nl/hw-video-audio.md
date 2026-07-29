# Hardware Video & Audio (`hw_video_audio.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`hw_video_audio.c`](../../hw_video_audio.c). Deze module vormt de interface tussen de geporteerde game-logica, VBlank synchronisatie, SDL2 audio/video rendering en RAM-bank opschoning.

---

## Inhoudsopgave
1. [Hoofd-entry & VBlank Synchronisatie](#1-hoofd-entry--vblank-synchronisatie)
2. [RAM- & Schermopschoning](#2-ram--schermopschoning)
3. [Score & Levens Weergave](#3-score--levens-weergave)

---

## 1. Hoofd-entry & VBlank Synchronisatie

### `phoenix_main_loop`
#### **Beschrijving**
De functie [`phoenix_main_loop`](../../hw_video_audio.c#L123-L148) (Z80 ROM: `$0000–$004F`) is de centrale hoofdlus en het startpunt van het *Phoenix* ROM-programma.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`init_sound_screen`](#init_sound_screen) — [`hw_video_audio.c#L124`](../../hw_video_audio.c#L124)
  - `print_text_lines` — [`hw_video_audio.c#L125`](../../hw_video_audio.c#L125)
  - [`wait_vblank_coin`](#wait_vblank_coin) — [`hw_video_audio.c#L128`](../../hw_video_audio.c#L128)
  - [`coin_checking`](attract-mode.md#coin_checking) — [`attract_mode.c#L281`](../../attract_mode.c#L281)
  - [`prompt_for_start_game`](attract-mode.md#prompt_for_start_game) — [`attract_mode.c#L293`](../../attract_mode.c#L293)
  - [`splash_and_demo`](attract-mode.md#splash_and_demo) — [`attract_mode.c#L32`](../../attract_mode.c#L32)
  - [`game_state_machine`](game-state-machine.md#game_state_machine) — [`game_state_machine.c#L31`](../../game_state_machine.c#L31)
  - [`update_scores_and_sound`](scoring.md#update_scores_and_sound) — [`scoring.c#L93`](../../scoring.c#L93)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - `main` / `platform_sdl_main` — [`platform_sdl.c`](../../platform_sdl.c)

---

### `wait_vblank_coin`
#### **Beschrijving**
De functie [`wait_vblank_coin`](../../hw_video_audio.c#L30-L71) (Z80 ROM: `$0080–$00B5`) wacht op de verticale blanking (60Hz VBlank), verwerkt munten-invoerflanken en verhoogt de frame-tellers `state.Counter9B` en `state.Counter9A`.

---

## 2. RAM- & Schermopschoning

### `clear_background` & `clear_foreground`
#### **Beschrijving**
- [`clear_background`](../../hw_video_audio.c#L155-L161) (Z80 ROM: `$03A0–$03AF`) wist de 26 kolommen van het achtergrondscherm (`$4800–$4B3F`).
- [`clear_foreground`](../../hw_video_audio.c#L237-L246) (Z80 ROM: `$0380–$039D`) wist de 26 kolommen van het voorgrondscherm (`$4000–$433F`), met uitzondering van de bovenste tekstbalk.

---

## 3. Score & Levens Weergave

### `clear_and_print_scores` & `update_lives_screen`
#### **Beschrijving**
- [`clear_and_print_scores`](../../hw_video_audio.c#L196-L210) (Z80 ROM: `$032E–$034E`) reset de scoregeheugens van P1 en P2 en drukt de 6-cijferige scores af op het scherm.
- [`update_lives_screen`](../../hw_video_audio.c#L216-L222) (Z80 ROM: `$0367–$0376`) stuurt de speler-levensweergave in VRAM aan.
