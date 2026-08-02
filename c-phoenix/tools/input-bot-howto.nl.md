# Input Bot: doel en gebruik

`tools/input_bot.py` is een deterministische evaluator en mutator voor
replay-scripts. Hij speelt een script headless af met C-Phoenix, leest de
coverage-uitvoer en kan nieuwe kandidaat-scripts genereren. Het is geen live
spelende AI en verandert geen gameplaycode.

## Voorbereiding

Werk vanuit de repository-root en bouw eerst de emulator:

```bash
make
python3 tools/input_bot.py list-targets
```

Een input-script bevat regels in de vorm:

```text
<frame> <button> <press|release>
```

De bot genereert na de behouden seed vooral `left`, `right`, `fire` en
`shield`-events. Een seed moet daarom eerst betrouwbaar de gewenste spelfase
bereiken.

## Bestaand script beoordelen

Gebruik `evaluate` om te zien welke states, levels en doelen een script haalt:

```bash
python3 tools/input_bot.py evaluate \
  --script context/input-scripts/basic_playthrough.txt \
  --frames 4000 \
  --target player_bullet_fired \
  --sdl-video-driver dummy \
  --no-render
```

`evaluate` schrijft tijdelijk een coverage-JSON en rapporteert de relevante
samenvatting. Met `--coverage-out=/tmp/coverage.json` blijft die JSON bewaard.

## De mutatie- en evaluatiecyclus

De twee commando's hebben verschillende verantwoordelijkheden:

1. `evaluate` speelt **een bestaand script** eenmalig af en meldt per target
   `HIT` of `MISS`. Gebruik dit om een seed te beoordelen of een kandidaat te
   bewijzen.
2. `mutate` maakt uit die seed **N varianten** (`--iterations N`). Iedere
   variant wordt meteen headless afgespeeld en intern op exact dezelfde
   coverage beoordeeld als bij `evaluate`.
3. `mutate` berekent een score voor iedere variant en schrijft alleen de beste
   `--keep` varianten weg. Een bestandsnaam zoals
   `mutated_rank_01_score_3092917.txt` betekent dus: hoogste score in deze
   zoekopdracht, niet: alle targets zijn bewezen.
4. Kies een opgeslagen kandidaat en voer expliciet `evaluate` uit met **alle
   vereiste targets**. Alleen wanneer elk vereist target `HIT` meldt, is dit
   een geldige fixture.
5. Herhaal de zoekopdracht met een andere `--random-seed`, meer iteraties, een
   andere mutatiemodus of een later `--mutate-after` wanneer de verificatie
   nog een `MISS` toont.

Kort: `mutate` **zoekt en rangschikt**; `evaluate` **controleert en bewijst**.
De seed zelf wordt nooit overschreven. De gegenereerde kandidaatbestanden en
hun coverage staan in `--output-dir`.

### Volledig voorbeeld: een 2P-bonusleven zoeken

De seed bereikt al de 2P-route, maar nog niet aantoonbaar het bonusleven. We
behouden daarom de eerste 2500 frames en variëren alleen daarna:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/p2_bonus_life.txt \
  --frames 12000 --iterations 80 --keep 5 \
  --target two_player_game_started \
  --target player_2_bank_initialized \
  --target two_player_turn_switch \
  --target bonus_life_awarded \
  --mutate-after 2500 --mutation-mode jitter --random-seed 1 \
  --output-dir /tmp/input-bot-p2-bonus
```

Dit voert 80 onafhankelijke kandidaat-replays uit en bewaart bijvoorbeeld:

```text
/tmp/input-bot-p2-bonus/mutated_rank_01_score_123456.txt
/tmp/input-bot-p2-bonus/mutated_rank_01_score_123456.coverage.json
```

Controleer vervolgens de **hele** doelset, niet alleen het nieuwe doel:

```bash
python3 tools/input_bot.py evaluate \
  --script /tmp/input-bot-p2-bonus/mutated_rank_01_score_123456.txt \
  --frames 12000 \
  --target two_player_game_started \
  --target player_2_bank_initialized \
  --target two_player_turn_switch \
  --target bonus_life_awarded \
  --sdl-video-driver dummy --no-render
```

Vervang `123456` door de daadwerkelijk geschreven score. Meldt de uitvoer
viermaal `HIT`, dan kan deze kandidaat na een herhaalbare tweede `evaluate`
naar `context/input-scripts/` worden gepromoveerd. Bij een `MISS` is de
kandidaat geen fixture: pas de zoekparameters aan en begin opnieuw bij
`mutate`.

## Nieuwe kandidaten zoeken

Gebruik `mutate` om kandidaat-scripts te maken en te rangschikken:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/basic_playthrough.txt \
  --frames 8000 \
  --iterations 20 \
  --target level_transition \
  --random-seed 1
```

De beste scripts en hun coverage gaan naar `/tmp/input-bot/` tenzij je iets
anders opgeeft, en elke run meldt waar hij ze heeft weggeschreven.

Ze belanden bewust **niet** in `context/input-scripts/generated/`. Die map is de
gecommitte verzameling — de 50 scripts waar het dekkingsbewijs op rust — en een
ruw zoekresultaat is nog geen fixture: het is alleen *gescoord*, niet bevestigd.
Promoveren doe je door er eerst `evaluate` op te draaien en het daarna te
kopiëren, of door `--output-dir` expliciet mee te geven.

Waar hij ook schrijft, een run weigert een bestaand bestand met afwijkende
inhoud te vervangen en noemt de bestanden, in plaats van er stilletjes overheen
te gaan. `--force` zet dat opzij. Dezelfde `--random-seed` geeft dezelfde
mutaties, zolang de emulator en seed gelijk zijn.

## Generaties: de zoektocht laten klimmen

Het commando hierboven is **één vlakke ronde**. Alle twintig kandidaten zijn
mutaties van dezelfde seed, ze worden gescoord, de beste worden bewaard — en de
winnaar wordt nooit hergebruikt. Voor een ondiep target als `level_transition`
is dat genoeg. Voor een diep target als `gameplay_level_9` of
`mothership_core_gate_70` niet: de run moet dan minuten spel overleven, en geen
enkele losse mutatie van een korte seed komt daar.

`--generations` dicht dat gat. Het beste script van ronde *N* wordt de seed van
ronde *N+1*, zodat elke ronde vertrekt vanaf de beste positie tot dan toe in
plaats van steeds dezelfde omgeving af te tasten:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/basic_playthrough.txt \
  --frames 8000 \
  --iterations 20 \
  --generations 5 \
  --target gameplay_level_9 \
  --random-seed 1 \
  --output-dir /tmp/input-bot-level9
```

Dit draait 5 x 20 = 100 replays en drukt per ronde een kop af:

```
-- generation 1/5 · seed score original
g01_0001: score=148300 max_game=0x05 ...
...
   best of this round: 148300  ->  seeds generation 2
-- generation 2/5 · seed score 148300
...
   re-seeded: 148300 -> 152900 (+4600)  ->  seeds generation 3
-- generation 3/5 · seed score 152900
...
   no improvement (151740 <= 152900); keeping the current seed
...
seed score per generation: 148300 -> 152900 -> 152900 -> 161100 -> 161100   (2 re-seeds after the first round)
```

Elke ronde eindigt met één regel die zegt of de seed verschoven is, en de run
sluit af met het hele verloop. Je hoeft dus nooit twee kopregels pagina's uit
elkaar te vergelijken om te zien of de zoektocht klimt of vastzit.

**Eén voorbehoud, en daar valt of staat het mee.** `--generations` bouwt alleen
voort als de mutator behoudt wat de vorige winnaar goed maakte, en twee van de
drie modi doen dat niet. `regenerate` (de standaard) en `sweep` gooien elk
seed-event vanaf `--mutate-after` weg en bouwen daar een vers patroon, dus een
her-seede winnaar draagt alleen zijn opening bij. Gemeten op een seed met vijf
markeer-events voorbij frame 220: **jitter neemt er vier mee, regenerate en
sweep geen enkele.**

Wil je dus iets aan generaties hebben, gebruik dan

```bash
  --mutation-mode jitter          # houdt de hele winnaar, schuift alleen de timing
```

of zet `--mutate-after` voorbij het deel dat je wilt meenemen. Een run die om
generaties vraagt met een weggooiende modus drukt precies deze waarschuwing af.
Wat elke modus doet, ligt vast in
[`tests/test_input_bot_generations.py`](../tests/test_input_bot_generations.py).

De seed verschuift alleen bij een **strikte verbetering**. Een ronde die niets
beters vindt meldt `no improvement (…); keeping the current seed`, en de
volgende ronde probeert het opnieuw vanaf dezelfde plek — een ongelukkige ronde
kan de zoektocht dus niet terugduwen. `--keep` rangschikt nog steeds over alle
generaties heen, niet per ronde.

`--generations 1` is de standaard en gedraagt zich precies zoals voorheen.

De zoeklogica wordt gedekt door
[`tests/test_input_bot_generations.py`](../tests/test_input_bot_generations.py),
die `mutate` aanstuurt met een nep-emulator — die test draait dus zonder SDL2 en
zonder gebouwde binary.

## Een uitgewerkte run, en de valkuil erin

Een echte zoektocht, zes generaties van acht kandidaten tegen `level_transition`:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/extended_playthrough.txt \
  --frames 6000 --iterations 8 --generations 6 \
  --mutation-mode jitter \
  --target level_transition --random-seed 1
```

```
-- generation 1/6 · seed score original
g01_0007: score=1256823 max_level=0x0B max_game=0x01 deaths=5 kills=11 mship_tiles=10 ... level_transition=hit
   best of this round: 1256823  ->  seeds generation 2
-- generation 2/6 · seed score 1256823
   re-seeded: 1256823 -> 1256919 (+96)  ->  seeds generation 3
-- generation 3/6 · seed score 1256919
   re-seeded: 1256919 -> 1265641 (+8722)  ->  seeds generation 4
-- generation 4/6 · seed score 1265641
   no improvement (1264995 <= 1265641); keeping the current seed
...
seed score per generation: 1256823 -> 1256919 -> 1265641 -> 1265641 -> 1265641 -> 1265641   (2 re-seeds after the first round)
```

De zoektocht doet precies wat de bedoeling is: twee verbeteringen, daarna een
plateau waar hij niet vanaf glijdt. Maar de getallen zeggen ook iets anders, en
dat is goed om te weten voordat je zo'n run vertrouwt.

**Kijk naar `max_level=0x0B` naast `max_game=0x01`.** De eerste telt elk level
dat *gezien* is, inclusief de attract-demo; de tweede alleen levels die in echt
spel zijn gehaald. Ronde 11 werd gehaald doordat de demo zichzelf speelde. De
speler kwam nooit voorbij ronde 1.

Dat telt zwaar, door de manier waarop de score is opgebouwd. `level_transition`
eindigt niet op `_gameplay`, dus `wants_gameplay_progress()` is onwaar en de
score gebruikt `max_level * 100000` — attract-voortgang en al — terwijl de
attract-frame-aftrek door vier wordt gedeeld in plaats van volledig te tellen.
De rekensom:

| | |
| --- | --- |
| `max_level` 0x0B x 100000 | 1.100.000 |
| `max_gameplay_level` 0x01 x 25000 | 25.000 |
| `level_transition` gehaald | 50.000 |
| 5 deaths x -500 | -2.500 |
| **vaste bodem** | **1.172.500** |

**87% van die score is de attract-demo.** Het deel waar de zoektocht werkelijk
aan kan draaien ging van 84.323 naar 93.141 — een echte winst van 10,5%, maar op
een tiende van het getal dat je in de log ziet. En wat hij vooral optimaliseerde
was `mship_tiles`, die bij `mship_game=0` óók allemaal tijdens de demo scoorden.

**De oplossing is een gameplay-target noemen.** Elk target dat op `_gameplay`
eindigt kantelt de scoring: `max_gameplay_level * 150000`, geen attract-bonus, en
de volledige attract-frame-aftrek.

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/extended_playthrough.txt \
  --frames 6000 --iterations 8 --generations 6 \
  --mutation-mode jitter \
  --target bird_wave_gameplay --random-seed 1
```

Twee gewoontes volgen hieruit. Vergelijk `max_level` met `max_game` in de log
voordat je een score gelooft, en kies een `_gameplay`-target zodra je wilt dat de
speler het werk doet en niet de demo.

## Meerdere targets

Herhaal `--target` voor een gecombineerd doel. Elk geraakt doel krijgt een
bonus in de rangschikking. Dit is zinvol wanneer alle voorwaarden nodig zijn
voor een bruikbare trace:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/generated/mutated_rank_01_score_3092917.txt \
  --frames 26000 \
  --iterations 80 \
  --target mothership_active_gameplay \
  --target mothership_tile_60_hit \
  --target mothership_core_window \
  --target mothership_core_gate_70 \
  --target mothership_explosion \
  --mutate-after 10000 \
  --mutation-mode sweep \
  --random-seed 1 \
  --output-dir /tmp/input-bot-mothership
```

Kies alleen doelen die inhoudelijk samen kunnen voorkomen. Een brede set kan
de zoekruimte vergroten en een script dat een belangrijk hoofddoel raakt
lager rangschikken dan een script met veel eenvoudige bijdoelen.

Targets zijn **scorebonussen**, geen harde filter. `mutate` kan dus een
hoogst scorend script bewaren dat niet ieder opgegeven target haalt. Beoordeel
elke kandidaat daarna altijd opnieuw met `evaluate`.

## Targetcatalogus

| Groep | Targets | Betekenis en gebruik |
| --- | --- | --- |
| Start en twee spelers | `coin_accepted`, `two_player_game_started`, `player_2_bank_initialized`, `two_player_turn_switch` | Valideer munt/start, initialisatie van beide RAM-banken en echte spelerwissel. Combineer de laatste drie voor een 2P-fixture. |
| Speler en projectielen | `player_bullet_fired`, `shield_used`, `player_death`, `game_over`, `enemy_bullets_active` | Korte smoke-, collision- en aflooproutes. |
| Voortgang | `level_transition`, `gameplay_level_5`, `gameplay_level_7`, `gameplay_level_8`, `gameplay_level_9` | Zoek een route die aantoonbaar een bepaalde spelronde in echte gameplay bereikt. |
| Aliens en vogels | `alien_kill`, `bird_hit`, `bird_wave_entry`, `bird_wave_gameplay`, `grown_bird_bonus_explosion` | `bird_hit` is breed; gebruik `grown_bird_bonus_explosion` voor de specifieke volgroeide-vogelroute. |
| Moederschip | `mothership_active`, `mothership_active_gameplay`, `mothership_tile_hit`, `mothership_tile_4c_hit`, `mothership_tile_60_hit`, `mothership_core_window`, `mothership_core_gate_70`, `mothership_explosion` | Bouw een gefaseerde moederschipcase op: actief in gameplay, tile-hit, kernvenster, gate `$70`, explosie. |
| Score | `bonus_life_awarded` | Controleert dat de score daadwerkelijk de bonuslevendrempel passeert. Combineer met 2P-targets voor de nog te maken 2P-bonuslevenfixture. |

De tabel hierboven groepeert de targets; **elk target wordt afzonderlijk
besproken**, met de exacte voorwaarde die het toetst en wanneer je het boven een
buurman kiest, in [input-bot-reference.nl.md](input-bot-reference.nl.md). Die
pagina somt ook elke opdrachtregeloptie met zijn standaardwaarde op. Beide zijn
gegenereerd uit `input_bot.py` en kunnen dus niet achterlopen op de code.

De actuele lijst is altijd op te vragen bij het gereedschap zelf:

```bash
python3 tools/input_bot.py list-targets          # namen plus de voorwaarde die elk toetst
python3 tools/input_bot.py list-targets --plain  # kale namen, voor scripts
```

## Aanbevolen cases

| Case | Seed | Targets | Doel |
| --- | --- | --- | --- |
| Korte smoke | `basic_playthrough.txt` | `level_transition` | Snelle controle dat de invoerroute en rondereset werken. |
| Brede 1P-regressie | `bird-investigation.txt` | alle relevante gameplay-, vogel- en moederschiptargets | Referentiesessie; uitgebreid maar niet compact. |
| 2P-bank en beurt | `p2_bonus_life.txt` | `two_player_game_started`, `player_2_bank_initialized`, `two_player_turn_switch`, `grown_bird_bonus_explosion` | Huidige 2P-regressieroute. |
| 2P-bonusleven | `p2_bonus_life.txt` | vorige set plus `bonus_life_awarded` | Nieuwe, gezochte fixture; nog niet bewezen door de huidige seed. |
| Compact moederschip | een late gameplayseed | `mothership_active_gameplay`, `mothership_tile_60_hit`, `mothership_core_window`, `mothership_core_gate_70`, `mothership_explosion` | Kortere vervanger voor de moederschipfase in de brede sessie. |

## Volledige voorbeelden

Controleer de bestaande 2P-route:

```bash
python3 tools/input_bot.py evaluate \
  --script context/input-scripts/p2_bonus_life.txt \
  --frames 9000 \
  --target two_player_game_started \
  --target player_2_bank_initialized \
  --target two_player_turn_switch \
  --target grown_bird_bonus_explosion \
  --sdl-video-driver dummy --no-render
```

Zoek naar de 2P-bonuslevencase, zonder de bewezen beginroute te muteren:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/p2_bonus_life.txt \
  --frames 12000 --iterations 80 --keep 5 \
  --target two_player_game_started \
  --target player_2_bank_initialized \
  --target two_player_turn_switch \
  --target bonus_life_awarded \
  --mutate-after 2500 --mutation-mode jitter --random-seed 1 \
  --output-dir /tmp/input-bot-p2-bonus

python3 tools/input_bot.py evaluate \
  --script /tmp/input-bot-p2-bonus/mutated_rank_01_score_<score>.txt \
  --frames 12000 --target bonus_life_awarded \
  --sdl-video-driver dummy --no-render
```

Gebruik voor een moederschipzoektocht `sweep` en bewaar eerst een seed die de
moederschipfase aantoonbaar bereikt. Promoveer een kandidaat pas na een clean
replay en, waar relevant, lockstepvergelijking.

## Mutatiemodi

- `regenerate` (standaard): behoudt de seed tot `--mutate-after` en genereert
  daarna een nieuw patroon.
- `jitter`: varieert vooral de timing van bestaande events; bruikbaar wanneer
  de seed al de juiste fase bereikt.
- `sweep`: behoudt de route en beweegt daarna herhaald links/rechts terwijl er
  wordt geschoten; bruikbaar voor moederschip- of gebiedsdoelen.

Gebruik `--mutate-after` om een bekende goede beginroute te behouden. De
standaard is frame `220`.

## Resultaat bekijken en bewaren

Speel een kandidaat zichtbaar af zonder `--run-frames`:

```bash
make replayrun \
  REPLAY_SCRIPT=context/input-scripts/generated/mutated_rank_01_score_....txt
```

Promoveer alleen een winnaar naar `context/input-scripts/` als deze een
herhaalbaar scenario of regressie vastlegt. Voeg dan een headercomment toe met
het doel, de seed en de relevante targets.
