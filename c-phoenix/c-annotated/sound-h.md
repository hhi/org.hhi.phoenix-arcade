# Sound Engine Declarations (`sound.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat de geannoteerde header-declaraties voor [`sound.h`](../sound.h).

---

## Declaraties & Koppelingen
- `sound_init(void)`: Initialiseert alle audio-generatoren en resamplers.
- `sound_set_frame_sample_index(uint16_t sample_index)`: Stelt de sample-index offset in voor latch-updates.
- `sound_write_control_a(uint8_t val)` / `sound_write_control_b(uint8_t val)`: Registreert poort $6000/$6800 latch updates.
- `sound_render_frame(int16_t* out)`: Rendert 1 frame audio (ca. 735 samples bij 44.1kHz).

#### **Knowledge Graph Koppelingen**
* **Overeenkomstige C-implementatie:** [`sound.c`](../sound.c) $\rightarrow$ [`sound.md`](sound.md)
