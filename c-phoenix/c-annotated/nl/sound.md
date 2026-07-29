# Sound Core & Mixer (`sound.c`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van alle functies in [`sound.c`](../../sound.c). Deze module regelt het synchroniseren, de events-queueing en het mixen van 44.1kHz audio (TMS3615 muziek, analoge discrete geluidseffecten en ruis).

---

## Inhoudsopgave
1. [Audio Initialisatie & Timing](#1-audio-initialisatie--timing)
2. [Hardware Latch Events](#2-hardware-latch-events)
3. [Per-frame Audio Renderer & Mixer](#3-per-frame-audio-renderer--mixer)

---

## 1. Audio Initialisatie & Timing

### `sound_init` & `sound_set_frame_sample_index`
#### **Beschrijving**
- [`sound_init`](../../sound.c#L58-L70): Initialiseert de TMS3615 muzieksynthesizer, analoge discreet-circuits en MAME lo-fi resamplers.
- [`sound_set_frame_sample_index`](../../sound.c#L77-L82): Bepaalt het exacte sample-tijdstip binnen een 60Hz videovraagframe waarin geluidscontroles veranderen.

---

## 2. Hardware Latch Events

### `sound_write_control_a` & `sound_write_control_b`
#### **Beschrijving**
Vangen schrijf-opdrachten op naar hardware-adressen `$6000` (Control A) en `$6800` (Control B) en plaatsen deze in een chronologische event-queue. Control B selecteert tevens de actieve melodie in de MM6221AA TMS3615 chip.

---

## 3. Per-frame Audio Renderer & Mixer

### `sound_render_frame`
#### **Beschrijving**
De functie [`sound_render_frame`](../../sound.c#L161-L190) genereert de PCM16 stereo/mono audio-buffer per videovraagframe (ca. 735 samples bij 44.1kHz) door de TMS-muziek, discrete effecten en custom ruissignalen in de juiste verhoudingen te mixen en te clippen (`clamp_pcm16`).

#### **Knowledge Graph Koppelingen**
* **Aanroepen (Outgoing Calls):**
  - `tms36xx_render_internal_sample` — [`tms36xx.c`](../../tms36xx.c)
  - `sound_discrete_step` / `sound_discrete_noise` — [`sound_discrete.c`](../../sound_discrete.c)
  - `mame_lofi_resampler_next` — [`mame_lofi_resampler.c`](../../mame_lofi_resampler.c)
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - `platform_audio_frame_hook` — [`platform_sdl.c`](../../platform_sdl.c)
