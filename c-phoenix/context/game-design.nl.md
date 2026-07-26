# Phoenix: spelontwerp en architectuur

Dit document beschrijft Phoenix zoals de huidige C-port het gedrag van de originele Z80-ROM uitvoert. Het is een wegwijzer, niet de normatieve specificatie voor een vertaalwijziging: bij conflict hebben [code-annotated.asm](code-annotated.asm), de [Computer Archeology Phoenix-referentie](ComputerArcheology.md) en de `[ASM: ...]`-ankers in de C-code voorrang.

## Doel en opbouw

Phoenix is een vaste-scherm-schietspel voor een of twee spelers. De speler beweegt een schip horizontaal, vuurt omhoog en gebruikt een tijdelijk schild. De spelrondes wisselen golven met aliens en vogels af met een gevecht tegen het moederschip. De attractmodus toont de presentatie en een demo totdat er een munt en een startkeuze zijn.

De C-port is geen nieuw ontworpen game-engine. Hij bewaart bewust de besturing, RAM-indeling en framegewijze routines van de ROM. Daardoor zijn spelregels, animaties, geluid en rendering verspreid over kleine routines die elk een ROM-adres vertegenwoordigen.

## Architectuur in een oogopslag

```text
SDL-platform (venster, invoer, audio-uitvoer, deterministische CLI)
                              |
                              v
phoenix_main_loop() -- per vblank/frame --> attractmodus of spelmodus
                              |                         |
                              |                         v
                              |                  game_state_machine()
                              |                    |-- initialisatie
                              |                    |-- spelronde
                              |                    |-- explosie/einde
                              v
hardwarelaag: video-RAM, scroll, palette, geluid, invoerpoorten
                              ^
                              |
PhoenixState: byte-exacte game-RAM ($4000-$4BFF)
```

De hoofdlus staat in [`hw_video_audio.c`](../hw_video_audio.c). Die wacht op de verticale blanking interval, verwerkt machine-invoer en kiest vervolgens de attracttak (`splash_and_demo()` in [`attract_mode.c`](../attract_mode.c)) of de speeltak (`game_state_machine()` in [`game_state_machine.c`](../game_state_machine.c)).

`PhoenixState` in [`phoenix_state.h`](../phoenix_state.h) is een byte-exacte afbeelding van de game-RAM. Code benadert ROM, RAM en arcade-I/O via `mem_read`/`mem_write` uit [`z80_core.h`](../z80_core.h). De SDL-specifieke zaken, waaronder venster, toetsenbordinvoer, player-bankwissels en headless replay-opties, zitten in [`platform_sdl.c`](../platform_sdl.c).

## Spelcyclus

```text
attractmodus -> munt/start -> nieuwe game -> initialisatie -> spelronde
       ^                                                    |
       |                                                    +--> speler vernietigd
       |                                                    |       |
       |                                                    |       +--> volgende speler of GAME OVER
       |                                                    |
       +---------------- GAME OVER <-----------------------+
                                                            |
spelronde: aliens/vogels -- ronde klaar --> volgende ronde -+
                         |
                         +-- moederschip vernietigd --> scoreweergave --> volgende ronde
```

De spelmodus gebruikt `GameState` (`$43A4`) als dispatchwaarde. De betekenis is direct zichtbaar in `game_state_machine()`:

| Waarde | Fase | Hoofdimplementatie |
| --- | --- | --- |
| 0 | nieuwe game / spelerwissel voorbereiden | `game_state_machine.c` |
| 1 | score van actieve speler laten knipperen, daarna ronde verhogen | `game_state_machine.c` |
| 2 | game- en rondergegevens initialiseren | `state_init.c` |
| 3 | normale spelactie | `state_play.c` |
| 4 | explosie van het spelersschip | `state_endings.c` |
| 5 | GAME OVER en terugkeer naar attractmodus waar nodig | `state_endings.c` |
| 6 | explosie van het moederschip | `state_endings.c` |
| 7 | score van moederschip tonen en door naar de volgende ronde | `state_endings.c` |

`LevelAndRound` (`$43B8`) bevat twee begrippen: de lage nibble kiest het rondepatroon en de hoge nibble telt de grotere rondecyclus. In state 3 dispatcht de lage nibble als volgt:

| Lage nibble | Spelinhoud |
| --- | --- |
| `0`, `2` | alien-golf die infadet |
| `1`, `3`, `B` | actieve alienronde |
| `4`, `6`, `8` | spiraalvormige vogelopbouw |
| `5`, `7` | vogelronde die infadet |
| `9` | moederschip fade-in |
| `A` | moederschip en aliens fade-in |

Dit is de ROM-dispatch, geen algemene leveldesigner. De precieze configuratie per ronde komt uit de tabellen en routines in onder meer [`init_global_level_data.c`](../init_global_level_data.c), [`alien_wave.c`](../alien_wave.c), [`bird_wave_behavior.c`](../bird_wave_behavior.c) en [`mothership_impl.c`](../mothership_impl.c).

## Kernmechanieken

### Speler

De speler kan binnen een vaste horizontale band bewegen. Een vuurschot wordt op een invoerflank gestart; ingedrukt houden is dus niet hetzelfde als iedere frame opnieuw schieten. Het schild is tijdelijk en wordt eveneens via de invoerlogica geactiveerd. `player_update()` verzorgt per frame de invoer, positie, kogels, schild en sprite-adressering in [`player_logic.c`](../player_logic.c).

De voornaamste bijbehorende RAM-velden zijn `PlayerShipX`, `PlayerState`, `ShieldCount`, `PlayerBulletState` en `AbovePlayerBulletState`; hun exacte adressen en bitbetekenissen staan in de [Computer Archeology Phoenix-referentie](ComputerArcheology.md).

### Vijanden en botsingen

Alien-, vogel- en moederschipgedrag zijn afzonderlijk vertaald om de originele routinegrenzen te behouden. De relevante modules zijn `alien_logic.c`/`alien_wave.c`, `bird_logic.c`/`birds_vertical_movement.c`/`bird_wave_behavior.c` en `mothership_logic.c`/`mothership_impl.c`. Algemene overlaptests en de afhandeling van projectielen staan in [`collision_detection.c`](../collision_detection.c) en [`weapon_collision.c`](../weapon_collision.c).

`AliensLeft` (`$43BA`) en `BirdsLeft` (`$43BB`) houden resterende vijanden bij voor de overgangslogica. Bij een vernietigd moederschip volgt eerst state 6 voor de animatie en daarna state 7 voor de scoreweergave; pas daarna wordt de volgende ronde geïnitialiseerd.

### Score, levens en twee spelers

Scores bestaan uit drie packed-BCD-bytes: score 1 op `$4381-$4383`, score 2 op `$4385-$4387` en de high score op `$4389-$438B`. De scoreverwerking en bonusleven-drempel staan in [`scoring.c`](../scoring.c). Het startaantal levens komt uit de DIP-switchinstelling en wordt in [`state_init.c`](../state_init.c) ingelezen.

De actieve speler wordt mede bepaald door `GameAndDemoOrSplash` (`$43A3`). Voor twee spelers wisselt de port de volledige player-bank, zodat spelerspecifieke RAM in dezelfde ROM-layout gebruikt kan blijven worden. De afhandeling van een vernietigd schip, resterende levens en GAME OVER staat in [`state_endings.c`](../state_endings.c).

## Presentatie en techniek

Sprites en tilegegevens worden uit de gameplay-state naar de arcade-achtige videoregisters geschreven door [`sprite_rendering.c`](../sprite_rendering.c) en de video-routines in [`hw_video_audio.c`](../hw_video_audio.c). Geluidsevents komen vanuit de spelroutines in de sound-latches terecht; [`sound.c`](../sound.c), [`sound_discrete.c`](../sound_discrete.c) en [`tms36xx.c`](../tms36xx.c) verzorgen emulatie en uitvoer.

De attractmodus is onderdeel van het spelontwerp, niet alleen een menu. Hij tekent de intro en scoretabel, verwerkt munten en startknoppen en laat een demo via dezelfde spelroutines lopen. Zie [`attract_mode.c`](../attract_mode.c).

## Waar verdere details staan

- [c_files_categorization.md](c_files_categorization.md): modules gegroepeerd per verantwoordelijkheid.
- [code-annotated.md](code-annotated.md): de geannoteerde ROM, met C-links.
- [ComputerArcheology.md](ComputerArcheology.md): externe hardware-, software-
  en RAM-referentie voor Phoenix.
- [mapping/c_functions_by_address.md](mapping/c_functions_by_address.md): adres-naar-C-functiemapping.
- [input-scripts/README.nl.md](input-scripts/README.nl.md): reproduceerbare spel- en regressiescenario's.

Bij documentatie van nieuw of nog onduidelijk gedrag geldt hetzelfde principe als voor de port: verwijs naar de ASM en noteer onzekerheid, in plaats van een spelregel te veronderstellen.
