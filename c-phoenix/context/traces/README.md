# Curated reference traces

This directory is for small, curated traces that document a specific porting
finding and are useful to keep with the source tree.

Dutch documentation: [README.nl.md](README.nl.md).

Keep:

- short instruction-level or object-level traces with a written conclusion;
- traces that explain a translated routine, RAM field, or historical bug fix;
- enough command/source context to reproduce the observation.

Do not keep:

- bulk RAM dumps, frame dumps, screenshots, or generated HTML viewers;
- exploratory logs without a summarized finding;
- machine-local paths or ROM assets.

Use `/tmp` or the ignored root-level `traces/` directory for disposable trace
output.

## Curated Cases

- `two_player_last_grown_bird_compare/` - jphoenix-vs-C-Phoenix RAM/object
  comparison for the 2-player replay where player 1 faces one remaining grown
  bird.

Use the [semantic case template](semantic-case-template.md) for a new case
that substantiates the meaning of a RAM field, bit, or routine.

The end-to-end replay, comparison, and tracer workflow is documented in
[replay-tracer-pipeline-howto.md](replay-tracer-pipeline-howto.md). See
[visual-tracer-howto.md](visual-tracer-howto.md) for the interactive object
viewer and [semantic-lockstep-howto.md](semantic-lockstep-howto.md) for
evidence-based RAM-field analysis.
