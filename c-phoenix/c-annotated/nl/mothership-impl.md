# Mothership Implementation (`mothership_impl.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de functies in [`mothership_impl.c`](../../mothership_impl.c). Deze module behandelt de tegel-inslag detectie, het doorboren van het moederschip-schild en de activatie van de moederschip-explosie.

---

## Inhoudsopgave
1. [Tegel-inslagen & Kern-activatie](#1-tegel-inslagen--kern-activatie)
2. [Explosietellers & Scroll-sync](#2-explosietellers--scroll-sync)

---

## 1. Tegel-inslagen & Kern-activatie

### `l2351_mothership_animation`
#### **Beschrijving**
De functie [`l2351_mothership_animation`](../../mothership_impl.c#L12-L123) (Z80 ROM: `$2351–$23C7`) verwerkt kogel-inslagen op de schildtegels van het moederschip en detecteert voltreffers in de moederschipkern.

#### **Context & Aanroep**
Aangeroepen bij kogeltreffers op het moederschip in level 5.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`coverage_hit`](coverage.md#coverage_hit) — [`coverage.c:L12`](../../coverage.c#L12)
  - `phoenix_mothership_explosion_pointers` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - [`mem_read`](utilities.md#mem_read) / [`mem_write`](utilities.md#mem_write) — [`utilities.c:L22`](../../utilities.c#L22)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - `process_player_bullet_vs_mothership` — [`weapon_collision.c`](../../weapon_collision.c)

#### **Geheugen- & Structuur-context**
- `state.M4366`: Vlag ingesteld op `0xFF` bij schade aan het moederschip.
- `state.GameState`: Wordt gezet op `GAME_STATE_MOTHERSHIP_EXPLODING` bij een dodelijke treffer op de kern.
- `state.CounterA5`: Explosieduur-teller (ingesteld op `0x60`).
- `state.ParticleExplosion`: Deeltjesexplosie-vlag (ingesteld op `0xFF`).

#### **Stap-voor-stap werking**
1. **Statuscontrole:** Breek af als de kogel/object-status bit 3 inactief is (`(a & 0x08) == 0`).
2. **Tegeladres berekenen:** Houdt rekening met de horizontale scrollpositie (`state.CounterB9 >> 3`) om de getroffen tegel in het VRAM te lokaliseren.
3. **Schild-schade (`tile == 0x4C`):** De kogel stuit af op de buitenste schildlaag; wist bit 3 van de kogelstatus en verlaagt de tegelwaarde in RAM naar `0x4B` of wis naar `0x00`.
4. **Kern-treffer (`tile == 0x60`):** Controleert of de kogel door de schildopening het zwakke punt van de moederschipkern raakt:
   - Als het hekwerk geopend is (`gate == 0x70`): Activeert de fatale explosie `state.GameState = GAME_STATE_MOTHERSHIP_EXPLODING`, zet de teller `state.CounterA5 = 0x60` en start de deeltjesexplosie `state.ParticleExplosion = 0xFF`.
   - Anders: Verwerkt gewone beschadiging en vervangt de tegel via `phoenix_mothership_explosion_pointers`.

---

## 2. Explosietellers & Scroll-sync

### `update_counters_for_mothership_explosion`
#### **Beschrijving**
De functie [`update_counters_for_mothership_explosion`](../../mothership_impl.c#L134-L156) (Z80 ROM: `$242C–$2442`) update de scrollregisters en telt de explosieteller `state.CounterA5` af tijdens de moederschip-explosie.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `hw_write_scroll_register` — [`hw_video_audio.c`](../../hw_video_audio.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`level_1_3_B_player_alive_aliens`](state-play.md#level_1_3_b_player_alive_aliens) — [`state_play.c#L16`](../../state_play.c#L16)

#### **Stap-voor-stap werking**
1. **Scroll-uitlijning:** Lijnt `state.CounterB9` uit op 8-pixel grenzen (`& 0xF8`) en roept `hw_write_scroll_register` aan.
2. **Scherm-pointer:** Berekent het aangepaste schermadres `de = 0x41C6` gecorrigeerd voor de scroll-offset.
3. **Teller aftellen:** Verlaagt `state.CounterA5--` en retourneert de resterende explosietijd.
