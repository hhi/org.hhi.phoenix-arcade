# Alien Logic (`alien_logic.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een diepgaande, geannoteerde analyse van alle functies in [`alien_logic.c`](../../alien_logic.c) en [`alien_logic.h`](../../alien_logic.h). Elke functie is uitgewerkt volgens een **Knowledge Graph benadering** met uitgaande aanroepen (`Aanroepen`) en inkomende koppelingen (`Aangeroepen door / Backlinks`).

---

## Inhoudsopgave
1. [Initialisatie & Posities](#1-initialisatie--posities)
2. [Explosies & Animaties voor Neergeschoten Aliens](#2-explosies--animaties-voor-neergeschoten-aliens)
3. [Scherm- & RAM-updates](#3-scherm--ram-updates)
4. [Beweging & Frame-animaties](#4-beweging--frame-animaties)
5. [Breakout, Bomb-drop & Pattern Schedulers](#5-breakout-bomb-drop--pattern-schedulers)
6. [Aanvalslogica & Dive-bomb Triggers](#6-aanvalslogica--dive-bomb-triggers)

---

## 1. Initialisatie & Posities

### `init_alien_control_states`
#### **Beschrijving**
De functie [`init_alien_control_states`](../../alien_logic.c#L19-L25) (Z80 ROM: `$05EC–$05F9`) bepaalt de initiële vlieg- en besturingsparameters voor de aliens aan het begin van een nieuwe ronde of level.

#### **Context & Aanroep**
Wordt aangeroepen tijdens het starten van een level vanuit de game-initialisatieroutine:
```c
init_alien_control_states();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`init_alien_control_states_05fa`](#init_alien_control_states_05fa) — [`alien_logic.c:L24`](../../alien_logic.c#L24)
  - `phoenix_alien_control_init_values` — [`phoenix_tables.c:L265`](../../phoenix_tables.c#L265)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_init_start_round`](state-init.md#state_init_start_round) — [`state_init.c:L45`](../../state_init.c#L45)

#### **Stap-voor-stap werking**
1. **Index bepalen:** Berekent de opzoek-index via `state.LevelAndRound & 0x0F`.
2. **Init-waarden ophalen:** Haalt uit de opzoektabel `phoenix_alien_control_init_values` twee initiële besturingsbytes op:
   - `d`: Waarde voor Controlstate A (status- en animatiebits).
   - `e`: Waarde voor Controlstate B (sprite/shape-index).
3. **Overbrengen naar RAM:** Roept [`init_alien_control_states_05fa(d, e)`](#init_alien_control_states_05fa) aan om deze waarden toe te wijzen aan het geheugenblok van alle aliens.

---

### `init_alien_control_states_05fa`
#### **Beschrijving**
De functie [`init_alien_control_states_05fa`](../../alien_logic.c#L207-L217) (Z80 ROM: `$05FA–$060D`) vult het geheugenblok van alle levende aliens met de gekozen controlestates `d` en `e`.

#### **Context & Aanroep**
Aangeroepen door `init_alien_control_states`:
```c
init_alien_control_states_05fa(d, e);
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`init_alien_control_states`](#init_alien_control_states) — [`alien_logic.c:L24`](../../alien_logic.c#L24)

#### **Geheugen- & Structuur-context**
De RAM-tabel voor de alien-besturing start op adres `0x4B70`. Elk alien-record is 4 bytes groot:
- **Byte 0 (`HL`):** Controlstate A (`d`)
- **Byte 1 (`HL+1`):** Controlstate B (`e`)
- **Byte 2 (`HL+2`):** X-coördinaat op het scherm
- **Byte 3 (`HL+3`):** Y-coördinaat op het scherm

#### **Stap-voor-stap werking**
1. **Statuscontrole:** Controleert of `state.AliensLeft == 0`. Zo ja, breekt de functie direct af.
2. **RAM vullen:** Loopt over maximaal 16 aliens. Schrijft `d` naar Control A (`0x4B70 + i*4`) en `e` naar Control B (`0x4B71 + i*4`).
3. **Pointer verhogen:** Ophoogt het geheugenadres steeds met 4 bytes (`hl += 4`).

---

### `init_alien_positions`
#### **Beschrijving**
De functie [`init_alien_positions`](../../alien_logic.c#L224-L242) (Z80 ROM: `$0610–$0638`) initialiseert de X- en Y-startcoördinaten op het schermraster voor de formatie van maximaal 16 aliens.

#### **Context & Aanroep**
Aangeroepen bij level-initialisatie:
```c
init_alien_positions();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
  - `phoenix_alien_position_pointer_table` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - `phoenix_alien_position_layout_page` — [`phoenix_tables.c`](../../phoenix_tables.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_init_start_round`](state-init.md#state_init_start_round) — [`state_init.c:L46`](../../state_init.c#L46)

#### **Stap-voor-stap werking**
1. **Layout-pagina bepalen:** Berekent de index `(state.LevelAndRound >> 1) & 0x0F` en zoekt in `phoenix_alien_position_pointer_table` het startadres/offset binnen de layoutpagina `phoenix_alien_position_layout_page` op.
2. **Coördinaten wegschrijven:** Doorloopt alle levende aliens (max 16) en schrijft de opeenvolgende X- en Y-coördinaten weg naar RAM-adres `0x4B72` (offset `+2` en `+3` binnen het 4-byte record).
3. **Pointer verhogen:** Springt na elke geschreven alien 3 bytes verder (`de += 3`), waardoor de coördinaten voor de volgende alien exact op `0x4B76`, `0x4B7A`, etc. terechtkomen.

---

### `copy_init_values_for_16_aliens`
#### **Beschrijving**
De functie [`copy_init_values_for_16_aliens`](../../alien_logic.c#L249-L265) (Z80 ROM: `$0650–$0679`) initialiseert de pointers naar het bewegingspatroon voor de 16 aliens.

#### **Context & Aanroep**
Aangeroepen tijdens de voorbereiding van een alien-golf.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
  - `phoenix_alien_layout_pointers` — [`phoenix_tables.c`](../../phoenix_tables.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_init_start_round`](state-init.md#state_init_start_round) — [`state_init.c:L47`](../../state_init.c#L47)

#### **Stap-voor-stap werking**
1. **Patroonadres ophalen:** Berekent de index via `state.LevelAndRound & 0x0F` en haalt het 16-bit patroonpointeradres `(d, e)` op uit `phoenix_alien_layout_pointers`.
2. **Tabel vullen:** Schrijft `d` (MSB) en `e` (LSB) opeenvolgend weg in de patroontabel op RAM-adres `0x4B50` (2 bytes per alien, in totaal 32 bytes voor 16 aliens: `0x4B50–0x4B6F`).

---

### `get_animation_chrs_aliens_fade_in`
#### **Beschrijving**
De functie [`get_animation_chrs_aliens_fade_in`](../../alien_logic.c#L31-L37) (Z80 ROM: `$085A–$0871`) bepaalt het tegel/karakter-ID van aliens tijdens hun verschijning (fade-in) aan de start van een golf.

#### **Context & Aanroep**
Aangeroepen in de rendering-lus zolang aliens aan het invliegen/verschijnen zijn.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - Geen (inspecteert `state.CounterB4`)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L35`](../../alien_wave.c#L35)

#### **Stap-voor-stap werking**
Inspecteert de algemene timer `state.CounterB4` en retourneert de sprite-tegel ID op basis van drempelwaarden:
- `a >= 0x11` $\rightarrow$ `0x6C`
- `a >= 0x0D` $\rightarrow$ `0x6D`
- `a >= 0x09` $\rightarrow$ `0x6E`
- `a >= 0x05` $\rightarrow$ `0x6F`
- Anders $\rightarrow$ `0x68`

---

## 2. Explosies & Animaties voor Neergeschoten Aliens

### `handle_animations_for_killed_aliens`
#### **Beschrijving**
De functie [`handle_animations_for_killed_aliens`](../../alien_logic.c#L195-L200) (Z80 ROM: `$0FC0–$0FFF`) is de centrale aanroeproutine die in elke frame-update alle actieve explosies en bonusscore-animaties op het scherm verwerkt.

#### **Context & Aanroep**
Wordt vanuit de hoofd-gameloop aangeroepen:
```c
void handle_animations_for_killed_aliens(void) {
    l0fd8(0x4370); // Explosieslot 0 voor normale aliens
    l0fd8(0x4374); // Explosieslot 1 voor normale aliens
    l3758_bonus_explosion_animation(0x4378); // Bonusexplosieslot 0 voor volgroeide vogels
    l3758_bonus_explosion_animation(0x437C); // Bonusexplosieslot 1 voor volgroeide vogels
}
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l0fd8`](#l0fd8) — [`alien_logic.c:L196-L197`](../../alien_logic.c#L196-L197)
  - [`l3758_bonus_explosion_animation`](#l3758_bonus_explosion_animation) — [`alien_logic.c:L198-L199`](../../alien_logic.c#L198-L199)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_play_frame_update`](state-play.md#state_play_frame_update) — [`state_play.c:L120`](../../state_play.c#L120)

---

### `l0fd8`
#### **Beschrijving**
De functie [`l0fd8`](../../alien_logic.c#L43-L74) (Z80 ROM: `$0FD8–$0FEF`) is verantwoordelijk voor het bijwerken en tekenen van de explosie-animatie van een neergeschoten standaard alien op geheugenadres `hl` (`0x4370` of `0x4374`).

#### **Context & Aanroep**
In de game-loop wordt `l0fd8` aangeroepen via `handle_animations_for_killed_aliens` voor twee vaste geheugenslots:
```c
l0fd8(0x4370); // Explosieslot 0
l0fd8(0x4374); // Explosieslot 1
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`left_one_column`](utilities.md#left_one_column) — [`utilities.c:L45`](../../utilities.c#L45)
  - `phoenix_alien_explosion_frames` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - [`drawNx2`](sprite-rendering.md#drawnx2) — [`sprite_rendering.c:L30`](../../sprite_rendering.c#L30)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`handle_animations_for_killed_aliens`](#handle_animations_for_killed_aliens) — [`alien_logic.c:L196-L197`](../../alien_logic.c#L196-L197)

#### **Geheugen- & Structuur-context**
Elk explosieslot is 4 bytes groot:
- **Byte 0 (`HL`):** Animatieteller / status (`0` = inactief, `>0` = actieve explosie).
- **Byte 1 (`HL+1`):** Niet gebruikt.
- **Byte 2 & 3 (`HL+2`, `HL+3`):** 16-bits schermankeradres (`DE`).

#### **Stap-voor-stap werking van `l0fd8`**
1. **Check of animatie actief is:**
   Leest de animatieteller `a = mem_read(hl)` uit het RAM-slot. Als `a == 0`, is er geen actieve explosie in dit slot en stopt de functie direct. *(Z80: `LD A,(HL)` / `AND A` / `RET Z`)*.
2. **Verlaag de animatieteller:**
   Slaat de huidige waarde op in `b = a` en verlaagt de teller met 1 in het RAM (`mem_write(hl, a - 1)`). *(Z80: `LD B,(HL)` / `DEC (HL)`)*.
3. **Schermcoördinaten uitlezen:**
   Leest het 16-bits schermankeradres `de` uit het geheugenblok (op offset `+2` en `+3`).
4. **Positie uitlijnen:**
   Verschuift het schermadres 1 kolom naar links via `left_one_column(de)`. *(Z80: `CALL $0210`)*.
5. **Explosieframe/sprite bepalen:**
   Berekent de frame-index aan de hand van de resterende tijd: `offset = (b & 0x0E) >> 1` (index 0..7). Zoekt het bijbehorende sprite-ID op in de opzoektabel `phoenix_alien_explosion_frames[offset]` en construeert het ROM-adres van het sprite-patroon (`0x1700 | img`).
6. **Sprite tekenen:**
   Roept `drawNx2(img_addr, de, 0xFFDF, 3)` aan om het explosie-frame (een 3x2 tegelmatrix) op het video-RAM te tekenen met een offset van `-33` (`0xFFDF`) tussen rijparen. *(Z80: `EX DE,HL`, `LD BC,$FFDF`, `JP $3540`)*.

---

### `l3758_bonus_explosion_animation`
#### **Beschrijving**
De functie [`l3758_bonus_explosion_animation`](../../alien_logic.c#L166-L188) (Z80 ROM: `$3758–$37CC`) animeert de uitwaaierende bonusexplosie en scoreweergave van een gedode volgroeide vogel op adres `hl` (`0x4378` of `0x437C`).

#### **Context & Aanroep**
Aangeroepen door `handle_animations_for_killed_aliens`:
```c
l3758_bonus_explosion_animation(0x4378);
l3758_bonus_explosion_animation(0x437C);
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l37cc_erase_bonus_explosion`](#l37cc_erase_bonus_explosion) — [`alien_logic.c:L172`](../../alien_logic.c#L172)
  - [`l37b0_print_bonus_score`](#l37b0_print_bonus_score) — [`alien_logic.c:L177`](../../alien_logic.c#L177)
  - [`l3796_bonus_explosion_left`](#l3796_bonus_explosion_left) — [`alien_logic.c:L186`](../../alien_logic.c#L186)
  - [`l3758_bonus_explosion_right`](#l3758_bonus_explosion_right) — [`alien_logic.c:L187`](../../alien_logic.c#L187)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`handle_animations_for_killed_aliens`](#handle_animations_for_killed_aliens) — [`alien_logic.c:L198-L199`](../../alien_logic.c#L198-L199)

#### **Stap-voor-stap werking**
1. **Statuscontrole:** Controleert `mem_read(hl) == 0`. Zo ja, keert direct terug.
2. **Teller verlagen:** Verlaagt de teller `counter = mem_read(hl) - 1`.
3. **Einde animatie (`counter == 0`):** De animatie is afgelopen; wist de restanten van het voorgrondscherm via [`l37cc_erase_bonus_explosion(hl)`](#l37cc_erase_bonus_explosion).
4. **Even tellerstand (`(counter & 1) == 0`):** Toont de behaalde bonusscorepunten in het midden van de explosie via [`l37b0_print_bonus_score(hl)`](#l37b0_print_bonus_score).
5. **Oneven tellerstand:** Berekent de uitwaaier-offset `a = ((0x0F - counter) & 0x0E) << 4` en tekent de linker- en rechterhelften van de explosie via [`l3796_bonus_explosion_left(a, de)`](#l3796_bonus_explosion_left) en [`l3758_bonus_explosion_right(a, de)`](#l3758_bonus_explosion_right).

---

### `l3796_bonus_explosion_left`
#### **Beschrijving**
De functie [`l3796_bonus_explosion_left`](../../alien_logic.c#L100-L107) (Z80 ROM: `$3796–$37AA`) tekent het linkerdeel van de uitwaaierende bonusexplosie op het scherm.

#### **Context & Aanroep**
Aangeroepen vanuit `l3758_bonus_explosion_animation` tijdens oneven frames.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`drawNx2`](sprite-rendering.md#drawnx2) — [`sprite_rendering.c:L30`](../../sprite_rendering.c#L30)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l3758_bonus_explosion_animation`](#l3758_bonus_explosion_animation) — [`alien_logic.c:L186`](../../alien_logic.c#L186)

#### **Stap-voor-stap werking**
1. **Schermadres berekenen:** Berekent het doel-RAM adres `hl = (a + 0x60) + de`.
2. **Grenscontrole:** Controleert of het adres binnen het geldige schermbereik valt (`(uint32_t)hl + 0xBCC0 > 0xFFFF` / Z80 `RET C`). Indien buiten bereik, breekt af.
3. **Sprite rendering:** Tekent de 3x2 tegelmatrix vanaf ROM-tegel `0x17D0` via `drawNx2(0x17D0, hl, 0xFFDF, 3)`.

---

### `l3758_bonus_explosion_right`
#### **Beschrijving**
De functie [`l3758_bonus_explosion_right`](../../alien_logic.c#L114-L126) (Z80 ROM: `$3772–$3792`) tekent het rechterdeel van de uitwaaierende bonusexplosie op het scherm.

#### **Context & Aanroep**
Aangeroepen vanuit `l3758_bonus_explosion_animation` tijdens oneven frames.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
  - [`drawNx2`](sprite-rendering.md#drawnx2) — [`sprite_rendering.c:L30`](../../sprite_rendering.c#L30)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l3758_bonus_explosion_animation`](#l3758_bonus_explosion_animation) — [`alien_logic.c:L187`](../../alien_logic.c#L187)

#### **Stap-voor-stap werking**
1. **Schermadres berekenen:** Berekent `target = de - a`.
2. **Grenscontrole:** Controleert `target + 0xBFA0 <= 0xFFFF` (Z80 `RET NC`). Indien ongeldig, breekt af.
3. **Buffer schonen & tekenen:** Wist 2 bytes op het startadres (`mem_write(target, 0)`), past de offset aan met `-33` (`0xFFDF`) en tekent de 3x2 tegelmatrix vanaf ROM-tegel `0x17D6` via `drawNx2`.

---

### `l37b0_print_bonus_score`
#### **Beschrijving**
De functie [`l37b0_print_bonus_score`](../../alien_logic.c#L135-L156) (Z80 ROM: `$37B0–$37C6`) drukt de behaalde bonusscorepunten af op de exacte positie van de explosie.

#### **Context & Aanroep**
Aangeroepen vanuit `l3758_bonus_explosion_animation` tijdens even frames.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
  - [`left_one_column`](utilities.md#left_one_column) — [`utilities.c:L45`](../../utilities.c#L45)
  - [`right_one_column`](utilities.md#right_one_column) — [`utilities.c:L50`](../../utilities.c#L50)
  - [`print_number`](utilities.md#print_number) — [`utilities.c:L80`](../../utilities.c#L80)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l3758_bonus_explosion_animation`](#l3758_bonus_explosion_animation) — [`alien_logic.c:L177`](../../alien_logic.c#L177)

#### **Stap-voor-stap werking**
1. **Scorebyte uitlezen:** Haalt de scorebyte op uit `hl + 1`.
2. **BCD-correctie (DAA simulatie):**
   - `if ((a & 0x0F) > 0x09) a += 0x06;`
   - `if (a > 0x99) a += 0x60;`
3. **Schermpositie bepalen:** Haalt het schermankeradres `de` op uit `hl + 2` en `hl + 3`.
4. **Cijfers afdrukken:** Verschuift 1 kolom naar rechts (`right_one_column`), schrijft een vaste `'0'` (tegel `0x20`) voor het meest rechtse cijfer, verschuift 1 kolom naar links (`left_one_column`) en roept `print_number(de, score_addr, 2)` aan om de 2 BCD-scorecijfers af te drukken.

---

### `l37cc_erase_bonus_explosion`
#### **Beschrijving**
De functie [`l37cc_erase_bonus_explosion`](../../alien_logic.c#L82-L93) (Z80 ROM: `$37CC–$37E5`) wist een complete schermkolom (26 rijen) van het voorgrondscherm zodra de bonusexplosieteller 0 bereikt.

#### **Context & Aanroep**
Aangeroepen aan het einde van de bonusexplosie door `l3758_bonus_explosion_animation`.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l3758_bonus_explosion_animation`](#l3758_bonus_explosion_animation) — [`alien_logic.c:L172`](../../alien_logic.c#L172)

#### **Stap-voor-stap werking**
1. **Voorgrondkolom bepalen:** Haalt het LSB van het schermadres uit `hl + 3` en berekent het voorgrondscherm-adres `0x4300 | ((a & 0x1F) + 0x20)`.
2. **Kolom wissen:** Doorloopt een lus van 26 stappen (`0x1A` rijen). In elke stap worden 2 opeenvolgende bytes op 0 gezet (`mem_write(addr, 0)`), waarna het adres met `-33` (`0xFFDF`) verminderd wordt om de volledige verticale kolom te wissen.

---

## 3. Scherm- & RAM-updates

### `alien_data_controller`
#### **Beschrijving**
De functie [`alien_data_controller`](../../alien_logic.c#L274-L283) (Z80 ROM: `$0A50–$0A6B`) stuurt het verversen van de grafische voorgrond- RAM voor alle aliens aan.

#### **Context & Aanroep**
Aangeroepen in de hoofd-gameloop:
```c
alien_data_controller();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `update_screen_objects` — [`hw_video_audio.c`](../../hw_video_audio.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_play_frame_update`](state-play.md#state_play_frame_update) — [`state_play.c:L125`](../../state_play.c#L125)

#### **Stap-voor-stap werking**
Doorloopt een lus van 20 iteraties (voor 16 aliens + extra entiteiten) over twee parallelle geheugenbuffers:
- `bc = 0x4B70` (grid control structure)
- `de = 0x4BB0` (screen RAM structure)
Roept per iteratie `update_screen_objects(bc, de)` aan en verhoogt beide pointers met 4 bytes (`bc += 4`, `de += 4`).

---

### `get_screen_ram_address_for_all_aliens`
#### **Beschrijving**
De functie [`get_screen_ram_address_for_all_aliens`](../../alien_logic.c#L290-L320) (Z80 ROM: `$0A6C–$0A99`) berekent de video-RAM adressen voor alle actieve aliens en onderhoudt de positie-historie.

#### **Context & Aanroep**
Aangeroepen voorafgaand aan het tekenen van het scherm.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
  - `get_screen_ram_address` — [`hw_video_audio.c`](../../hw_video_audio.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_play_frame_update`](state-play.md#state_play_frame_update) — [`state_play.c:L126`](../../state_play.c#L126)

#### **Stap-voor-stap werking**
1. **Lusspectrum:** Doorloopt 20 slots vanaf `bc = 0x4B70` en `de = 0x4BB3`.
2. **Statuscontrole:** Leest Controlstate A (`mem_read(bc)`). Controleert of bits 3 of 4 actief zijn (`(a & 0x18) != 0`).
3. **Positiehistorie verschuiven:** Verschuift het adresverleden in RAM 2 bytes terug: leest de bytes op `4BB3` en `4BB2` en schrijft deze naar `4BB1` en `4BB0`.
4. **Nieuw adres berekenen:** Roept `get_screen_ram_address(bc + 2, de - 1)` aan om de nieuwe coördinaten om te zetten naar een video-RAM adres op `4BB2/4BB3`.
5. **Pointer ophooging:** Verhoogt beide pointers met 4 bytes (`bc += 4`, `de += 4`).

---

## 4. Beweging & Frame-animaties

### `alien_movement_update`
#### **Beschrijving**
De functie [`alien_movement_update`](../../alien_logic.c#L335-L375) (Z80 ROM: `$0D1C–$0D67`) werkt de X/Y schermposities van alle vliegende aliens bij volgens hun toegewezen richtingsvectoren.

#### **Context & Aanroep**
Aangeroepen in de bewegingsfase van de game loop.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `phoenix_alien_movement_byte` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - `phoenix_alien_direction_vectors` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L40`](../../alien_wave.c#L40)

#### **Stap-voor-stap werking**
1. **Lusspectrum:** Scant 16 aliens (`0x4B50 + i*2` voor patroonpointer, `0x4B70 + i*4` voor coördinaten).
2. **Vliegbit controle:** Slaat aliens over waarvan bit 3 van Control A niet actief is (`(ctrl & 0x08) == 0`).
3. **Vliegroute uitlezen:** Haalt het 16-bit patroonadres op (big-endian) en bepaalt de bewegingsindex via `phoenix_alien_movement_byte(pattern)`.
4. **Richtingsvector opzoeken:** Voert een bitrotatie uit (`RLCA`: `(idx << 1) | (idx >> 7)`) en haalt de richtingsvectoren voor X en Y op uit `phoenix_alien_direction_vectors`.
5. **Coördinaten bijwerken:** Past X-coördinaat (`grid + 2`) en/of Y-coördinaat (`grid + 3`) aan.
6. **Rastergrensovergang:** Als de bijgewerkte coördinaat een 8-pixel rastergrens passeert (`(a & 0x07) == 0`), wordt het LSB van de patroonpointer verhoogd (`mem_write(ptr_addr + 1, ... + 1)`), waardoor de alien overstapt naar het volgende route-segment.

---

### `alien_animation_update`
#### **Beschrijving**
De functie [`alien_animation_update`](../../alien_logic.c#L382-L449) (Z80 ROM: `$0D70–$0DB5`, `$0DBB–$0DC6`, `$0DCC–$0DEE`) bepaalt de juiste sprite-animatieframe voor elke vliegende alien op basis van diens positie en vliegrichting.

#### **Context & Aanroep**
Aangeroepen in de animatiefase van de game loop.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `phoenix_alien_movement_byte` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - `phoenix_alien_shape_offset_page` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L41`](../../alien_wave.c#L41)

#### **Stap-voor-stap werking**
1. **Lusspectrum:** Scant 16 aliens (`bc = 0x4B70`, `hl = 0x4B50`).
2. **Patrooncontrole:** Indien actief (`ctrl_a & 0x08`): leest patroonindex. Bij einde van een patroon (index 0) retarget de functie de pointer naar `state.M4394:M4395`.
3. **Animatie-offset:** Berekent de animatie-offset `0xA0 + (list_index * 3)` in `phoenix_alien_shape_offset_page`. Schrijft de bijgewerkte Controlstate A weg.
4. **Sprite-shape bepalen:** Evalueert `anim_byte2` uit de tabel:
   - `0x01` (`L0DBB`): Gecombineerde Y/X-afhankelijke berekening (`res_a = x + y + anim_byte3`).
   - `0x02` (`L0DCC`): X-afhankelijke berekening (`res_a = x + anim_byte3`).
   - Anders (`0x04`): Y-afhankelijke berekening (`res_a = y + anim_byte3`).
5. **Controlstate B bijwerken:** Haalt het uiteindelijke tegel/shape ID op uit `phoenix_alien_shape_offset_page[res_a]` en slaat dit op in Controlstate B (`bc + 1`).

---

## 5. Breakout, Bomb-drop & Pattern Schedulers

### `l3264`
#### **Beschrijving**
De functie [`l3264`](../../alien_logic.c#L459-L493) (Z80 ROM: `$3264–$32AF`) roteert de startwaarde-pointer voor alien-bewegingen en herricht vliegende aliens naar nieuwe bewegingsroutes.

#### **Context & Aanroep**
Aangeroepen door de breakout scheduler bij vliegroute-veranderingen.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L42`](../../alien_wave.c#L42)

#### **Stap-voor-stap werking**
1. **LSB roteren:** Slaat het oude LSB op in `state.M4356` en verhoogt `state.M4395` modulo 16 (`(old_lsb + 1) & 0x0F`).
2. **Pass controle:** Voert de retarget-scan pas uit zodra `state.M4350` de waarde 5 bereikt (reset de teller daarna naar 0).
3. **Patroontabel scannen:** Doorloopt de patroonpointer-tabel op `0x4B50..0x4B6F` voor `state.M4353` paaren.
4. **Retargeting:** Vervangt alle pointers die matchen met het oude patroon `state.M4394:M4356` door het nieuwe patroon `state.M4351:M4352`.

---

### `l3074_breakout_delay`
#### **Beschrijving**
De functie [`l3074_breakout_delay`](../../alien_logic.c#L501-L518) (Z80 ROM: `$3074–$30A8`) berekent dynamisch de wachttijd (vertraging) voor de breakout- en bomb-drop schedulers.

#### **Context & Aanroep**
Hulpfunctie voor de schedulers `l3028` en `l30ba`. Hoe hoger het level of hoe minder aliens er over zijn, hoe korter de vertraging (snellere aanvallen).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`get_random_number`](utilities.md#get_random_number) — [`utilities.c:L15`](../../utilities.c#L15)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l3028`](#l3028) — [`alien_logic.c:L550`](../../alien_logic.c#L550)
  - [`l30ba`](#l30ba) — [`alien_logic.c:L580`](../../alien_logic.c#L580)

#### **Formule & Werking**
1. `c = 7 - ((LevelAndRound >> 1) & 0x07)` (vertraging vermindert bij hogere levels).
2. `c += 7 - ((a >> 4) & 0x07)` (vertraging vermindert bij hogere rondes, gecapped op `$70`).
3. `c += (AliensLeft < 5) ? 0x10 : (AliensLeft - 5)` (minder dan 5 aliens voegt een vaste offset toe).
4. `c += get_random_number() & 0x07` (voegt 0 tot 7 willekeurige ruis toe).

---

### `l3028`
#### **Beschrijving**
De functie [`l3028`](../../alien_logic.c#L528-L554) (Z80 ROM: `$3028–$3059`, `$305C–$306D`) is de **Breakout Scheduler**. Deze beheert wanneer en hoeveel aliens uit de formatie losbreken voor een aanvalsgolf.

#### **Context & Aanroep**
Periodiek aangeroepen vanuit de game loop.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l3074_breakout_delay`](#l3074_breakout_delay) — [`alien_logic.c:L550`](../../alien_logic.c#L550)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L43`](../../alien_wave.c#L43)

#### **Stap-voor-stap werking**
1. **Grenzen testen:** Breekt direct af indien er reeds 3 of meer aliens in de breakout-golf vliegen (`state.M4357 >= 3`) of als er een pass actief is (`state.M4350 >= 4`).
2. **Timer aftellen:** Als timer `state.M4358 != 0`: telt af. Zodra deze 0 bereikt, wordt de retarget-pass gewapend:
   - `state.M4357++`, `state.M4350 = 0x04`, `state.M4353 = 0x10`, `state.M4354 = 0x50`, `state.M4351 = 0x2E`.
   - Inspecteert speler X-pariteit (`state.PlayerShipX & 0x01`): als de pariteit even is, wordt patroon LSB `M4352 = 0x40`, anders `0x00`.
3. **Nieuwe aftelling inplannen:** Indien `M4358 == 0`: berekent en plant het volgende aftelmoment in via `l3074_breakout_delay()`.

---

### `l30ba`
#### **Beschrijving**
De functie [`l30ba`](../../alien_logic.c#L562-L599) (Z80 ROM: `$30BA–$30D8`, `$30E4–$310F`, `$3112–$3121`) is de **Bomb-drop Scheduler**. Deze beheert de tijdsintervallen en slots voor het gooien van bommen door aliens.

#### **Context & Aanroep**
Periodiek aangeroepen vanuit de game loop.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l3074_breakout_delay`](#l3074_breakout_delay) — [`alien_logic.c:L580`](../../alien_logic.c#L580)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L44`](../../alien_wave.c#L44)

#### **Stap-voor-stap werking**
1. **Bom-timers aftellen:** Telt drie per-bom aftelslots af (`state.M4359`, `state.M435A`, `state.M435B`).
2. **Pass controle:** Indien `state.M4350 != 0` (er is al een pass gewapend), breekt af.
3. **Drop-pass wapenen:** Als timer `state.M4355 != 0`: telt af; op 0 wordt `state.M4350 = 0x01` ingesteld om het bomwerpen te starten.
4. **Nieuwe vertraging berekenen:** Indien `M4355 == 0`: berekent de nieuwe vertraging via `l3074_breakout_delay()`, past deze aan op basis van `state.Counter9A`, halveert de vertraging voor elk vrij bom-slot en stelt `state.M4355` in.

---

### `l3124`
#### **Beschrijving**
De functie [`l3124`](../../alien_logic.c#L607-L620) (Z80 ROM: `$3124–$314E`) vormt **Pattern Retarget Fase 1 -> 2**.

#### **Context & Aanroep**
Onderdeel van de 6-fasen state machine voor patroonherrichting.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`get_random_number`](utilities.md#get_random_number) — [`utilities.c:L15`](../../utilities.c#L15)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L45`](../../alien_wave.c#L45)

#### **Stap-voor-stap werking**
Indien `state.M4350 == 1`, schakelt de functie over naar fase 2 (`state.M4350 = 2`). Berekent het aantal te scannen patroonparen `state.M4353` op basis van het rondenummer (`((LevelAndRound >> 2) & 0x0F) + 5`, begrensd op 5) verminderd met het aantal vliegende aliens `M4357` en een willekeurige waarde.

---

### `l315a`
#### **Beschrijving**
De functie [`l315a`](../../alien_logic.c#L629-L653) (Z80 ROM: `$315A–$318E`, `$3192–$31AD`) vormt **Pattern Retarget Fase 2 -> 3**.

#### **Context & Aanroep**
Onderdeel van de 6-fasen state machine.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`get_random_number`](utilities.md#get_random_number) — [`utilities.c:L15`](../../utilities.c#L15)
  - [`mem_read`](utilities.md#mem_read) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L46`](../../alien_wave.c#L46)

#### **Stap-voor-stap werking**
Indien `state.M4350 == 2`, zoekt de functie vanaf een willekeurige alien-index door het geheugen naar de eerste actieve alien waarvan het bewegingspatroon nog overeenkomt met het oude patroon `state.M4394:M4356`. Slaat de gevonden positie op in `state.M4354` en schakelt over naar fase 3 (`state.M4350 = 3`).

---

### `l31b4`
#### **Beschrijving**
De functie [`l31b4`](../../alien_logic.c#L662-L710) (Z80 ROM: `$31B4–$320D`, `$3210–$3228`) vormt **Pattern Retarget Fase 3 -> 5**. Deze selecteert een nieuw gesloten-lus bewegingspatroon voor de geselecteerde alien.

#### **Context & Aanroep**
Onderdeel van de 6-fasen state machine.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`get_random_number`](utilities.md#get_random_number) — [`utilities.c:L15`](../../utilities.c#L15)
  - `phoenix_alien_distance_bands` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - `phoenix_alien_pattern_selectors` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - `phoenix_alien_closed_loop_pointers` — [`phoenix_tables.c`](../../phoenix_tables.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L47`](../../alien_wave.c#L47)

#### **Stap-voor-stap werking**
1. **Alien posities uitlezen:** Haalt de X- en Y-coördinaten op van de gekozen alien (`state.M4354`).
2. **Afstand tot speler:** Berekent de afstand en relatieve positie (links of rechts) ten opzichte van `state.PlayerShipX`.
3. **Patroon-tabellen raadplegen:** Berekent de afstandsband via `phoenix_alien_distance_bands` en bepaalt de index in `phoenix_alien_pattern_selectors`.
4. **Nieuw patroon instellen:** Haalt het nieuwe MSB/LSB paar op uit `phoenix_alien_closed_loop_pointers`. Slaat de nieuwe patroonpointer op in `state.M4351` en `state.M4352` en schakelt over naar fase 5 (`state.M4350 = 5`).

---

### `l322c`
#### **Beschrijving**
De functie [`l322c`](../../alien_logic.c#L718-L730) (Z80 ROM: `$322C–$325E`) vormt **Pattern Retarget Fase 4 -> 6**. Deze voert een synchronisatiecontrole uit.

#### **Context & Aanroep**
Onderdeel van de 6-fasen state machine.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_read`](utilities.md#mem_read) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L48`](../../alien_wave.c#L48)

#### **Stap-voor-stap werking**
Controleert of *alle* actieve aliens op het veld reeds op het oude patroon `M4394:M4356` vliegen. Indien zelfs maar één actieve alien een afwijkend patroon heeft, breekt de functie direct af. Als alle aliens gesynchroniseerd zijn, wordt fase 6 ingesteld (`state.M4350 = 6`).

---

## 6. Aanvalslogica & Dive-bomb Triggers

### `l2560`
#### **Beschrijving**
De functie [`l2560`](../../alien_logic.c#L778-L794) (Z80 ROM: `$2560–$2595`) scant 8 kandidaat-aliens om te bepalen of een alien een gerichte duikvluchtaanval mag inzetten.

#### **Context & Aanroep**
Aanvalscontrole vanuit de game loop:
```c
l2560();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l2596`](#l2596) — [`alien_logic.c:L790`](../../alien_logic.c#L790)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`alien_wave_update`](alien-wave.md#alien_wave_update) — [`alien_wave.c:L50`](../../alien_wave.c#L50)

#### **Stap-voor-stap werking**
1. **RAM-blok selecteren:** Selecteert de te scannen RAM-basis (`0x4B70` of `0x4B90`) afhankelijk van frame-teller bit `state.Counter93 & 0x01`.
2. **Kaders berekenen:** Berekent dynamische afstandsgrenzen op basis van `state.M4357`, `state.M439E` en `state.M439F`.
3. **Kandidaten scannen:** Doorloopt 8 kandidaten en roept per kandidaat [`l2596`](#l2596) aan. Stopt direct bij de eerste geslaagde kandidaat.

---

### `l2596`
#### **Beschrijving**
De functie [`l2596`](../../alien_logic.c#L744-L769) (Z80 ROM: `$2596–$25B6`) voert de individuele geschiktheidscontrole uit van één alien voor een duikvlucht.

#### **Context & Aanroep**
Aangeroepen door `l2560` voor elke kandidaat-alien.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `l25b7` — [`weapon_collision.c:L100`](../../weapon_collision.c#L100) / [`weapon-collision.md#l25b7`](weapon-collision.md#l25b7)
  - [`mem_read`](utilities.md#mem_read) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`l2560`](#l2560) — [`alien_logic.c:L790`](../../alien_logic.c#L790)

#### **Stap-voor-stap werking & Voorwaarden**
1. **Actief bit:** Controleert of bit 3 in Controlstate A actief is (`a & 0x08 != 0`); zo niet, retourneert `false`.
2. **Sprite-shape:** Controleert of de sprite-vorm binnen de geldige grenzen valt (`a != 0x08` en `a < 0x88`); zo niet, retourneert `false`.
3. **X-positie venster:** Controleert of de X-coördinaat binnen het venster `[b, c[` valt.
4. **Y-positie venster:** Controleert of de Y-coördinaat binnen het venster `[0x80, d[` valt.
5. **Aanval starten:** Indien aan alle 4 voorwaarden voldaan is, roept de functie `l25b7(new_b, new_c)` aan om een vijandelijke kogel/aanvalsslot te claimen en retourneert `true`.
