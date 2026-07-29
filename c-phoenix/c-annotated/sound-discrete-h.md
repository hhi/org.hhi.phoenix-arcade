# Discrete Sound Declarations (`sound_discrete.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat de geannoteerde header-declaraties voor [`sound_discrete.h`](../sound_discrete.h).

---

## Structuur & Declaraties
- `SoundDiscrete`: Bevat de 555-multivibratoren (`effect2_node33`, `effect2_node34`, etc.), RC-circuits, C24/C25 ruis-niveaus en het `poly18` LFSR-register.
- `sound_discrete_init(SoundDiscrete* sd)`: Initialisatie van de analoge discreet-knooppunten.
- `sound_discrete_step(...)`: Berekent 1 discreet sample.
- `sound_discrete_noise(...)`: Genereert ruis voor explosie-effecten.

#### **Knowledge Graph Koppelingen**
* **Overeenkomstige C-implementatie:** [`sound_discrete.c`](../sound_discrete.c) $\rightarrow$ [`sound-discrete.md`](sound-discrete.md)
