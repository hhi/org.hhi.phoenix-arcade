# Phoenix Animaties & Trajecten Gids (`c-phoenix/animations`)

Welkom in het centrale visuele archief van de *Phoenix* Arcade Game (`c-phoenix`). Deze map beantwoordt twee verschillende vragen: **waaruit** elk object bestaat, en **waarheen** het beweegt.

## Bronstatus

De bron van waarheid is, in deze volgorde: **Z80 ASM/ROM → C-port → geannoteerde analyse → deze visualisaties**. De SVG's maken ROM- en C-data inzichtelijk, maar vervangen die bron niet. Een conclusie zonder koppeling naar ASM, ROM of C-code is een interpretatie die nog gecontroleerd moet worden.

---

## 🗂️ Op deze pagina

- [Overkoepelende hoofd-animatie](#-overkoepelende-hoofd-animatie) — drie bewegingssoorten tegelijk
- [De vogel, fase voor fase](#-de-vogel-fase-voor-fase) — van ei tot volgroeide vogel
- [Waar alles uit bestaat](#-waar-alles-uit-bestaat) — karakters, kleurgroepen, spritesequenties
- [Vliegpatronen & trajecten](#-vliegpatronen--trajecten) — de banen die objecten volgen

---

## 🎬 Overkoepelende Hoofd-Animatie

Drie bewegingssoorten uit het spel tegelijk — een alien-zwenking, een vogel-duikbom en de daling van het moederschip — allemaal getekend uit de vectoren die in de ROM staan:

![Hoofd-animatie: een alien-zwenking, een vogel-duikbom met bom, en de gestage daling van het moederschip, gegenereerd uit de originele ROM-bewegingsvectoren](../00_overview_flight_patterns.svg)

Bronbestand: [`00_overview_flight_patterns.svg`](../00_overview_flight_patterns.svg).

---

## 🦅 De vogel, fase voor fase

Een Phoenix-vogel is niet één sprite. Hij komt uit het ei, groeit, valt aan en explodeert — zes onderscheiden animatiefases, elk gereconstrueerd uit de graphics-ROM:

| Ei komt uit | Kleine vogel wiekt | Volgroeide spanwijdte |
| --- | --- | --- |
| <img src="../01_egg_hatching.svg" width="230" alt="Een ei dat uitkomt tot een vogel"> | <img src="../02_small_bird_flapping.svg" width="230" alt="Een kleine vogel die met de vleugels wiekt, frame A en B"> | <img src="../03_grown_bird_matrix.svg" width="230" alt="De 4x4-matrix van vleugelstanden van een volgroeide vogel"> |
| **Duikaanval** | **Explosie en bonus** | **Daling moederschip** |
| <img src="../04_dive_bombing_attack.svg" width="230" alt="Een vogel die op de speler duikt en een bom laat vallen"> | <img src="../05_bird_explosion_bonus.svg" width="230" alt="Een vogel die uiteenspat in deeltjes met 500 punten bonus"> | <img src="../09_mothership_descent_trajectory.svg" width="230" alt="Het moederschip dat langs zijn vaste traject daalt"> |

📄 **[`bird-animations.md`](bird-animations.md)** — alle zes fases in detail, met de RAM-slots en ROM-routines erachter.

---

## 🔡 Waar alles uit bestaat

Phoenix heeft geen sprite-engine. Elk object op het scherm is een handvol **8×8-karakters** die naar het schermgeheugen worden geschreven, en het karakternummer bepaalt zélf de kleur — bit 5-7 kiezen een van de acht kleurgroepen in de PROM-tabel. Daarom lijkt elk blok van 32 karakters op één familie: letters, cijfers, het spelerschip, de vogels, explosies, het schild.

Er zijn twee onafhankelijke sets van 256 karakters. De voorgrondset bevat de speler, de aliens, de explosies en het schild; de achtergrondset bevat het sterrenveld, de planeet, de vogels en het moederschip.

Objectmaten liggen niet vast. Een kleine familie **drawNxN-routines** schrijft twee karakters onder elkaar in een kolom en stapt dan zijwaarts, en voor sommige objecten kiest `sprite_rendering.c` tijdens runtime `1x1`, `2x1`, `1x2` of `2x2` op basis van het control-byte — dezelfde tabel kan dus verschillende vormen opleveren, afhankelijk van wat het object doet.

📄 **[`animation-sequences.md`](animation-sequences.md)** — de volledige karakterset, elke spritesequentie frame voor frame met de karaktercodes, de bewegende versies, en de C-routine die elk daarvan tekent.

---

## 🎨 Vliegpatronen & Trajecten

Elke alienformatie en vogelduik volgt een vast pad, in de ROM opgeslagen als een korte lijst bewegingsvectoren. Deze map telt 130 SVG-bestanden; de 78 patroonanimaties hieronder zijn er één per ROM-gedefinieerd patroon, gegroepeerd naar het subsysteem dat ze gebruikt:

- **Cluster A** (ROM `$1000–$13FF`) — patronen 01–18, geordende formatiegolven in alienwave 1 & 3
- **Cluster B** (ROM `$2C00–$2FFF`) — patronen 19–36, breakout-aliens en moederschip-escorts
- **Vogel-AI-scripts** (ROM `$3F00–$3F7F`) — 16 gedragsscripts
- **Vogelduik- en spawn-posities** (ROM `$3DC0–$3DDF`) — 16 start- en duikcoördinaten

📄 **[`animation-trajectory.md`](animation-trajectory.md)** — elk patroon getoond en toegelicht, met de ROM-clusterindeling, de RAM-datastructuren (`$4000-$4BFF`) en de vectorengine erachter.

📐 **[`animation-trajectory-detailed.md`](animation-trajectory-detailed.md)** — stap-voor-stap coördinatentabellen per patroon: stapnummer, vectorindex, dX, dY, cumulatief X/Y.

---

## 🔗 Knowledge Graph Koppelingen

Elk C-bronbestand in dit subsysteem heeft een geannoteerde tegenhanger in `../../c-annotated/nl/`:

* [`phoenix_tables.c`](../../phoenix_tables.c) → [`phoenix-tables.md`](../../c-annotated/nl/phoenix-tables.md)
* [`alien_logic.c`](../../alien_logic.c) → [`alien-logic.md`](../../c-annotated/nl/alien-logic.md)
* [`bird_logic.c`](../../bird_logic.c) → [`bird-logic.md`](../../c-annotated/nl/bird-logic.md)
* [`bird_wave_behavior.c`](../../bird_wave_behavior.c) → [`bird-wave-behavior.md`](../../c-annotated/nl/bird-wave-behavior.md)
* [`attract_mode.c`](../../attract_mode.c) → [`attract-mode.md`](../../c-annotated/nl/attract-mode.md)
