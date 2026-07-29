# Mothership Logic (`mothership_logic.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`mothership_logic.c`](../mothership_logic.c). Deze module behandelt de logica voor het moederschip (level 5), inclusief het wissen van het moederschip en de bonusscore-berekening bij het vernietigen van de kern.

---

## Inhoudsopgave
1. [Moederschip Animatie & Wissen](#1-moederschip-animatie--wissen)
2. [Kern-vernietiging & Bonusscore](#2-kern-vernietiging--bonusscore)

---

## 1. Moederschip Animatie & Wissen

### `mothership_descent_logic`
#### **Beschrijving**
De functie [`mothership_descent_logic`](../mothership_logic.c#L12-L15) roept de animatieroutine op vaste RAM-slots aan.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l2351_mothership_animation`](mothership-impl.md#l2351_mothership_animation) — [`mothership_impl.c#L12`](../mothership_impl.c#L12)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_play_frame_update`](state-play.md#state_play_frame_update) — [`state_play.c`](../state_play.c)

---

### `erase_mothership`
#### **Beschrijving**
De functie [`erase_mothership`](../mothership_logic.c#L22-L30) (Z80 ROM: `$246A–$2475`) wist de weergave van het moederschip van het voorgrondscherm.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `draw_image_c_by_b` — [`sprite_rendering.c`](../sprite_rendering.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_play_frame_update`](state-play.md#state_play_frame_update) — [`state_play.c`](../state_play.c)

#### **Stap-voor-stap werking**
Herstelt het achtergrond-sterrenveld op schermadres `0x4AC6` door 20 kolommen bij 9 rijen (`0x14` x `0x09`) te overschrijven met de achtergrondtegels van ROM `0x1C00` via `draw_image_c_by_b(0x1C00, 0x4AC6, 0x09, 0x14)`.

---

## 2. Kern-vernietiging & Bonusscore

### `mothership_core_hit_check`
#### **Beschrijving**
De functie [`mothership_core_hit_check`](../mothership_logic.c#L48-L76) (Z80 ROM: `$2520–$254F`) berekenen de bonusscore bij een voltreffer op de kern van het moederschip, slaat deze op in BCD-formaat en toont de score op het scherm.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `clear_foreground` — [`hw_video_audio.c`](../hw_video_audio.c)
  - [`print_number`](utilities.md#print_number) — [`utilities.c:L80`](../utilities.c#L80)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - `process_player_bullet_vs_mothership` — [`weapon_collision.c`](../weapon_collision.c)

#### **Stap-voor-stap werking**
1. **Scherm schonen:** Roept `clear_foreground()` aan om overbodige sprites te wissen.
2. **Bonusscore berekenen:** Roept `CounterB9` op met offset `0x60`, voert een `RRCA` rotatie uit en voegt de ronde-bits toe (`LevelAndRound & 0xF0`). Klem de waarde op maximaal `$90`.
3. **BCD-correctie:** Voert DAA BCD-correctie uit op de bonuswaarde.
4. **Opslaan in RAM:** Slaat de BCD-score op in `state.M439D` (MSB) en `state.M439E` (LSB).
5. **Score afdrukken:** Roept `print_number(screen, 0x439E, 4)` aan om de 4-cijferige bonusscore af te drukken op positie `DE - $5E`.
