# Scoring & Sound Service (`scoring.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`scoring.c`](../../scoring.c). Deze module beheert de BCD-scoretelling, High Score vergelijkingen, bonusleven-drempelcontroles, attract-mode muntsymbolen en de per-frame geluidssynchronisatie.

---

## Inhoudsopgave
1. [BCD Score-berekeningen & High Score](#1-bcd-score-berekeningen--high-score)
2. [Per-frame Score & Geluid Service](#2-per-frame-score--geluid-service)
3. [Attract Mode Muntcontroles](#3-attract-mode-muntcontroles)

---

## 1. BCD Score-berekeningen & High Score

### `add_score` & `bcd_add`
#### **Beschrijving**
De functie [`add_score`](../../scoring.c#L66-L81) telt een BCD-gecodeerde score toe aan de actieve speler (Player 1 of Player 2, afhankelijk van bit 0 in `state.GameAndDemoOrSplash`). Hulpfunctie `bcd_add` verzorgt de BCD-optelling met half-carry en upper-carry correcties.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`update_hi_score`](#update_hi_score) — [`scoring.c#L80`](../../scoring.c#L80)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`update_scores_and_sound`](#update_scores_and_sound) — [`scoring.c#L109`](../../scoring.c#L109), [`L124`](../../scoring.c#L124)

---

### `update_hi_score`
#### **Beschrijving**
De functie [`update_hi_score`](../../scoring.c#L39-L59) (Z80 ROM: `$02F0–$02F5`) vergelijkt de 3-byte BCD scores van Player 1 en Player 2 en werkt de globale High Score (`HiScorehigh`, `HiScoremid`, `HiScorelow`) bij indien een nieuw record is bereikt.

---

## 2. Per-frame Score & Geluid Service

### `update_scores_and_sound`
#### **Beschrijving**
De functie [`update_scores_and_sound`](../../scoring.c#L93-L195) (Z80 ROM: `$2700–$27A8`, `$3A10`) is de per-frame servicemodule voor scoretoekenning, bonusleven-controle en geluidssynchronisatie.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - [`add_score`](#add_score) — [`scoring.c#L109`](../../scoring.c#L109), [`L124`](../../scoring.c#L124)
  - [`print_number`](utilities.md#print_number) — [`utilities.c:L80`](../../utilities.c#L80)
  - `update_lives_screen` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - `hw_write_sound_a` / `hw_write_sound_b` — [`hw_video_audio.c`](../../hw_video_audio.c)
  - `sound_set_frame_sample_index` — [`sound.c`](../../sound.c)
  - `l3a10` — [`sound_dispatcher.c`](../../sound_dispatcher.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_play_frame_update`](state-play.md#state_play_frame_update) — [`state_play.c`](../../state_play.c)

#### **Stap-voor-stap werking**
1. **Queued Scores toekennen:** Scant de score-buffers `state.M4370..M437F` (4 slots van 4 bytes) en roept [`add_score`](#add_score) aan voor verwerkte punten.
2. **Moederschip-explosie bonus:** Als `GameState == GAME_STATE_MOTHERSHIP_EXPLODING`, voegt hij de moederschip-bonusscore toe.
3. **Bonusleven drempelcontrole:** Voert een multi-byte BCD aftrekking uit (`Threshold - Score`). Bij een borrow (score hoger dan drempel):
   - Ophogen aantal levens (`Player1Lives++` of `Player2Lives++`).
   - Scherm verversen via `update_lives_screen()`.
   - Volgende bonusleven-drempel instellen.
4. **Hardware Audio Latching:** Schrijft de actuele geluidswaarden via `hw_write_sound_a` en `hw_write_sound_b` en roept de geluidsdispatcher `l3a10` aan.

---

## 3. Attract Mode Muntcontroles

### `check_coin_event`
#### **Beschrijving**
De functie [`check_coin_event`](../../scoring.c#L202-L218) verwerkt muntsymbolen in het VRAM tijdens de attract mode op basis van de DIP-switch instellingen (`hw_read_dsw()`).
