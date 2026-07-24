# Starting the Visual Tracer

This directory contains a standalone, compressed visual tracer:

```text
last-grown-bird-diff.html.zip
```

## Extract

Open a terminal in this directory and extract the archive:

```bash
unzip last-grown-bird-diff.html.zip
```

This creates `last-grown-bird-diff.html`. The file is generated locally and is
intentionally listed in `.gitignore`.

## Start

From the repository root, start a local web server:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 \
  --directory context/traces/two_player_last_grown_bird_compare
```

Then open:

```text
http://127.0.0.1:8765/last-grown-bird-diff.html
```

Stop the server with `Ctrl-C` in the same terminal.

## Regenerate

Regenerate the HTML from the repository root when the tracer source or RAM
dumps change:

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

Then archive the updated viewer in the same directory:

```bash
cd context/traces/two_player_last_grown_bird_compare
zip -9 last-grown-bird-diff.html.zip last-grown-bird-diff.html
```
