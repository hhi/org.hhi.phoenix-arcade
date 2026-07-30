# Test Coverage Declarations (`coverage.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat de geannoteerde header-declaraties voor [`coverage.h`](../../coverage.h).

---

## Declaraties & Koppelingen
- `coverage_set_output_path(const char* path)`: Stelt het pad in voor de JSON-dekking dump.
- `coverage_is_enabled(void)`: Controleert of dekking actief is.
- `coverage_hit(const char* name)`: Registreert het bereiken van een logisch label.
- `coverage_observe_frame(int frame, const PhoenixState* s)`: Meting per frame.

#### **Knowledge Graph Koppelingen**
* **Overeenkomstige C-implementatie:** [`coverage.c`](../../coverage.c) → [`coverage.md`](coverage.md)
