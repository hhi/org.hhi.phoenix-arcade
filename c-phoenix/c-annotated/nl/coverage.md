# Test Coverage & Verification (`coverage.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de functies in [`coverage.c`](../../coverage.c). Deze module verzorgt de runtime-instrumentatie, lockstep-verificatie en dekkingsstatistieken voor de geporteerde C-codebases.

---

## 1. Instrumentatie & Dekking System

### `coverage_hit` & `coverage_observe_frame`
#### **Beschrijving**
- [`coverage_hit`](../../coverage.c#L67-L84): Wordt aangeroepen op kritieke logische locaties in de code (bijv. kogeltreffers, speler dood, schildgebruik) om de uitvoering te tellen en op te slaan per frame.
- [`coverage_observe_frame`](../../coverage.c#L92-L100): Analyseert per frame de Phoenix-status (`state.GameState`, `state.LevelAndRound`, spelerlevens) ten behoeve van geautomatiseerde lockstep-testen tegen de Java- en Z80-emulatoren.
- `coverage_dump_json`: Schrijft een JSON-rapport met de behaalde dekkings-statistieken naar schijf bij het afsluiten van de game.

#### **Knowledge Graph Koppelingen**
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - Vrijwel alle C-bestanden in `c-phoenix` (`alien_logic.c`, `player_logic.c`, `weapon_collision.c`, etc.).
