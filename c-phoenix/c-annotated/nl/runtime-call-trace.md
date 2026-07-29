# Runtime Call Tracer (`runtime_call_trace.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`runtime_call_trace.c`](../../runtime_call_trace.c). Deze module bevat de compiler-level profileringshooks (`__cyg_profile_func_enter`) voor het automatisch genereren van binaire call-graphs en dynamic trace logs van de C-code execution.

---

## 1. Dynamic Profiling & Callgraph Tracer

### `runtime_call_trace_start`, `runtime_call_trace_stop` & `__cyg_profile_func_enter`
#### **Beschrijving**
- `runtime_call_trace_start(const char *path)`: Initialiseert de hash-tabel voor call-edges en opent het binaire trace-bestand (`.cg`).
- `runtime_call_trace_stop()`: Schrijft de callgraph-header (`CPHXCG01`) en alle verzamelde caller/callee paren met hun aanroepaantallen naar het trace-bestand.
- `__cyg_profile_func_enter(void *callee, void *caller)`: Wordt door de GCC/Clang compiler-vlag `-finstrument-functions` automatisch aangeroepen bij ELKE functie-invoer om het precieze verloop van de executie-graaf vast te leggen.

#### **Knowledge Graph Koppelingen**
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - Compiler instrumentation entrypoints bij het draaien van profiling-runs.
