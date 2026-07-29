# Z80 Core Emulation Macros (`z80_core.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de Z80 CPU hulpmacro's in [`z80_core.h`](../../z80_core.h). Dit bestand definieert de lage-niveau hulporoutines voor bitrotaties, BCD-optellingen en 8-bits registerbewerkingen.

---

## Inhoudsopgave
1. [Z80 Bitrotatie & Vlaggen Macros](#1-z80-bitrotatie--vlaggen-macros)
2. [Hulpfuncties](#2-hulpfuncties)

---

## 1. Z80 Bitrotatie & Vlaggen Macros

### Rotatie-instructies
- `RLCA`: Rotate Left Circular Accumulator (`(a << 1) | (a >> 7)`).
- `RRCA`: Rotate Right Circular Accumulator (`(a >> 1) | (a << 7)`).
- `DAA`: Decimal Adjust Accumulator (BCD-optellingscorrectie na optellingen of aftrekkingen).

---

## 2. Hulpfuncties

### `add_one_to_mem` & `compare_bc_to_mem`
- `add_one_to_mem(uint16_t addr)`: Verhoogt de 16-bits waarde op RAM-locatie `addr:addr+1` atomic met 1.
- `compare_bc_to_mem(uint16_t addr, uint16_t val)`: Vergelijkt een 16-bits waarde met een RAM-locatie.
