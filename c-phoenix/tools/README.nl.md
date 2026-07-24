# Phoenix C-poort Tools

Deze map bevat hulpscripts om de Z80-naar-C-vertaling van Phoenix te
verifieren, mappen, vergelijken en documenteren.

Engelse documentatie: [README.md](README.md).

## Documentatiegeneratie

`generate_mappings.py` leest de `[ASM: XXXX-YYYY]` comments in `.c` en `.h`
bestanden en schrijft mappingdocumentatie naar `context/mapping/`.

```bash
python3 tools/generate_mappings.py
```

`generate_annotated_asm.py` maakt van `context/code-annotated.asm` een
klikbare Markdown-versie met C-koppelingen:

```bash
python3 tools/generate_annotated_asm.py
```

## Verificatie en Replay

### `input_bot.py`

Zie voor doel, mutatiemodi, meerdere targets en een volledige workflow:
[input-bot-howto.nl.md](input-bot-howto.nl.md).

Gebruik `evaluate` om een replay te scoren tegen coverage-doelen:

```bash
python3 tools/input_bot.py evaluate \
  --script context/input-scripts/basic_playthrough.txt \
  --frames 4000 \
  --target player_bullet_fired \
  --sdl-video-driver dummy \
  --no-render
```

Gebruik `mutate` om kandidaat-scripts te genereren:

```bash
python3 tools/input_bot.py mutate \
  --seed context/input-scripts/basic_playthrough.txt \
  --frames 8000 \
  --target level_transition
```

Voor doelgericht botgebruik staat de workflow in
[context/input-scripts/README.nl.md](../context/input-scripts/README.nl.md).

### `compare_ram_dumps.py`

Vergelijkt jphoenix- en C-Phoenix RAM-dumps byte-exact:

```bash
python3 tools/compare_ram_dumps.py /tmp/jphx.bin /tmp/port.bin \
  --align-c98 --stop-after 999999
```

### `lockstep/`

Bevat batchtooling om alle gecureerde inputscripts door jphoenix en c-phoenix
te draaien, clean runs te aggregeren en handmatige dumpparen voor
divergentieonderzoek te maken. Zie [lockstep/README.nl.md](lockstep/README.nl.md).

### `trace_sprites.py`

Extraheert objecttijdlijnen uit een RAM-dump:

```bash
python3 tools/trace_sprites.py /tmp/phoenix-ram.bin --kind all \
  --only-active --output=/tmp/objects.csv
```

### `view_sprite_trace.py`

De standaardmodus `auto` volgt per frame de gedeelde `$4B70-$4BAF`-overlay:
zestien alienslots in alienfases en acht vogelslots in vogelfases.

Maakt een interactieve HTML-viewer voor objecten of C-vs-jphoenix verschillen:

```bash
python3 tools/view_sprite_trace.py /tmp/jphoenix-ram.bin \
  --compare /tmp/c-phoenix-ram.bin \
  --reference-label jphoenix --port-label c-phoenix \
  --kind birds --player 1 --output=/tmp/bird-diff.html
```
