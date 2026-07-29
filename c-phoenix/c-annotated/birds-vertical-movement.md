# Birds Vertical Movement (`birds_vertical_movement.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`birds_vertical_movement.c`](../birds_vertical_movement.c). Deze module beheert de verticale golf- en scrollbewegingen van de vogelformatie via de hardware-scrollregisters.

---

## Inhoudsopgave
1. [Hoofd-scroll & Verticale Beweging](#1-hoofd-scroll--verticale-beweging)
2. [Snelheids- & Formatie-analyse](#2-snelheids--formatie-analyse)
3. [Klim- & Aftelschedulers](#3-klim--aftelschedulers)

---

## 1. Hoofd-scroll & Verticale Beweging

### `birds_vertical_movement_update`
#### **Beschrijving**
De functie [`birds_vertical_movement_update`](../birds_vertical_movement.c#L112-L142) (Z80 ROM: `$2600–$2664`) stelt de verticale scrollwaarde van de vogel-laag in via het hardware-register `hw_write_scroll_register`.

#### **Context & Aanroep**
Aangeroepen in elke frame-update van de vogelgolf:
```c
birds_vertical_movement_update();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `hw_write_scroll_register` — [`hw_video_audio.c`](../hw_video_audio.c)
  - `phoenix_bird_scroll_steps` — [`phoenix_tables.c`](../phoenix_tables.c)
  - [`l2668`](#l2668) — [`birds_vertical_movement.c#L137`](../birds_vertical_movement.c#L137)
  - [`l26aa`](#l26aa) — [`birds_vertical_movement.c#L138`](../birds_vertical_movement.c#L138)
  - [`l26d0`](#l26d0) — [`birds_vertical_movement.c#L140`](../birds_vertical_movement.c#L140)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`process_birds`](bird-logic.md#process_birds) — [`bird_logic.c#L31`](../bird_logic.c#L31)

#### **Stap-voor-stap werking**
1. **Scroll-band berekening:** Berekent `state.B4BD2 = (((uint8_t)~state.CounterB9) >> 3) & 0x1F` voor botsingscontroles.
2. **Klimmen of Dalen:**
   - Als `state.B4BD1 < state.B4BD3`: Formatie klimt (`CounterB9 += scroll_step`).
   - Anders: Formatie daalt (`CounterB9 -= scroll_step`) op basis van dalingssnelheid `state.B4BD5`.
3. **Hardware schrijven:** Schrijft de nieuwe positie `state.CounterB9` weg via `hw_write_scroll_register(a)`.
4. **Interleaved updates:** 
   - Oneven frames (`state.Counter9B & 1`): Herberekenen snelheid ([`l2668`](#l2668)) en klim-timer ([`l26aa`](#l26aa)).
   - Even frames: Rescannen de formatie-hoogte ([`l26d0`](#l26d0)).

---

## 2. Snelheids- & Formatie-analyse

### `l2668`
#### **Beschrijving**
De functie [`l2668`](../birds_vertical_movement.c#L15-L27) (Z80 ROM: `$2668–$26A7`) berekent de dalingssnelheid `state.B4BD5` op basis van de moeilijkheidsgraad, het aantal resterende aliens (`AliensLeft`) en vogels (`BirdsLeft`).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `phoenix_bird_descent_caps` — [`phoenix_tables.c`](../phoenix_tables.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`birds_vertical_movement_update`](#birds_vertical_movement_update) — [`birds_vertical_movement.c#L137`](../birds_vertical_movement.c#L137)

---

### `l26d0`
#### **Beschrijving**
De functie [`l26d0`](../birds_vertical_movement.c#L36-L51) (Z80 ROM: `$26D0–$26FD`) scant de 8 vogel-slots (van slot 7 terug naar slot 0) om de posities `state.B4BD6` (formatie-positie) en `state.B4BD7` (formatie-hoogte) te bepalen.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`mem_read`](utilities.md#mem_read) — [`utilities.c:L22`](../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`birds_vertical_movement_update`](#birds_vertical_movement_update) — [`birds_vertical_movement.c#L140`](../birds_vertical_movement.c#L140)

---

## 3. Klim- & Aftelschedulers

### `l26aa`
#### **Beschrijving**
De functie [`l26aa`](../birds_vertical_movement.c#L60-L102) (Z80 ROM: `$26AA–$26CC`, `$2476–$2493`, `$2495–$249F`) beheert de aftelteller `state.B4BD3` en wapent de klimdrempel `state.B4BD1` zodra de formatie zich binnen de hoogteband 8..15 bevindt.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - Geen (inspecteert en schrijft `state` variabelen)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`birds_vertical_movement_update`](#birds_vertical_movement_update) — [`birds_vertical_movement.c#L138`](../birds_vertical_movement.c#L138)
