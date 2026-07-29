# MAME Lo-Fi Resampler Declarations (`mame_lofi_resampler.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat de geannoteerde header-declaraties voor [`mame_lofi_resampler.h`](../mame_lofi_resampler.h).

---

## Structuur & Declaraties
- `MameLofiResampler`: Bevat de stapgrootte (`step`), fase (`phase`) en de 4-punts sample-window `s0..s3`.
- `mame_lofi_resampler_init(...)`: Initialiseert de kubische resampler.
- `mame_lofi_resampler_next(...)`: Berekent de volgende hersamplede waarde.

#### **Knowledge Graph Koppelingen**
* **Overeenkomstige C-implementatie:** [`mame_lofi_resampler.c`](../mame_lofi_resampler.c) $\rightarrow$ [`mame-lofi-resampler.md`](mame-lofi-resampler.md)
