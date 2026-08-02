# Input-bot-referentie: elk target en elke optie

Wat elk target betekent, wat er nodig is om het te halen, en wat elke opdrachtregeloptie doet. Gegenereerd door `tools/generate_input_bot_reference.py` uit de `TARGETS`-tabel en de argparse-definities in `input_bot.py` — niet met de hand aanpassen. Voor de werkwijze zelf, zie [input-bot-howto.nl.md](input-bot-howto.nl.md).

**Targets: 28** · **Opties: 26**

---

## Hoe een target wordt vastgesteld

Niets hier kijkt naar het beeld op het scherm. Een target wordt vastgesteld uit twee soorten bewijs die de port tijdens het spelen afgeeft:

1. **Sondes.** Een aanroep `coverage_hit("naam")` staat in de vertaalde routine, precies op de tak waar de gebeurtenis plaatsvindt. Het bewijst dat de port *die weg heeft afgelegd* — niet dat er een knop is ingedrukt. `two_player_turn_switch` vuurt bijvoorbeeld alleen op de tak die het spel teruggeeft vanaf speler twee, en alleen als `GameOrAttract == 0x02`, zodat de attract-demo hem niet kan afvinken.
2. **Frame-sampling.** `coverage_observe_frame()` draait één keer per frame en leest de spelstatus uit; daar komen tellers als `mothership_gameplay_frames` vandaan. Sommige waarden zijn afgeleid in plaats van gemeten: `player_deaths` is *spelstatus werd 4*, `level_transitions` is *LevelAndRound veranderde*.

Een sonde bewijst dat de code er langskwam; een frame-teller bewijst dat de toestand er was. Beide worden weggeschreven naar het bestand achter `--coverage-dump=`, en de voorwaarden hieronder lezen dat bestand.

Dit meet de **C-port**. Dat de originele ROM dezelfde tak neemt, blijkt hier niet uit — daarvoor is de lockstep-vergelijking. Het betekent ook dat een nieuw target niet van buitenaf te bedenken is: er moet eerst een sonde in de C-bron of een teller in de sampler bij.

---

## Een spel starten en tweespelermodus

| Target | Wat het betekent | Voorwaarde in de code | Gemeten in |
| --- | --- | --- | --- |
| `coin_accepted` | Er is een munt geaccepteerd. De kortst mogelijke controle dat invoer de machine überhaupt bereikt. | `hit(c, "coin_accepted")` | `attract_mode.c` → `decrement_coins()` |
| `player_2_bank_initialized` | De aparte RAM-bank van speler twee is opgezet. Bewijst dat de port twee onafhankelijke speltoestanden bijhoudt, geen één. | `hit(c, "player_2_bank_initialized")` | `attract_mode.c` → `prompt_for_start_game()` |
| `two_player_game_started` | Er is een tweespelerspel gestart. Zegt alleen dat het spel begon, niet dat beide spelers ook echt speelden. | `hit(c, "two_player_game_started")` | `attract_mode.c` → `decrement_coins()` |
| `two_player_turn_switch` | Het spel is werkelijk overgedragen van de ene speler aan de andere. Dit is de echte tweespelertest; de twee hierboven zijn de voorwaarden ervoor. | `hit(c, "two_player_turn_switch")` | `game_state_machine.c` → `state_0_new_game_start()` |

## De speler: schieten, schild, sterven

| Target | Wat het betekent | Voorwaarde in de code | Gemeten in |
| --- | --- | --- | --- |
| `enemy_bullets_active` | Er was vijandelijk vuur onderweg. Anders dan sterven: het betekent alleen dat de vijand terugschoot. | `summary(c, "enemy_bullet_active_frames") > 0` | frame-sampler in `coverage.c` |
| `game_over` | Alle levens waren op en het spel eindigde. Gebruik dit, niet player_death, als je de eindsequentie zelf nodig hebt. | `summary(c, "game_overs") > 0` | frame-sampler in `coverage.c` |
| `player_bullet_fired` | De speler heeft minstens één schot gelost. Een rooktest: mist dit, dan kwam de replay nooit voorbij het attract-scherm. | `hit(c, "spawn_player_bullet")` | `player_logic.c` → `spawn_player_bullet()` |
| `player_death` | De speler verloor een leven. Eén leven — het spel kan daarna gewoon doorgaan. | `summary(c, "player_deaths") > 0 or hit(c, "player_killed")` | frame-sampler in `coverage.c`, `weapon_collision.c` → `l0cc4_player_killed()` |
| `shield_used` | De schildknop is ingedrukt. Nodig voor alles wat de 4x4-schildsprite of de botsingsafhandeling ervan bestudeert. | `hit(c, "player_shield_pressed")` | `player_logic.c` → `move_player()` |

## Verder komen in het spel

| Target | Wat het betekent | Voorwaarde in de code | Gemeten in |
| --- | --- | --- | --- |
| `gameplay_level_5` | Ronde 5 gehaald in echt spel. Het eerste level waarvoor de zoektocht meestal meer dan één generatie nodig heeft. | `summary(c, "max_gameplay_level_and_round") >= 0x05` | frame-sampler in `coverage.c` |
| `gameplay_level_7` | Ronde 7 gehaald in echt spel. | `summary(c, "max_gameplay_level_and_round") >= 0x07` | frame-sampler in `coverage.c` |
| `gameplay_level_8` | Ronde 8 gehaald in echt spel. | `summary(c, "max_gameplay_level_and_round") >= 0x08` | frame-sampler in `coverage.c` |
| `gameplay_level_9` | Ronde 9 gehaald in echt spel. Het diepste ingebouwde target; reken op --generations en een lange --frames. | `summary(c, "max_gameplay_level_and_round") >= 0x09` | frame-sampler in `coverage.c` |
| `level_transition` | Het spel ging minstens één keer van de ene ronde naar de volgende. Het goedkoopste bewijs dat voortgang überhaupt werkt. | `summary(c, "level_transitions") > 0` | frame-sampler in `coverage.c` |

## Aliens en vogels

| Target | Wat het betekent | Voorwaarde in de code | Gemeten in |
| --- | --- | --- | --- |
| `alien_kill` | Een alien is vernietigd en scoorde punten. Scoren hoort bij de voorwaarde, dus een treffer die niets oplevert telt niet mee. | `hit(c, "alien_killed_with_score")` | `weapon_collision.c` → `l0ea4_with_score()` |
| `bird_hit` | Er is een vogel of ei geraakt, in welk groeistadium dan ook. Bewust breed — gebruik het om de vogelfase te bereiken, niet om vast te leggen welke vogel. | `hit(c, "small_bird_hit") or hit(c, "large_bird_or_egg_hit")` | `collision_detection.c` → `l3844_small_bird_hit()`, `collision_detection.c` → `l38bc_large_hit()` |
| `bird_wave_entry` | Er verscheen een vogelgolf op het scherm — ook tijdens de attract-demo, waar niemand speelt. | `summary(c, "bird_wave_frames") > 0` | frame-sampler in `coverage.c` |
| `bird_wave_gameplay` | Er verscheen een vogelgolf terwijl er werkelijk gespeeld werd. Gebruik deze voor fixtures; bird_wave_entry kan al door de demo worden afgevinkt. | `summary(c, "bird_wave_gameplay_frames") > 0` | frame-sampler in `coverage.c` |
| `grown_bird_bonus_explosion` | Een volgroeide vogel is vernietigd en keerde zijn bonus uit. De smalle tegenhanger van bird_hit. | `hit(c, "grown_bird_bonus_explosion")` | `collision_detection.c` → `l3844_small_bird_hit()` |

## Het moederschip, fase voor fase

| Target | Wat het betekent | Voorwaarde in de code | Gemeten in |
| --- | --- | --- | --- |
| `mothership_active` | Het moederschip stond op het scherm — attract-modus telt mee. Zelden wat je op zichzelf wilt. | `summary(c, "mothership_frames") > 0` | frame-sampler in `coverage.c` |
| `mothership_active_gameplay` | Het moederschip stond op het scherm tijdens echt spel. Hierop bouw je een moederschip-fixture. | `summary(c, "mothership_gameplay_frames") > 0` | frame-sampler in `coverage.c` |
| `mothership_core_gate_70` | De kernpoort op $70 stond open — het smalle moment waarop het moederschip werkelijk vernietigd kan worden. | `hit(c, "mothership_core_gate_70_seen")` | `mothership_impl.c` → `l2351_mothership_animation()` |
| `mothership_core_window` | De romp ging ver genoeg open om de kern bloot te leggen. Een voorwaarde voor de kill, niet de kill zelf. | `hit(c, "mothership_core_window_seen")` | `mothership_impl.c` → `l2351_mothership_animation()` |
| `mothership_explosion` | Het moederschip is vernietigd, of speltoestand 6 is bereikt. Het einde van de fasereeks hierboven. | `hit(c, "mothership_explosion_trigger") or game_state_seen(c, "6")` | `mothership_impl.c` → `l2351_mothership_animation()`, frame-sampler in `coverage.c` |
| `mothership_tile_4c_hit` | Specifiek karakter 0x4C is geraakt — de gladde buitenromp. Zie de rompsheet in animations/*/animation-sequences.md. | `hit(c, "mothership_tile_4c_hit")` | `mothership_impl.c` → `l2351_mothership_animation()` |
| `mothership_tile_60_hit` | Specifiek karakter 0x60 is geraakt — de motorrij langs het breedste deel van de romp. Moeilijker te bereiken dan 0x4C, en veel hoger gescoord. | `hit(c, "mothership_tile_60_hit")` | `mothership_impl.c` → `l2351_mothership_animation()` |
| `mothership_tile_hit` | Er is een romptegel van het moederschip weggeschoten. Breed: het zegt niet welk deel van de romp. | `hit(c, "mothership_tile_hit")` | `mothership_impl.c` → `l2351_mothership_animation()` |

## Score

| Target | Wat het betekent | Voorwaarde in de code | Gemeten in |
| --- | --- | --- | --- |
| `bonus_life_awarded` | De score is werkelijk over de bonuslevendrempel gegaan. Combineer met de tweespelertargets voor de geplande 2P-bonuslevenfixture. | `hit(c, "bonus_life_awarded")` | `scoring.c` → `update_scores_and_sound()` |

---

## Opdrachtregelopties

### `input_bot.py evaluate`

| Optie | Standaard | Wat het doet |
| --- | --- | --- |
| `--script` | verplicht | input script to replay |
| `--frames` | `8000` | frames to run |
| `--emulator` | `./build/c-phoenix` | emulator binary |
| `--cwd` | `.` | working directory for emulator |
| `--coverage-out` | verplicht | write/read coverage JSON at this path |
| `--ram-dump` | verplicht | optional RAM dump output path |
| `--sdl-video-driver` | verplicht | optional SDL_VIDEODRIVER override |
| `--no-render` | vlag | skip rendering during headless runs |
| `--json` | vlag | print raw coverage JSON |
| `--target` | `[]` | target to evaluate; can be repeated |

### `input_bot.py list-targets`

| Optie | Standaard | Wat het doet |
| --- | --- | --- |
| `--plain` | vlag | print bare target names only, one per line, for scripting |

### `input_bot.py mutate`

| Optie | Standaard | Wat het doet |
| --- | --- | --- |
| `--seed` | verplicht | seed input script |
| `--frames` | `8000` | frames to run each candidate |
| `--iterations` | `20` | number of candidates per generation |
| `--generations` | `1` | rounds of search; each round re-seeds with the previous round's best script, so the search climbs instead of resampling the same seed (default 1 = a single flat round) |
| `--keep` | `5` | number of top scripts to save |
| `--output-dir` | `/tmp/input-bot` | where to save the top scripts (default: a scratch directory; promoting a script into context/input-scripts/generated is a deliberate step, taken only after evaluate has confirmed it) |
| `--force` | vlag | allow replacing existing files in --output-dir |
| `--emulator` | `./build/c-phoenix` | emulator binary |
| `--cwd` | `.` | working directory for emulator |
| `--sdl-video-driver` | `dummy` | SDL_VIDEODRIVER for emulator |
| `--random-seed` | `1` | deterministic RNG seed |
| `--mutate-after` | `220` | preserve seed events before this frame |
| `--mutation-mode` | `regenerate` | how to mutate events after --mutate-after |
| `--verbose` | vlag | print emulator output on failures |
| `--target` | `[]` | target to reward; can be repeated |

---

Terug naar [tools/README.nl.md](README.nl.md).
