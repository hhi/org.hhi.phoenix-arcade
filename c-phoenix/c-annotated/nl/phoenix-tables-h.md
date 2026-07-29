# ROM Tables Header (`phoenix_tables.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de ROM-tabel declaraties in [`phoenix_tables.h`](../../phoenix_tables.h). Dit bestand verklaart alle statische data-arrays die uit het originele Arcade ROM zijn geëxtraheerd.

---

## Inhoudsopgave
1. [Belangrijkste Externe Arrays](#1-belangrijkste-externe-arrays)
2. [Knowledge Graph Koppelingen](#2-knowledge-graph-koppelingen)

---

## 1. Belangrijkste Externe Arrays

- `extern const uint8_t phoenix_player_init_data[0x20]`: Standaard startdata voor speler- en kogelslots.
- `extern const uint8_t phoenix_level_data_pointer_table[0x10]` / `phoenix_level_data_page[0x30]`: Levelconfiguratie tabellen.
- `extern const uint8_t phoenix_player_x_position_mapping[0x10]`: X-positie botsingsgrenzen mapping.
- `extern const uint8_t phoenix_alien_movement_cluster_a[0x400]` / `b[0x400]`: Vliegpatronen van de alien-zwermen.
- `extern const uint8_t phoenix_bird_behaviour_scripts[0x100]`: AI-gedragstabellen voor vogels.
- `extern const uint8_t phoenix_mothership_explosion_pointers[0x60]`: Tegel-pointers voor moederschip- en spelersexplosies.

---

## 2. Knowledge Graph Koppelingen

#### **Knowledge Graph Koppelingen**
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`phoenix_tables.c`](phoenix-tables.md)
  - [`alien_logic.c`](alien-logic.md)
  - [`bird_logic.c`](bird-logic.md)
  - [`player_logic.c`](player-logic.md)
