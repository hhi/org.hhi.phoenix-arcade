# TMS3615 / MM6221AA Synthesizer (`tms36xx.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`tms36xx.c`](../../tms36xx.c). Deze module emuleert de Texas Instruments TMS3615 / MM6221AA custom orgelsynthesizer-chip die de achtergrondmelodieën van *Phoenix* afspeelt.

---

## Inhoudsopgave
1. [TMS36XX Chip Initialisatie](#1-tms36xx-chip-initialisatie)
2. [Melodie Selectie & Rendering](#2-melodie-selectie--rendering)

---

## 1. TMS36XX Chip Initialisatie

### `tms36xx_init`
#### **Beschrijving**
De functie [`tms36xx_init`](../../tms36xx.c#L200-L240) stelt de 12 stemmen (6 actieve stemmen + 6 afvallende stemmen), basisfrequentie (372Hz), samplefrequentie (23.808kHz) en decay-tijden in voor het orgel-circuit.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - geen
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`sound_init`](sound.md#sound_init) — [`sound.c#L59`](../../sound.c#L59)

---

## 2. Melodie Selectie & Rendering

### `tms36xx_mm6221aa_tune_w` & `tms36xx_render_internal_sample`
#### **Beschrijving**
- [`tms36xx_mm6221aa_tune_w`](../../tms36xx.c#L247-L253) selecteert de actieve ingebouwde ROM-melodie (`g_tune1`, `g_tune2` of `g_tune3`).
- [`tms36xx_render_internal_sample`](../../tms36xx.c#L260-L287) rendert per sample de blokgolf-frequenties en uitdovings-enveloppen over de 12 stemmen.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `tune_table` — [`tms36xx.c#L127`](../../tms36xx.c#L127)
  - `tms36xx_decay` — [`tms36xx.c#L141`](../../tms36xx.c#L141)
  - `tms36xx_restart` — [`tms36xx.c#L160`](../../tms36xx.c#L160)
  - `tms36xx_tone` — [`tms36xx.c#L181`](../../tms36xx.c#L181)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`sound_render_frame`](sound.md#sound_render_frame) — [`sound.c#L176`](../../sound.c#L176)
