# Phoenix Animation Trajectories & Prescribed Movement Patterns (`animation-trajectory.md`)

Dit document bevat een diepgaande Knowledge Graph-analyse van **voorgeschreven bewegingspatronen, vector-tabellen, Z80 ROM-clusters, ROM-adressen, RAM-datastructuren en AI-vliegscripten** in de *Phoenix* Arcade-codebase. De classificatie als **gesloten lus** of **open traject** is afgeleid uit de ROM-vectoren; de directory bevat 78 SVG-bestanden, waaronder patroonweergaven en overzichtsanimaties.

---

## Inhoudsopgave
1. [Overzicht Vliegpatroon-architectuur & Z80 Geheugen-lus](#1-overzicht-vliegpatroon-architectuur--z80-geheugen-lus)
2. [Verschil tussen Gesloten Lus en Open Traject Patronen](#2-verschil-tussen-gesloten-lus-en-open-traject-patronen)
3. [Waarom Verschillende Clusters & Hoofdstukindeling?](#3-waarom-verschillende-clusters--hoofdstukindeling)
4. [Alien Cluster A Patterns — Wave 1 & 3 Formaties (Patronen 01 t/m 18)](#4-alien-cluster-a-patterns--wave-1--3-formaties-patronen-01-tm-18)
5. [Alien Cluster B Patterns — Breakout & Escorts (Patronen 19 t/m 36)](#5-alien-cluster-b-patterns--breakout--escorts-patronen-19-tm-36)
6. [Vogel Vliegtrajecten & AI Behavior Scripts](#6-vogel-vliegtrajecten--ai-behavior-scripts)
7. [Moederschip & Attract Mode Bewegingspaden](#7-moederschip--attract-mode-bewegingspaden)
8. [Uitvoerings-lus & Mermaid Diagram](#8-uitvoerings-lus--mermaid-diagram)

---

## 1. Overzicht Vliegpatroon-architectuur & Z80 Geheugen-lus

In de *Phoenix* arcadehardware worden bewegingen van vijanden (aliens, vogels en het moederschip) niet willekeurig berekend via dynamische natuurkunde, maar aangestuurd via **statische vectoriële opzoektabellen** uit het Z80 ROM opgeslagen in [`phoenix_tables.c`](../../phoenix_tables.c) / [`phoenix_tables.h`](../../phoenix_tables.h).

### **Geheugenkaart & RAM-Datastructuren**
Elke actieve entiteit op het scherm gebruikt een specifieke geheugenstructuur in het Arcade RAM (`$4000–$4BFF`):

| RAM Adres / Offset | Variabele / Register | Functionele Omschrijving |
|---|---|---|
| `$43C0–$43DF` | `PlayerShipX` / Bullet Grid | Spelerschip coördinaten en actieve spelerkogels |
| `$4360–$437F` | `M436D`, `M436E`, `M436F` | Vogel AI-fase registers, afdaaldoelen en willekeurige duik-drempels |
| `$4B50–$4B6F` | `AlienPointerTable` | 16-bit RAM pointers die wijzen naar de actieve stap in een vliegpatroon |
| `$4800–$4B3F` | `BackgroundScreen` / VRAM | 90° geroteerde 32x32 tegelmatrix videobuffer (832 bytes per pagina) |

### **Vector-transformatie & Indexering**
Een RAM-pointer (bijv. op offset `$4B50`) leest per frame een stap-byte uit het ROM. Deze byte fungeert als index in de richtingstabel [`phoenix_alien_direction_vectors`](../../phoenix_tables.h#L162) (ROM `$1700–$173F`):

```math
\mathrm{VectorAddress} = \mathtt{0x1700} + (\mathtt{StepByte}\ \mathrm{AND}\ \mathtt{0x1F}) \times 2
```

De gelezen twee bytes leveren het paarsgewijze richtingsverschil $(\Delta X, \Delta Y)$ op:
```math
X_{\mathrm{nieuw}} = X_{\mathrm{oud}} + \Delta X
```

```math
Y_{\mathrm{nieuw}} = Y_{\mathrm{oud}} + \Delta Y
```

---

### **Bovenliggende Hoofd-Animatie van alle Vliegtrajecten**
Onderstaande geanimeerde SVG toont de gelijktijdige werking van het hele Arcade vector-systeem: de alien duiklus (cyan), de vogel sinus-duik met bommenwerpen (roze/geel) en het gestage moederschip daal-traject (groen):

![Phoenix Master Flight Path Overview](../00_overview_flight_patterns.svg)

#### **Knowledge Graph Koppelingen**
* **Relevante C-bestanden:**
  - [`phoenix_tables.c`](../../phoenix_tables.c) $\rightarrow$ [`phoenix-tables.md`](../../c-annotated/nl/phoenix-tables.md)
  - [`alien_logic.c`](../../alien_logic.c) $\rightarrow$ [`alien-logic.md`](../../c-annotated/nl/alien-logic.md)
  - [`bird_logic.c`](../../bird_logic.c) $\rightarrow$ [`bird-logic.md`](../../c-annotated/nl/bird-logic.md)
  - [`bird_wave_behavior.c`](../../bird_wave_behavior.c) $\rightarrow$ [`bird-wave-behavior.md`](../../c-annotated/nl/bird-wave-behavior.md)
  - [`attract_mode.c`](../../attract_mode.c) $\rightarrow$ [`attract-mode.md`](../../c-annotated/nl/attract-mode.md)

---

## 2. Verschil tussen Gesloten Lus en Open Traject Patronen

De vector-integratie van de hieronder behandelde ROM-patronen onderscheidt **twee typen bewegingspatronen** in de *Phoenix*-engine:

| Eigenschap | 🔄 Gesloten Lus Patronen (Closed Loops) | ↗️ Open Traject Patronen (Open Trajectories) |
|---|---|---|
| **Netto Verplaatsing** | $\sum \Delta X = 0 \quad \text{en} \quad \sum \Delta Y = 0$ | $\sum \Delta X \neq 0 \quad \text{of} \quad \sum \Delta Y \neq 0$ |
| **Vorm & Traject** | De entiteit verlaat zijn formatiepositie $(X_0, Y_0)$, maakt een cirkel-, ovaal- of 8-vormige lus, en **keert exact terug op $(X_0, Y_0)$**. | De entiteit voert een verplaatsing of breakout-sprint uit over het scherm (bijv. naar beneden of schuin zijwaarts). |
| **Typische Patronen** | Cluster A Patronen `01`, `02`, `07`, `10`, `11`, `12` & Cluster B Patroon `23`. | Cluster A Patronen `03`, `04`, `05`, `06`, `08`, `09`, `13–18` & Cluster B Patronen `19–22`, `24–36`. |
| **Einde-Lus Verwerking** | Bij de `0x00` terminator start het patroon naadloos opnieuw vanaf het begin op hetzelfde ankeradres. | Bij de `0x00` terminator of schermrand activeert de game-engine een breakout-herpositionering ([`l3028`](../../c-annotated/nl/alien-logic.md#l3028)) of her-oriëntatie ([`l3672_aim`](../../c-annotated/nl/bird-wave-behavior.md#l3672_aim)). |

---

## 3. Waarom Verschillende Clusters & Hoofdstukindeling?

### **1. Waarom gescheiden ROM "Clusters"?**
De C-port modelleert de bewegingsdata als twee afzonderlijke ROM-bereiken ("clusters"). De hieronder beschreven indeling is afgeleid uit die tabellen en hun ASM-adresranges:

1. **Cluster A (ROM `$1000–$13FF` / 1024 bytes):**
   - **Locatie:** ROM-chip 1 op `$1000`.
   - **Functie:** Bevat **Patronen 01 t/m 18** (`phoenix_alien_movement_cluster_a`). Dit zijn voornamelijk gesloten formatielussen die gebruikt worden tijdens **Alien Wave 1 en Wave 3** (de synchrone zwermformaties met kleine en middelgrote aliens).
   - **Initialisatie:** De tabel [`phoenix_alien_layout_pointers`](../../phoenix_tables.h#L139) initialiseert de alien-pointers standaard naar het begin van deze pagina op `$1000`.

2. **Cluster B (ROM `$2C00–$2FFF` / 1024 bytes):**
   - **Locatie:** ROM-chip 3 op `$2C00`.
   - **Functie:** Bevat **Patronen 19 t/m 36** (`phoenix_alien_movement_cluster_b`). Dit zijn voornamelijk open breakout-patronen die gebruikt worden door **Breakout-aliens** (aliens die uit de formatie losbreken) en de **Moederschip-escortgolven** (Levels 9, 10 en 11).
   - **Breakout-mechanisme:** De breakout-scheduler [`l3028`](../../c-annotated/nl/alien-logic.md#l3028) in `alien_logic.c` springt bij een aanval direct naar de ingangsadressen `$2E00` en `$2E40` in Cluster B.

---

### **2. Waarom deze Hoofdstukindeling? (Game Engine Subsystemen)**
De indeling in dit document volgt exact de 4 fysieke game-entiteit subsystemen van de Arcade Z80 engine:

- **Hoofdstuk 4 (Alien Cluster A):** Formatie-aliens in Waves 1 & 3.
- **Hoofdstuk 5 (Alien Cluster B):** Losbrekende aanvals-aliens & moederschip-escorts.
- **Hoofdstuk 6 (Vogel AI Scripts & Duik-spawns):** De vogelzwermen in Waves 5 & 7, inclusief ei-uitbroeden, klimmen, vleugelwieken en sinus-duikbommenwerpers.
- **Hoofdstuk 7 (Moederschip & Attract Mode):** De 26x9 moederschip-tegelmatrix, Attract Mode intro-vogel en achtergronddecoraties.

---

## 4. Alien Cluster A Patterns — Wave 1 & 3 Formaties (Patronen 01 t/m 18)

### **Gedetailleerde Analyse Cluster A**
- **ROM Adresbereik:** `$1000–$13FF` (1024 bytes) in [`phoenix_tables.c`](../../phoenix_tables.c#L73).
- **Structurele Opbouw:** 18 gesloten-lus & open traject patronen (`T1020` t/m `T13D0`), elk bestaand uit een reeks van vector-indices afgesloten met `0x00` en opgevuld met `0xFF`.
- **Gesloten vs Open:** Patronen `01`, `02`, `07`, `10`, `11`, `12` zijn **Gesloten Lussen** ($\sum \Delta = (0,0)$). Patronen `03`, `04`, `05`, `06`, `08`, `09`, `13–18` zijn **Open Trajecten**.

### **Overzichts-animatie Cluster A**
![Alien Cluster A Overzichts-Animatie](../07_alien_closed_loop_cluster_a.svg)

---

### **Gedetailleerde Onderverdeling per Patroon (01 t/m 18)**

#### Patronen 01 t/m 06
| Patroon 01 (ROM $1020, 64b — Gesloten) | Patroon 02 (ROM $1064, 64b — Gesloten) |
|---|---|
| ![Alien Cluster A Patroon 01](../cluster_a/pattern_01.svg) | ![Alien Cluster A Patroon 02](../cluster_a/pattern_02.svg) |

| Patroon 03 (ROM $10A8, 40b — Open) | Patroon 04 (ROM $10D4, 40b — Open) |
|---|---|
| ![Alien Cluster A Patroon 03](../cluster_a/pattern_03.svg) | ![Alien Cluster A Patroon 04](../cluster_a/pattern_04.svg) |

| Patroon 05 (ROM $1100, 43b — Open) | Patroon 06 (ROM $1130, 43b — Open) |
|---|---|
| ![Alien Cluster A Patroon 05](../cluster_a/pattern_05.svg) | ![Alien Cluster A Patroon 06](../cluster_a/pattern_06.svg) |

---

#### Patronen 07 t/m 12
| Patroon 07 (ROM $1160, 64b — Gesloten) | Patroon 08 (ROM $11A4, 40b — Open) |
|---|---|
| ![Alien Cluster A Patroon 07](../cluster_a/pattern_07.svg) | ![Alien Cluster A Patroon 08](../cluster_a/pattern_08.svg) |

| Patroon 09 (ROM $11D0, 45b — Open) | Patroon 10 (ROM $1200, 64b — Gesloten) |
|---|---|
| ![Alien Cluster A Patroon 09](../cluster_a/pattern_09.svg) | ![Alien Cluster A Patroon 10](../cluster_a/pattern_10.svg) |

| Patroon 11 (ROM $1244, 64b — Gesloten) | Patroon 12 (ROM $1288, 64b — Gesloten) |
|---|---|
| ![Alien Cluster A Patroon 11](../cluster_a/pattern_11.svg) | ![Alien Cluster A Patroon 12](../cluster_a/pattern_12.svg) |

---

#### Patronen 13 t/m 18
| Patroon 13 (ROM $12CA, 53b — Open) | Patroon 14 (ROM $1300, 36b — Open) |
|---|---|
| ![Alien Cluster A Patroon 13](../cluster_a/pattern_13.svg) | ![Alien Cluster A Patroon 14](../cluster_a/pattern_14.svg) |

| Patroon 15 (ROM $1328, 38b — Open) | Patroon 16 (ROM $1354, 69b — Open) |
|---|---|
| ![Alien Cluster A Patroon 15](../cluster_a/pattern_15.svg) | ![Alien Cluster A Patroon 16](../cluster_a/pattern_16.svg) |

| Patroon 17 (ROM $139C, 49b — Open) | Patroon 18 (ROM $13D0, 43b — Open) |
|---|---|
| ![Alien Cluster A Patroon 17](../cluster_a/pattern_17.svg) | ![Alien Cluster A Patroon 18](../cluster_a/pattern_18.svg) |

---

## 5. Alien Cluster B Patterns — Breakout & Escorts (Patronen 19 t/m 36)

### **Gedetailleerde Analyse Cluster B**
- **ROM Adresbereik:** `$2C00–$2FFF` (1024 bytes) in [`phoenix_tables.c`](../../phoenix_tables.c#L423).
- **Structurele Opbouw:** 18 patronen (patronen 19 t/m 36) voornamelijk bestaand uit open breakout-trajecten voor losbrekende aliens en moederschip-escortwaves.
- **Gesloten vs Open:** Patroon `23` is een **Gesloten Lus** ($\sum \Delta = (0,0)$). Patronen `19–22`, `24–36` zijn **Open Trajecten** met netto verplaatsingen over het scherm.

### **Overzichts-animatie Cluster B**
![Alien Cluster B Overzichts-Animatie](../08_alien_breakout_cluster_b.svg)

---

### **Gedetailleerde Onderverdeling per Patroon (19 t/m 36)**

#### Patronen 19 t/m 24
| Patroon 19 (ROM $2C00, 48b — Open) | Patroon 20 (ROM $2C34, 86b — Open) |
|---|---|
| ![Alien Cluster B Patroon 19](../cluster_b/pattern_19.svg) | ![Alien Cluster B Patroon 20](../cluster_b/pattern_20.svg) |

| Patroon 21 (ROM $2C90, 53b — Open) | Patroon 22 (ROM $2CC8, 54b — Open) |
|---|---|
| ![Alien Cluster B Patroon 21](../cluster_b/pattern_21.svg) | ![Alien Cluster B Patroon 22](../cluster_b/pattern_22.svg) |

| Patroon 23 (ROM $2D00, 64b — Gesloten) | Patroon 24 (ROM $2D44, 64b — Open) |
|---|---|
| ![Alien Cluster B Patroon 23](../cluster_b/pattern_23.svg) | ![Alien Cluster B Patroon 24](../cluster_b/pattern_24.svg) |

---

#### Patronen 25 t/m 30
| Patroon 25 (ROM $2D88, 52b — Open) | Patroon 26 (ROM $2DC0, 50b — Open) |
|---|---|
| ![Alien Cluster B Patroon 25](../cluster_b/pattern_25.svg) | ![Alien Cluster B Patroon 26](../cluster_b/pattern_26.svg) |

| Patroon 27 (ROM $2E00, 28b — Breakout) | Patroon 28 (ROM $2E20, 28b — Breakout) |
|---|---|
| ![Alien Cluster B Patroon 27](../cluster_b/pattern_27.svg) | ![Alien Cluster B Patroon 28](../cluster_b/pattern_28.svg) |

| Patroon 29 (ROM $2E40, 40b — Open) | Patroon 30 (ROM $2E6C, 32b — Open) |
|---|---|
| ![Alien Cluster B Patroon 29](../cluster_b/pattern_29.svg) | ![Alien Cluster B Patroon 30](../cluster_b/pattern_30.svg) |

---

#### Patronen 31 t/m 36
| Patroon 31 (ROM $2E90, 49b — Open) | Patroon 32 (ROM $2EC4, 48b — Open) |
|---|---|
| ![Alien Cluster B Patroon 31](../cluster_b/pattern_31.svg) | ![Alien Cluster B Patroon 32](../cluster_b/pattern_32.svg) |

| Patroon 33 (ROM $2F00, 48b — Open) | Patroon 34 (ROM $2F34, 46b — Open) |
|---|---|
| ![Alien Cluster B Patroon 33](../cluster_b/pattern_33.svg) | ![Alien Cluster B Patroon 34](../cluster_b/pattern_34.svg) |

| Patroon 35 (ROM $2F64, 50b — Escort) | Patroon 36 (ROM $2FA0, 94b — Escort) |
|---|---|
| ![Alien Cluster B Patroon 35](../cluster_b/pattern_35.svg) | ![Alien Cluster B Patroon 36](../cluster_b/pattern_36.svg) |

---

## 6. Vogel Vliegtrajecten & AI Behavior Scripts

### **Gedetailleerde Analyse Vogel AI Subsysteem**
Het vogel-AI subsysteem in [`bird_wave_behavior.c`](../../bird_wave_behavior.c) en [`bird_logic.c`](../../bird_logic.c) wordt aangestuurd door 4 gekoppelde ROM-geheugentabellen:

1. **`phoenix_bird_behaviour_scripts` (ROM `$3F00–$3F7F` / 128 bytes):**
   - 16 AI-patroonscripts van elk 8 bytes (twee datawoorden + twee vervolg-routine adressen).
   - Aangeroepen door [`update_bird_behavior`](../../c-annotated/nl/bird-wave-behavior.md#update_bird_behavior).
   - **Functies in C:**
     - `l35e0_descend()`: Afdaalfase waarbij de vogel naar beneden versnelt en op de speler richt.
     - `l3628_climb()`: Klimfase waarbij de vogel in trappen naar boven stijgt.
     - `l36c0_animate()`: Vleugelwieken animatie-timer.
     - `l36d2_grow()` / `l36ea_grow()` / `l370a_grow_or_dive()`: Ei-uitbroeden, transformatie naar 4x4 matrix-vogel en activatie van duikbommenwerpers.

2. **`phoenix_bird_dive_spawn_positions` (ROM `$3DC0–$3DDF` / 32 bytes):**
   - 32 voorgeschreven start- en aanvalsposities (`(sp_x, sp_y)` paarsgewijs opgeslagen).
   - Aangeroepen door [`try_spawn_bird_dive_bomb`](../../c-annotated/nl/bird-wave-behavior.md#try_spawn_bird_dive_bomb).

---

### **1. Vogel AI Behavior Scripts (ROM `$3F00–$3F7F`) — 16 Gedetailleerde AI-Scripts**

#### Scripts 00 t/m 07
| Script 00 (ROM $3F00 — Formatie Idle) | Script 01 (ROM $3F08 — Broed/Wieken) |
|---|---|
| ![Bird Script 00](../bird_scripts/bird_script_00.svg) | ![Bird Script 01](../bird_scripts/bird_script_01.svg) |

| Script 02 (ROM $3F10 — Steile Duik) | Script 03 (ROM $3F18 — Sluitvlucht) |
|---|---|
| ![Bird Script 02](../bird_scripts/bird_script_02.svg) | ![Bird Script 03](../bird_scripts/bird_script_03.svg) |

| Script 04 (ROM $3F20 — Groeiscript Init) | Script 05 (ROM $3F28 — Wieg/Klim) |
|---|---|
| ![Bird Script 04](../bird_scripts/bird_script_04.svg) | ![Bird Script 05](../bird_scripts/bird_script_05.svg) |

| Script 06 (ROM $3F30 — Duikbommenwerper) | Script 07 (ROM $3F38 — Diepe Aanvalslus) |
|---|---|
| ![Bird Script 06](../bird_scripts/bird_script_06.svg) | ![Bird Script 07](../bird_scripts/bird_script_07.svg) |

---

#### Scripts 08 t/m 15
| Script 08 (ROM $3F40 — Grote Vogel Matrix) | Script 09 (ROM $3F48 — Zware Afdaling) |
|---|---|
| ![Bird Script 08](../bird_scripts/bird_script_08.svg) | ![Bird Script 09](../bird_scripts/bird_script_09.svg) |

| Script 10 (ROM $3F50 — Aanvals-Sinus) | Script 11 (ROM $3F58 — Escort Bommen) |
|---|---|
| ![Bird Script 10](../bird_scripts/bird_script_10.svg) | ![Bird Script 11](../bird_scripts/bird_script_11.svg) |

| Script 12 (ROM $3F60 — Moederschip Escort 1) | Script 13 (ROM $3F68 — Moederschip Escort 2) |
|---|---|
| ![Bird Script 12](../bird_scripts/bird_script_12.svg) | ![Bird Script 13](../bird_scripts/bird_script_13.svg) |

| Script 14 (ROM $3F70 — Sluit-Escort) | Script 15 (ROM $3F78 — Terminal Duik) |
|---|---|
| ![Bird Script 14](../bird_scripts/bird_script_14.svg) | ![Bird Script 15](../bird_scripts/bird_script_15.svg) |

---

### **2. Vogel Duik- & Launch-posities (ROM `$3DC0–$3DDF`) — 16 Scherm-Coördinaten**

| Launch 00 & 01 (ROM $3DC0 & $3DC2) | Launch 02 & 03 (ROM $3DC4 & $3DC6) |
|---|---|
| ![Spawn 00](../bird_dive_spawns/dive_spawn_00.svg) | ![Spawn 02](../bird_dive_spawns/dive_spawn_02.svg) |

| Launch 04 & 05 (ROM $3DC8 & $3DCA) | Launch 06 & 07 (ROM $3DCC & $3DCE) |
|---|---|
| ![Spawn 04](../bird_dive_spawns/dive_spawn_04.svg) | ![Spawn 06](../bird_dive_spawns/dive_spawn_06.svg) |

| Launch 08 & 09 (ROM $3DD0 & $3DD2) | Launch 10 & 11 (ROM $3DD4 & $3DD6) |
|---|---|
| ![Spawn 08](../bird_dive_spawns/dive_spawn_08.svg) | ![Spawn 10](../bird_dive_spawns/dive_spawn_10.svg) |

| Launch 12 & 13 (ROM $3DD8 & $3DDA) | Launch 14 & 15 (ROM $3DDC & $3DDE) |
|---|---|
| ![Spawn 12](../bird_dive_spawns/dive_spawn_12.svg) | ![Spawn 14](../bird_dive_spawns/dive_spawn_14.svg) |

---

## 7. Moederschip & Attract Mode Bewegingspaden

### **1. `phoenix_mothership_tile_page` (ROM `$1D00–$1DFF`)**
- **Beschrijving:** De voorgeschreven 26x9 tegel-matrix en daalsnelheids-tabel voor de gestage neerwaartse beweging van het moederschip in [`mothership_impl.c`](../../mothership_impl.c) en [`mothership_logic.c`](../../mothership_logic.c).

![Moederschip Daal-Traject](../09_mothership_descent_trajectory.svg)

---

### **2. `phoenix_intro_bird_anim_frames` (ROM `$233A–$2359`)**
- **Beschrijving:** Voorgeschreven frame- en bewegingsreeks van 32 stappen voor de vogel die over het titel-scherm zweeft in Attract Mode ([`attract-mode.md`](../../c-annotated/nl/attract-mode.md)).
- **Aanroep:** [`draw_intro_bird_animation_frame`](../../c-annotated/nl/attract-mode.md#draw_intro_bird_animation_frame) in `attract_mode.c`.

![Intro Splash Vogel Traject](../06_intro_splash_bird.svg)

---

## 8. Uitvoerings-lus & Mermaid Diagram

```mermaid
graph TD
  A["Level Dispatcher (state_play.c)"] --> B["Selecteer Vliegpatroon Pointer"]
  B --> C{"Entiteit Type"}
  
  C -- "Alien Wave 1/3 (Cluster A)" --> D["phoenix_alien_movement_cluster_a (0x1000)"]
  C -- "Alien Breakout/Escort (Cluster B)" --> E["phoenix_alien_movement_cluster_b (0x2C00)"]
  C -- "Vogel AI Script" --> F["phoenix_bird_behaviour_scripts (0x3F00)"]
  C -- "Moederschip Daalpad" --> G["phoenix_mothership_tile_page (0x1D00)"]
  
  D --> H["Vector Index (dx, dy) in phoenix_alien_direction_vectors"]
  E --> H
  F --> I["Duik-positie in phoenix_bird_dive_spawn_positions"]
  
  H --> J["Update RAM Ankeradres (DE / 0x43C2 / 0x4B50)"]
  I --> J
  G --> J
  
  J --> K["Sprite Rendering Engine (sprite_rendering.c)"]
  K --> L["Scherm VRAM Update (0x4000-0x433F)"]
```
