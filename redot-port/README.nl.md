# Phoenix Redot-poort — vertical slice

🇳🇱 Nederlands · 🇬🇧 [English](README.md)

Dit is een zelfstandig Redot-project met een native Phoenix-core. De
Redot-scene rendert een logisch viewport van 416×512: de C-core levert twee
ruwe voorgrond-/achtergrondlagen van 208×256, waarna een Redot-GPU-shader de
Scale2x-beslisregel, beperkte kleurvermenging tussen buren en
coördinaatstabiele korrel toepast. Het project toont dat standaard op
1664×2048. Redot interpoleert ook de vorige en huidige videolagen op de
verversingssnelheid van het scherm, terwijl de spelsimulatie op de originele
60 Hz blijft draaien. Er is geen tijdelijk schip, vijandformatie of
synthetische HUD.

## Spelen

1. Bouw de extensie: `make -C redot-port/native extension`.
2. Open `redot-port/project.godot` in Redot en druk op **F6**, of start het
   project. Druk op Enter om de authentieke attract-demo te openen. Druk op C
   om een credit in te werpen en daarna op 1 of Enter voor één speler, of op
   2 voor twee spelers. Gebruik
   Links/Rechts (of A/D) en Spatie (of Z) pas nadat het spel is gestart.
   Gebruik Omlaag, S of K voor het Phoenix-schild. Druk op R om terug te gaan
   naar het beginscherm. Dat beginscherm bevriest de Phoenix-core; de eerste
   Enter start de attract-sequentie bij het eerste frame. Een spel starten met
   een credit springt niet vooruit naar een actieve golf.

De Redot- en browserbuild gebruiken de versiebeheerde header
`c-phoenix/phoenix_render_assets.h`. Zij lezen niet uit
`roms/assembled` en voeren geen `romprepare` uit; die
voorbereidingsroute hoort alleen bij de JPhoenix-emulator.

## Redot installeren (alleen de native Redot-uitgave)

Dit onderdeel geldt alleen voor de native editoruitgave. De zelfstandige
browseruitgave gebruikt Redot niet en heeft het ook niet nodig.

1. Download de standaardeditor **Redot 26.2** voor je platform via de
   [officiële Redot-26.2-release](https://github.com/Redot-Engine/redot-engine/releases/tag/redot-26.2-stable).
   De C++-bindings van deze poort passen bij Redot 26.2; vervang die versie dus
   niet door een andere editorversie.
2. Pak de editor uit of installeer hem volgens de gebruikelijke procedure van
   je platform en start het Redot-programma eenmaal.
3. Bouw de extensie met `make -C redot-port/native extension`, open
   `redot-port/project.godot` in de editor en start het project.

De zelfstandige browseruitgave staat beschreven in
[`../browser-port/README.nl.md`](../browser-port/README.nl.md).

## Native core

`native/adapter/` bevat de Redot-eigen platformadapter. De build koppelt
die aan de canonieke `../c-phoenix/`-spelbronnen, met alleen het SDL-
desktopplatform uitgesloten. Hij bevat geen ROM-data.

Bouw en test deze core zonder enig ander deelproject aan te raken:

```sh
make -C redot-port/native
make -C redot-port/native test
make -C redot-port/native extension
```

Voor de extensiebouw is SCons nodig. Op deze machine is het commando
`SCONS=/tmp/phoenix-redot-scons/bin/scons make -C redot-port/native extension`;
met een gewone SCons-installatie volstaat het kale commando hierboven.

Op macOS/Apple Silicon schrijft dit
`native/build/libphoenix_redot_extension.macos.debug.arm64.dylib`. De
geëxporteerde ABI staat in `native/adapter/redot_core.h`: creëer de core,
lever actieve-lage cabinetinvoer aan, ga precies één frame vooruit en vraag
video, status en audio op.

De GDExtension registreert `PhoenixCore`, die `PhoenixSlice.gd` op elke
60Hz-tik maakt en aanroept. Score, levens en alle andere Phoenix-schermtekst
worden door de tegelrenderer van de lokale C-core gegenereerd.

## Grens tussen rendering en audio

De Redot-scene ontvangt twee ongeschaalde videolagen van 208×256 via een smalle
GDExtension-methode. De lagen worden gemaakt uit de originele tegel-RAM-vlakken
en echt gedecodeerde Phoenix-graphics-/paletdata. De Redot-shader voegt ze
samen en schaalt ze op:

```text
Redot Node2D -> GDExtension-brug -> C-Phoenix-framestap -> tegel-RAM
    -> Phoenix-tegelrasteraar -> achtergrond + voorgrondtextures
    -> GPU C2 Scale2x/kleurpass -> uiteindelijke vensterschaal
```

Dezelfde brug levert de 48kHz-mono-PCM-frames van de originele soundcore aan
Redots `AudioStreamGenerator`.

De GDExtension-wrapper staat in `native/extension/`, naast een vendored kopie
van de bijpassende Redot 26.2-C++-bindings in `native/redot-cpp/`.

## Een macOS-programma exporteren

De meegeleverde `export_presets.cfg` richt zich op macOS op Apple Silicon. Om
een zelfstandige applicatie te maken, bouw je de native extensie zoals hierboven
beschreven. Een ROM-voorbereidingsstap is niet nodig. Installeer eenmalig de
bijpassende Redot 26.2-exporttemplates via
**Editor → Manage Export Templates**; Redot bundelt deze niet met de editor.
Kies in **Project → Export** de bestaande **macOS**-preset en kies **Export
Project**, met bijvoorbeeld `dist/Phoenix.app` als uitvoer.

Na het eenmalig aanmaken van die preset is het equivalente commando:

```sh
redot --headless --path redot-port --export-release "macOS" dist/Phoenix.app
```

De `.app`-bundle is het uitvoerbare distributieproduct; houd de interne
mapstructuur intact bij kopiëren of verspreiden. De export gebruikt de
extensiebibliotheek onder `native/build/`; bouw die bibliotheek daarom opnieuw
voor een release-export wanneer de native code is gewijzigd. De map `dist/` is
lokale uitvoer en wordt door Git genegeerd.

## Platformstatus en bewuste grenzen

De C-gamecore zelf is gewone C en niet intrinsiek macOS-gebonden. Deze poort
levert nu echter alleen een macOS/Apple-Silicon-GDExtension: `phoenix_redot.gdextension`
en de native Makefile bevatten alleen het `macos.*.arm64`-bibliotheekdoel. Hij
draait daarom nu op dat platform. Linux en Windows vereisen aparte
extensiebouws en bijpassende `.gdextension`-vermeldingen (`.so` en `.dll`);
die zijn nog niet beschikbaar. Het bestaande macOS-binary cross-compileren is
geen oplossing.

### Linux- of Windows-ondersteuning toevoegen

Wijzig hiervoor **niet** `native/adapter/`. Het benodigde werk blijft
beperkt tot de GDExtension-buildgrens:

1. Bouw de vendored `native/redot-cpp/`-bindings op het doel-OS met dezelfde
   Redot-versie/API als het project, voor dat platform en die architectuur
   (bijvoorbeeld `platform=linux arch=x86_64` of `platform=windows
   arch=x86_64`).
2. Compileer de bestaande extensiebronnen in `native/extension/` samen met de
   ongewijzigde C-core tot een native gedeelde bibliotheek. Linux heeft een
   `.so` nodig; Windows een `.dll`. Vervang de macOS-only-linkervlaggen in de
   Makefile door de shared-library-vlaggen van het doelplatform.
3. Voeg de geproduceerde bibliotheekpaden toe aan
   `native/extension/phoenix_redot.gdextension`, naast de bestaande
   macOS-vermeldingen. Bijvoorbeeld:

   ```ini
   linux.debug.x86_64 = "res://native/build/libphoenix_redot_extension.linux.debug.x86_64.so"
   windows.debug.x86_64 = "res://native/build/phoenix_redot_extension.windows.debug.x86_64.dll"
   ```

   Releasevermeldingen moeten naar de bijbehorende releasebuilds wijzen.
4. Voer `make -C redot-port/native test` uit op dat OS, open daarna het project
   in Redot en exporteer met de exportpreset van dat OS.

De Phoenix-C-bronnen, gedeelde versiebeheerde renderassetheader, besturing, C2-shader en
audiobrug blijven op alle platformen hetzelfde.

De poort bevat of commit geen originele ROMs/PROMs. De bestaande Phoenix-
soundcore produceert 48kHz-mono-PCM, die de Redot-front-end via een
`AudioStreamGenerator` in de wachtrij zet.
