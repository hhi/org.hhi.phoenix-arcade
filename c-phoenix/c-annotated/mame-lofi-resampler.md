# MAME Lo-Fi Stream Resampler (`mame_lofi_resampler.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de functies in [`mame_lofi_resampler.c`](../mame_lofi_resampler.c). Deze module implementeert MAME's 4-punts kubische interpolatie (cubic interpolation) resampler om bron-audio (zoals 23.8kHz TMS-muziek of 96kHz discreet-audio) om te zetten naar de 44.1kHz SDL2-afspeelfrequentie.

---

## 1. Resampler Initialisatie & Sampling

### `mame_lofi_resampler_init` & `mame_lofi_resampler_next`
#### **Beschrijving**
- [`mame_lofi_resampler_init`](../mame_lofi_resampler.c#L40-L46): Genereert de process-globale interpolatie-tabel `g_interp` en berekent de vaste-kommaberekening stapgrootte (`r->step`).
- [`mame_lofi_resampler_next`](../mame_lofi_resampler.c#L66-L82): Berekent de gewogen 4-punts kubische interpolatie over de sample-window `s0..s3` en schuift de bron-samples op bij phase-overflow.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `build_interpolation` — [`mame_lofi_resampler.c#L15`](../mame_lofi_resampler.c#L15)
  - `read_source` — [`mame_lofi_resampler.c#L53`](../mame_lofi_resampler.c#L53)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`sound_init`](sound.md#sound_init) — [`sound.c#L60`](../sound.c#L60), [`L62`](../sound.c#L62)
  - [`sound_render_frame`](sound.md#sound_render_frame) — [`sound.c#L176`](../sound.c#L176), [`L177`](../sound.c#L177)
