# C-Phoenix runtime trace explorer

Open [index.html](index.html) directly in a browser. It is a self-contained
interactive view of the most recently recorded C-Phoenix runtime call trace.
It does not run the game; it groups and explores calls that were recorded by
the instrumentation during a prior gameplay scenario.

Regenerate it with:

```sh
make -C c-phoenix runtimegraph RUNTIME_SCENARIO=bird-investigation RUNTIME_FRAMES=13935
```

The scenario-specific SVG, PNG, CSV and comparison evidence remains under
`c-phoenix/context/runtimegraphs/<scenario>/`. This directory is the stable,
discoverable entry point for the interactive explorer.
