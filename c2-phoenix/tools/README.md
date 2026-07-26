# C2-Phoenix Tools

These scripts turn native C2 RAM dumps into semantic evidence. Their normal
entry points are the matching `make` targets in the parent directory.

| Script | Input | Output | Kind |
| --- | --- | --- | --- |
| `generate_hires_sprite_assets.py` | assembled graphics and colour PROM ROMs | generated C2 sprite-atlas header in `build/native/.../generated/` | Build-time asset generation |
| `extract_semantic_frames.py` | C2 RAM dump | semantic frame JSON | Runtime analysis |
| `render_semantic_trace.py` | semantic frame JSON | standalone HTML trace | Runtime visualization |
| `compare_semantic_frames.py` | reference and port semantic JSON | named semantic differences | Runtime comparison |
| `summarize_semantic_scenario.py` | semantic frame JSON | scenario summary and assertions | Runtime evidence |

See [../SCENARIOS.md](../SCENARIOS.md) for the curated scenarios and
[../SEMANTIC-FRAME.md](../SEMANTIC-FRAME.md) for the JSON contract.
