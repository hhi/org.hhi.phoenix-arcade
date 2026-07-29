# Game Constants & Enums (`game_constants.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de constanten en enums in [`game_constants.h`](../../game_constants.h). Dit bestand bevat de toestandscoderingen van de game state machine en de 12 levelpatronen.

---

## Inhoudsopgave
1. [PhoenixGameState Enum ($43A4)](#1-phoenixgamestate-enum-43a4)
2. [Level- & Ronde-Patronen ($43B8)](#2-level---ronde-patronen-43b8)
3. [Speler- & Schild-constanten](#3-speler---schild-constanten)

---

## 1. PhoenixGameState Enum ($43A4)

### GameState Waarden
Opgeslagen in `state.GameState` en verwerkt door [`game_state_machine`](game-state-machine.md#game_state_machine):

| Waarde | Enum Naam | Omschrijving |
|---|---|---|
| `0x00` | `GAME_STATE_NEW_GAME` | Spelstart / Beurtwissel initiëren |
| `0x01` | `GAME_STATE_SCORE_FLASH` | Knipperende scoreweergave |
| `0x02` | `GAME_STATE_INIT_ROUND` | Initialisatie van level- en entiteitsdata |
| `0x03` | `GAME_STATE_PLAYING` | Actieve gameplay (sturing via level pattern) |
| `0x04` | `GAME_STATE_PLAYER_EXPLODING` | Animatie spelersexplosie |
| `0x05` | `GAME_STATE_GAME_OVER` | "GAME OVER" weergave en reset |
| `0x06` | `GAME_STATE_MOTHERSHIP_EXPLODING` | Explosie van het moederschip |
| `0x07` | `GAME_STATE_MOTHERSHIP_SCORE` | Moederschip scoreweergave |

---

## 2. Level- & Ronde-Patronen ($43B8)

### Level Patterns (`LEVEL_PATTERN_*`)
Geëxtraheerd uit de lage nibble van `state.LevelAndRound` (`& 0x0F`) en gedispatched in [`state_3_normal_game_play`](state-play.md#state_3_normal_game_play):

- `0x00`: `LEVEL_PATTERN_ALIENS_FADE_IN_0` (Alien golf 1 fade-in)
- `0x01`: `LEVEL_PATTERN_ALIENS_ACTIVE_1` (Alien golf 1 actieve zwerm)
- `0x02`: `LEVEL_PATTERN_ALIENS_FADE_IN_2` (Alien golf 2 fade-in)
- `0x03`: `LEVEL_PATTERN_ALIENS_ACTIVE_3` (Alien golf 2 actieve zwerm)
- `0x04`: `LEVEL_PATTERN_BIRDS_SPIRAL_4` (Spiraalvulling tussen-animatie)
- `0x05`: `LEVEL_PATTERN_BIRDS_FADE_IN_5` (Vogel golf 1 intro)
- `0x06`: `LEVEL_PATTERN_BIRDS_SPIRAL_6` (Spiraalvulling tussen-animatie)
- `0x07`: `LEVEL_PATTERN_BIRDS_FADE_IN_7` (Vogel golf 2 intro)
- `0x08`: `LEVEL_PATTERN_BIRDS_SPIRAL_8` (Spiraalvulling voor moederschip)
- `0x09`: `LEVEL_PATTERN_MOTHERSHIP_FADE_IN_9` (Moederschip verschijning)
- `0x0A`: `LEVEL_PATTERN_MOTHERSHIP_AND_ALIENS_A` (Moederschip & escort-aliens)
- `0x0B`: `LEVEL_PATTERN_ALIENS_ACTIVE_B` (Escort-aliens respawn wave)

---

## 3. Speler- & Schild-constanten

- `PLAYER_STATE_MOVEMENT_ENABLED` (`0x08`): Vlag die aangeeft dat de speler de joystick mag gebruiken.
- `SHIELD_DURATION_INITIAL` (`0xFF`): De initiële waarde van `state.ShieldCount` bij het activeren van het krachtveld.
