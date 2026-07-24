# Visuele Tracer Starten

Deze map bevat een zelfstandige, gecomprimeerde visual tracer:

```text
last-grown-bird-diff.html.zip
```

## Uitpakken

Open een terminal in deze map en pak het archief uit:

```bash
unzip last-grown-bird-diff.html.zip
```

Dit maakt `last-grown-bird-diff.html`. Dit bestand is lokaal gegenereerd en
staat bewust in `.gitignore`.

## Starten

Start vanuit de repository-root een lokale webserver:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 \
  --directory context/traces/two_player_last_grown_bird_compare
```

Open vervolgens:

```text
http://127.0.0.1:8765/last-grown-bird-diff.html
```

Stop de server met `Ctrl-C` in dezelfde terminal.

## Opnieuw Genereren

Genereer de HTML opnieuw vanuit de repository-root wanneer de tracerbron of
de RAM-dumps veranderen:

```bash
gzip -dc context/traces/two_player_last_grown_bird_compare/j-last-grown-bird.bin.gz > /tmp/j-last-grown-bird.bin
gzip -dc context/traces/two_player_last_grown_bird_compare/c-last-grown-bird.bin.gz > /tmp/c-last-grown-bird.bin
python3 tools/view_sprite_trace.py \
  /tmp/j-last-grown-bird.bin \
  --compare /tmp/c-last-grown-bird.bin \
  --reference-label jphoenix \
  --port-label c-phoenix \
  --player 1 \
  --output=context/traces/two_player_last_grown_bird_compare/last-grown-bird-diff.html
```

Archiveer daarna de vernieuwde viewer in dezelfde map:

```bash
cd context/traces/two_player_last_grown_bird_compare
zip -9 last-grown-bird-diff.html.zip last-grown-bird-diff.html
```
