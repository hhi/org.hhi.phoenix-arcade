bird-investigation
==================

Dit is de opgenomen interactieve sessie in bird-investigation.txt.
Het script eindigt op frame 13535. De extra 400 frames laten effecten die al
in gang zijn gezet nog doorlopen; daarom wordt de vergelijking tot frame 13935
uitgevoerd.

Genereer de RAM-dumps en de visuele tracer vanuit de repository-root:

make tracerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999

Uitvoer (niet gecommit):

- /tmp/ref_bird-investigation.bin     jphoenix RAM-dump
- /tmp/port_bird-investigation.bin    c-phoenix RAM-dump
- /tmp/bird-investigation-diff.html   zelfstandige visuele tracer

Open de tracer lokaal:

make tracer-view-only TRACE_VIEW_OUTPUT=/tmp/bird-investigation-diff.html

Open daarna de door Make gemelde localhost-URL. Stop de server met Ctrl-C.

De .bin-dumps en de HTML zijn afgeleide, grote bestanden en horen niet in Git.
