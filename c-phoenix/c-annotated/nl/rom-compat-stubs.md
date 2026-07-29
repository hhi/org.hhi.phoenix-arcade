# ROM Compatibility Stubs (`rom_compat_stubs.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de functies in [`rom_compat_stubs.c`](../../rom_compat_stubs.c). Deze module bevat ROM-compatibiliteit stubs en de originele anti-piraterij beveiligingscontrole op de copyrighttekst.

---

## 1. ROM-compatibiliteit & Anti-piraterij

### `l1df0`
#### **Beschrijving**
De functie [`l1df0`](../../rom_compat_stubs.c#L22-L26) (Z80 ROM: `$1DF0–$1DFF`) leest het VRAM-geheugenadres van de copyrighttekst ("AMSTAR ELECTRONICS CORP.") op offset `0x31D` en controleert of de ROM niet gekraakt of gewijzigd is.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - geen
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`state_5_game_over_text`](state-endings.md#state_5_game_over_text) — [`state_endings.c#L93`](../../state_endings.c#L93)
