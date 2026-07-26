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

Gebruik vanuit de repository-root de standaard lokale viewer-target:

```bash
make -C c-phoenix tracer-view-only \
  TRACE_VIEW_OUTPUT=context/traces/two_player_last_grown_bird_compare/last-grown-bird-diff.html
```

Open de door Make gemelde localhost-URL (standaardpoort `8766`). Stop de
server met `Ctrl-C` in dezelfde terminal.

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
