# Large File Review

This repository deliberately keeps generated bulk data out of Git. The audit
command reports every file of at least 1 MiB and rejects unapproved files of
20 MiB or more.

```sh
make large-files
```

## Current Curated Files

| Path | Approximate size | Decision |
| --- | ---: | --- |
| `c-phoenix/context/traces/two_player_last_grown_bird_compare/*.bin.gz` | 0.5 MiB each | Keep. Compressed deterministic RAM fixtures; see the case README for extraction. |
| `c-phoenix/context/traces/two_player_last_grown_bird_compare/last-grown-bird-diff.html.zip` | 1.1 MiB | Keep. Standalone visual-tracer fixture. |
| `demo/*.mp4` | 1.0-1.3 MiB | Keep. Short curated showcase recordings. |
| `demo/runtimegraphs/bird-investigation/jphoenix_semantic_runtime_callgraph.png` | 1.6 MiB | Keep. Curated JPhoenix runtime graph. |
| `demo/runtimegraphs/bird-investigation/c_phoenix_runtime_callgraph.png` | 8.1 MiB | Keep pending visual-format review. Required for the current showcase. |
| `demo/runtimegraphs/bird-investigation/c_phoenix_design_runtime_comparison.png` | 10 MiB | Keep pending visual-format review. Required for the current showcase. |

Do not add raw RAM dumps, frame screenshots, browser HTML traces, or build
output. Recreate them locally, publish them as release assets, or use Git LFS
only when a reviewed workflow requires the full binary.
