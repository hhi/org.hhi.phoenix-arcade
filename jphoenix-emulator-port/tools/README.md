# JPhoenix Tools

| Script | Input | Output | Kind |
| --- | --- | --- | --- |
| `generate_8080_boot_flow.py` | annotated 8080 assembly | boot-flow graph artifacts | Design-time analysis |
| `generate_8080_semantic_callgraph.py` | JPhoenix runtime call trace and labels | executed 8080 callgraph | Runtime analysis |
| `generate_8080_design_runtime_comparison.py` | design graph and runtime callgraph | observed versus designed call-edge comparison | Combined design/runtime analysis |
| `generate_runtime_callgraph.py` | generic runtime trace | rendered callgraph artifacts | Runtime analysis |
| `record_jphoenix_melody.sh` | emulator audio output | melody capture artifact | Runtime audio capture |

Use `make runtimegraph` for the supported scenario workflow; it writes its
results to `context/runtimegraphs/<scenario>/`. The design/runtime comparison
there is evidence for one replay, not a proof of unexecuted paths.
