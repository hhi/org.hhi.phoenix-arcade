# Vergelijking Laatste Volgroeide Vogel

Deze map bewaart de gecureerde vergelijking tussen jphoenix en C-Phoenix voor
de replay waarin player 1 in een 2-player game tegen een laatste volgroeide
vogel speelt.

Engelse documentatie: [README.md](README.md).

Normaal horen bulk RAM-dumps in `/tmp` of de genegeerde root-map `/traces/`.
Deze case is bewust als uitzondering in `context/traces/` geplaatst, omdat de
bijbehorende replay een concrete regressie-/debugfixture is.

## Scenario

Inputscript:

```bash
context/input-scripts/two_player_last_grown_bird.txt
```

Verwachte target-window:

- record-index `7000..7283`
- jphoenix frameheaders `7521..7823`
- C-Phoenix frameheaders `7001..7284`
- `player1`
- echte gameplay (`GameOrAttract != 0`)
- `LevelAndRound = 0x05`
- `BirdsLeft = 1`
- exact een actieve vogel: slot `7`, `grown_bird`, state `0x0F`

De frameheader verschilt tussen beide dumps, maar de record-index en decoded
objectstate zijn gelijk in de target-window.

## Artefacten

| Bestand | Omschrijving | Grootte | SHA-256 |
| --- | --- | ---: | --- |
| `j-last-grown-bird.bin.gz` | Gecomprimeerde jphoenix RAM-dump, 8422 records | 511,684 bytes | `b2a6217f105fa76a4630d77ba6939620aad0e929e104b82844d2de0479667209` |
| `c-last-grown-bird.bin.gz` | Gecomprimeerde C-Phoenix RAM-dump, 8999 records | 509,737 bytes | `3a6070e80d71a6aec5c424ea446f83f88aff089cd332c4acccdb4fdd0db98100` |
| `last-grown-bird-diff.html.zip` | Gecomprimeerde standalone visuele object-diffviewer met auto-overlay | 1,190,094 bytes | `e728b7ae44afc306ee4724af5851b7eacec5d475c2523ff4079b9f78575cd503` |
| `c-last-grown-bird.coverage.json` | C-Phoenix coverage summary voor de run | 4,057 bytes | `d852b39a45ce9639feda1e0251c609248373c4a94f3951c8eb2b8e41a498c528` |
| `j-last-grown-bird.pc-coverage.csv` | jphoenix PC coverage uit `PhoenixCoverageRunner` | 103,023 bytes | `0de8bcd2385df604a06635e8d22e90451819fbef61f02d1301a70f65a873d1de` |

## Gecureerde Dumps Uitpakken

De ruwe dumps staan bewust niet in Git. Pak ze eerst uit naar `/tmp` voordat
je de vergelijkings- of tracercommando's gebruikt:

```bash
gzip -dc context/traces/two_player_last_grown_bird_compare/j-last-grown-bird.bin.gz > /tmp/j-last-grown-bird.bin
gzip -dc context/traces/two_player_last_grown_bird_compare/c-last-grown-bird.bin.gz > /tmp/c-last-grown-bird.bin
```

`gunzip -c` is gelijkwaardig. Gebruik op native Windows 7-Zip, of voer deze
commando's uit in WSL2. De SHA-256 van de uitgepakte bestanden is respectievelijk
`c26e1ed489ce37bb6d018f70323f71789d087e38534ece6b2d922070f66f3b54` en
`657e7f95234c393eac4c2d641aa920be993458105ac3658717efa3e599d5036c`.

## Dumps Opnieuw Maken

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./c-phoenix \
  --run-frames=9000 \
  --input-script=context/input-scripts/two_player_last_grown_bird.txt \
  --ram-dump=/tmp/c-last-grown-bird.bin \
  --coverage-dump=/tmp/c-last-grown-bird.coverage.json \
  --no-render
```

```bash
cd ../jphoenix-emulator-port
java \
  -Dphoenix.inputclock=poll \
  -Dphoenix.ramdump=/tmp/j-last-grown-bird.bin \
  -Dphoenix.ramdump.frames=9000 \
  -cp build/classes PhoenixCoverageRunner \
  ../c-phoenix/context/input-scripts/two_player_last_grown_bird.txt \
  /tmp/j-last-grown-bird-coverage \
  9000
cd ../c-phoenix
```

## RAM Vergelijken

```bash
python3 tools/compare_ram_dumps.py \
  /tmp/j-last-grown-bird.bin \
  /tmp/c-last-grown-bird.bin \
  --regions 438E-47FF,4B40-4BE5 \
  --stop-after 999999 \
  --max-diffs-per-frame 8
```

Resultaat:

- buiten scherm-RAM zijn er 6 afwijkende frame-paren;
- die afwijkingen zijn alleen `Counter9A/Counter9B`;
- target-records `7000`, `7001`, `7283` en `7284` hebben 0 verschillen in
  state/object-RAM;
- met foreground/background-scherm-RAM meegerekend zijn er 30 afwijkende
  frame-paren, vooral schermtekening/timing.

## Counter98-Uitlijning

`Counter98` is de 16-bit teller in RAM op `$4398:$4399`. De optie
`--align-c98` vergelijkt records waarin beide emulators dezelfde
`Counter98`-waarde hadden. Dat helpt bij frameheader-verschillen, maar minder
bij 2-player turn switches waar tellerwaarden terugkomen.

## Dump-/Timingruis

Dump-/timingruis zijn verschillen die ontstaan doordat de RAM-dump net voor of
net na een tussenstap wordt genomen, terwijl de objectstate later weer gelijk
is.

Mitigatie:

- vergelijk gameplay/object-RAM apart van scherm-RAM;
- sluit hi-score en Z80-stack uit bij functionele vergelijkingen;
- gebruik record-index plus decoded objectstate rond een target-window;
- gebruik write-level instrumentatie wanneer een exact schrijfadres/tijdstip
  onderzocht moet worden.

## Visuele Tracer

Pak eerst `last-grown-bird-diff.html.zip` uit. Zie
[VISUAL-TRACER.nl.md](VISUAL-TRACER.nl.md) voor de volledige startinstructie.

```bash
python3 tools/view_sprite_trace.py \
  /tmp/j-last-grown-bird.bin \
  --compare /tmp/c-last-grown-bird.bin \
  --reference-label jphoenix \
  --port-label c-phoenix \
  --player 1 \
  --output=context/traces/two_player_last_grown_bird_compare/last-grown-bird-diff.html
```

Het gegenereerde HTML-bestand is bewust niet versiebeheerd; archiveer het
opnieuw met `zip -9 last-grown-bird-diff.html.zip last-grown-bird-diff.html`.

De algemene bediening en interpretatie staan in
[de werkinstructie voor de visuele tracer](../visual-tracer-howto.nl.md).

Voor deze case bevestigt de objecttracer dat de laatste volgroeide vogel in de
target-window gelijk loopt tussen jphoenix en C-Phoenix.
