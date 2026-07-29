# Arcade RAM Memory Map (`phoenix_state.h`) - C-Annotated Knowledge Graph Documentatie

Dit document bevat een geannoteerde analyse van de centrale RAM-geheugenkaart in [`phoenix_state.h`](../../phoenix_state.h). De `PhoenixState` structuur bevat de exacte, gepackte 3KB geheugenspiegeling van het Arcade RAM (`$4000–$4BFF`).

---

## Inhoudsopgave
1. [Geheugenkaart Structuur Overview](#1-geheugenkaart-structuur-overview)
2. [VRAM & Scherm-buffers](#2-vram--scherm-buffers)
3. [Speler- & Kogel-status (Grid $43C0–$43DF)](#3-speler--kogel-status-grid-43c043df)
4. [Score-, Levens- & Geluids-RAM ($4380–$43A0)](#4-score--levens--geluids-ram-438043a0)
5. [Level- & Besturingsvariabelen](#5-level--besturingsvariabelen)

---

## 1. Geheugenkaart Structuur Overview

### `PhoenixState`
#### **Beschrijving**
De structuur [`PhoenixState`](../../phoenix_state.h#L8-L349) is de centrale toestand van de game. Elk veld komt exact overeen met een 8-bits RAM-locatie in de oorspronkelijke Z80 hardware architecture.

#### **Knowledge Graph Koppelingen**
* **Aangeroepen door (Incoming Calls / Backlinks):**
  - Vrijwel alle C-functies in `c-phoenix` raadplegen en muteren de globale instantie `extern PhoenixState state;`.

---

## 2. VRAM & Scherm-buffers

### `ForegroundScreen[832]` (`$4000–$433F`)
- 26 kolommen x 32 rijen voorgrondscherm VRAM.
- Bevat de tegel-ID's van actieve karakters, scores, spelerschip, kogels en zwerm-aliens.

---

## 3. Speler- & Kogel-status (Grid `$43C0–$43DF`)

### Spelerschip & Kogelgeheugens
- `PlayerState` (`$4360`): Bit 3 (`0x08`) geeft aan of spelersbeweging actief is.
- `PlayerShipX`, `PlayerShipY`: Spelerschipcoördinaten.
- `PlayerBulletState`, `PlayerBulletX`, `PlayerBulletY`: Coördinaten en status van de primaire spelerkogel.
- `AbovePlayerBulletState`, `AbovePlayerBulletX`, `AbovePlayerBulletY`: Coördinaten en status van de secundaire spelerkogel (level 3/B).
- `ShieldCount` (`$43A6`): Aftelteller van het speler-krachtveld (5 seconden actieftijd).

---

## 4. Score-, Levens- & Geluids-RAM (`$4380–$43A0`)

### Scores & Audio Latches
- `Score1high..Score1low` (`$4381–$4383`): 3-byte packed-BCD score voor Player 1.
- `Score2high..Score2low` (`$4385–$4387`): 3-byte packed-BCD score voor Player 2.
- `HiScorehigh..HiScorelow` (`$4389–$438B`): 3-byte packed-BCD High Score.
- `SoundControlA` (`$438C`) / `SoundControlB` (`$438D`): Schaduw-spiegels voor hardware-geluidspoorten `$6000` en `$6800`.
- `Player1Lives` (`$4390`) / `Player2Lives` (`$4391`): Resterend aantal levens.
- `CoinCount` (`$438F`): Aantal geaccepteerde munten/credits.

---

## 5. Level- & Besturingsvariabelen

### Spel- & Besturingstoestanden
- `GameState` (`$43A4`): Huidige status in de toestandsmachine (States 0 t/m 7, zie [`game-constants-h.md`](game-constants-h.md)).
- `LevelAndRound` (`$43B8`): Hoge nibble is de ronde-teller, lage nibble is het levelpatroon.
- `AliensLeft` (`$43BA`): Aantal resterende aliens in de wave.
- `BirdsLeft` (`$43B9`): Aantal resterende vogels in de wave.
- `B4BD2`: Verticale scroll-offset voor de vogel-laag.
