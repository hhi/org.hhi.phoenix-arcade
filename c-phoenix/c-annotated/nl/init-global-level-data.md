# Global Level Data Init (`init_global_level_data.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de functie in [`init_global_level_data.c`](../../init_global_level_data.c). Deze module initialiseert de globale niveaudata voor elke ronde en level.

---

## 1. Globale Niveau Initialisatie

### `init_global_level_data`
#### **Beschrijving**
De functie [`init_global_level_data`](../../init_global_level_data.c#L7-L17) (Z80 ROM: `$0580–$0595`) haalt 12 configuratiebytes op uit `phoenix_level_data_page` en kopieert deze naar de interne spelstatus `state.M43AB`.

#### **Context & Aanroep**
Aangeroepen bij level-initialisatie in GameState 2 en attract mode:
```c
init_global_level_data();
```

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `phoenix_level_data_pointer_table` — [`phoenix_tables.c`](../../phoenix_tables.c)
  - `phoenix_level_data_page` — [`phoenix_tables.c`](../../phoenix_tables.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_2_init_game_and_level_data`](state-init.md#state_2_init_game_and_level_data) — [`state_init.c#L75`](../../state_init.c#L75)
  - [`splash_and_demo`](attract-mode.md#splash_and_demo) — [`attract_mode.c#L76`](../../attract_mode.c#L76)

#### **Stap-voor-stap werking**
1. **Pointer opzoeken:** Berekent de index `state.LevelAndRound & 0x0F` en zoekt de tabel-offset op in `phoenix_level_data_pointer_table`.
2. **Data kopiëren:** Kopieert 12 opeenvolgende bytes vanaf de opgehaalde ROM-pagina naar de geheugengebieden vanaf `state.M43AB`.
