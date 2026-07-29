# Per-Frame Sound Dispatcher (`sound_dispatcher.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`sound_dispatcher.c`](../../sound_dispatcher.c). Deze module implementeert de originele Z80 Z80-routine `$3A10–$3B5B`, die in elk frame de juiste geluidseffecten (sirenes, schoten, speler-explosies, vogelkweel en moederschip-brom) berekent en opslaat in de hardware-latches `SoundControlA` en `SoundControlB`.

---

## Inhoudsopgave
1. [Master Sound Dispatcher](#1-master-sound-dispatcher)
2. [Level-Geconcentreerde Geluidseffecten](#2-level-geconcentreerde-geluidseffecten)
3. [Speler- & Explosie-effecten](#3-speler--explosie-effecten)

---

## 1. Master Sound Dispatcher

### `l3a10` & `l3b43`
#### **Beschrijving**
- [`l3a10`](../../sound_dispatcher.c#L265-L271) (Z80 ROM: `$3A10–$3A1C`) is het startpunt dat aan de start van een game (`LevelAndRound == 0`) de beroemde intro-melodie *Romance de Amor / Estudio* triggert (`SoundControlB = 0xCF`), of per frame `l3b43` aanroept.
- [`l3b43`](../../sound_dispatcher.c#L247-L257) (Z80 ROM: `$3B43–$3B5B`) doorloopt in vastgestelde volgorde alle vervaltellers en effect-stappen voor de huidige frame-update.

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`l23d6`](#l23d6) — [`sound_dispatcher.c#L249`](../../sound_dispatcher.c#L249)
  - [`l27bd`](#l27bd) — [`sound_dispatcher.c#L254`](../../sound_dispatcher.c#L254)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - [`update_scores_and_sound`](scoring.md#update_scores_and_sound) — [`scoring.c#L194`](../../scoring.c#L194)

---

## 2. Level-Geconcentreerde Geluidseffecten

### `l23d6` & `l3a98_scan`
#### **Beschrijving**
- [`l23d6`](../../sound_dispatcher.c#L21-L29) (Z80 ROM: `$23D6–$23FB`) schakelt afhankelijk van het levelpatroon naar de specifieke geluidsroutines: alien-sirene scan ([`l3a98_scan`](#l3a98_scan)), vogel-kadans ([`l3ad0`](#l3ad0)) of moederschip-brom ([`l3b02`](#l3b02)).
- [`l3a98_scan`](../../sound_dispatcher.c#L154-L170) (Z80 ROM: `$3A98–$3ACA`) telt de actieve aliens en stelt de dynamische toonhoogte van de alien-sirene in.

---

## 3. Speler- & Explosie-effecten

### `l27bd`
#### **Beschrijving**
De functie [`l27bd`](../../sound_dispatcher.c#L35-L53) (Z80 ROM: `$27BD–$27EE`) beheert de ruis- en toonafval van het schotgeluid (`BulletTriggered`) en de spelersexplosie (`ParticleExplosion`).
