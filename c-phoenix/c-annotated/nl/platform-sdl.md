# SDL2 Platform Host (`platform_sdl.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`platform_sdl.c`](../../platform_sdl.c). Deze module bevat de hoofd-entrypoint van de applicatie, het SDL2-vensterbeheer, toetsenbordinvoer, VRAM-bankswapping en de audio/video 60Hz vblank synchronisatie.

---

## Inhoudsopgave
1. [Platform Host & Main Loop](#1-platform-host--main-loop)
2. [Hardware Emulatie & Bank-swapping](#2-hardware-emulatie--bank-swapping)

---

## 1. Platform Host & Main Loop

### `main`
#### **Beschrijving**
De functie `main` initialiseert de SDL2 subsystemen (video en audio), opent het Phoenix-arcadevenster (256x224 schaalbaar), start de audio-stream thread en de 60Hz vblank-timer, en start de Z80-geporteerde hoofdlus [`phoenix_main_loop`](hw-video-audio.md#phoenix_main_loop).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - [`sound_init`](sound.md#sound_init) — [`sound.c`](../../sound.c)
  - [`phoenix_main_loop`](hw-video-audio.md#phoenix_main_loop) — [`hw_video_audio.c`](../../hw_video_audio.c)

---

## 2. Hardware Emulatie & Bank-swapping

### `bank_swap_to` & `copy_memory_bank`
#### **Beschrijving**
- `bank_swap_to`: Emuleert het fysieke bank-swappen van de twee 3KB VRAM-banken (Player 1 RAM versus Player 2 RAM).
- [`copy_memory_bank`](../../platform_sdl.c#L90-L137) (Z80 ROM: `$0460–$049D`): Kopiëert de gedeelde header-rijen en achtergrondparameters tussen Player 1 en Player 2 banken.
