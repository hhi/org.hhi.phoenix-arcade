# TMS36XX Synthesizer Declarations (`tms36xx.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat de geannoteerde header-declaraties voor [`tms36xx.h`](../../tms36xx.h).

---

## Structuur & Declaraties
- `TMS36XX`: Bevat de 12-stemmingen toestand, uitdovingstellers (`decay`), frequenties en melodietellers.
- `tms36xx_init(TMS36XX* tms)`: Chip initialisatie.
- `tms36xx_mm6221aa_tune_w(TMS36XX* tms, int tune)`: Selectie van de achtergrondmelodie (Tune 1, 2 of 3).
- `tms36xx_render_internal_sample(TMS36XX* tms)`: Rendert 1 interne sample op 23.8kHz.

#### **Knowledge Graph Koppelingen**
* **Overeenkomstige C-implementatie:** [`tms36xx.c`](../../tms36xx.c) → [`tms36xx.md`](tms36xx.md)
