# Phoenix-ROMs voorbereiden

Engelse versie: [README.md](README.md).

Voordat je een spel kunt starten, heb je zelf een Phoenix Amstar-ROM-set
nodig. Zoek een legaal bruikbare set; de repository bevat geen ROM-bestanden.

![ROM-voorbereiding en assemblage](diagrams/rom-provisioning-pipeline.nl.svg)

## 1. Zoek de ROM-set op

Zoek zelf online een legaal bruikbare Phoenix Amstar-ROM-set op. Gebruik alleen
de Phoenix (Amstar)-set; andere Phoenix-revisies gebruiken andere chips en
komen niet door de controle.

## 2. Plaats de chipbestanden

Plaats de losse bestanden van je Phoenix Amstar-set in `roms/local/`. De namen
moeten precies als volgt zijn:

```text
roms/local/
  ic45              ic46              ic47              ic48
  h5-ic49.5a        h6-ic50.6a        h7-ic51.7a        h8-ic52.8a
  b1-ic39.3b        b2-ic40.4b        ic23.3d           ic24.4d
  mmi6301.ic40      mmi6301.ic41
```

`roms/local/` is de standaardlocatie die de scripts gebruiken.

## 3. Bereid de ROM-set voor

Voer vanuit de repository-root (de hoofddirectory) uit:

```sh
make romprepare
```

`make romprepare` controleert ieder chipbestand, combineert ze tot drie bestanden in
`roms/assembled/` en werkt de van die bestanden afgeleide C-bronbestanden bij:

| Bestand | Gebruikt voor |
| --- | --- |
| `program.rom` | Het spelprogramma |
| `graphics.rom` | De spelgraphics |
| `proms.rom` | Het kleurenpalet |

Daaruit worden ook twee C-bestanden voorbereid:

- De samengestelde ROM-bestanden blijven bewaard als reproduceerbare build- en
  byte-niveau-testinvoer. De klassieke C-Phoenix-renderer gebruikt
  gegenereerde gedecodeerde tilepixels en RGB-kleuren, en linkt geen ruwe
  ROM-arrays.
- `c-phoenix/phoenix_tables.c` bevat benoemde speldata-tabellen voor de
  gedeelde gamecore. Daardoor kunnen C-Phoenix en C2-Phoenix de spelregels en
  timing gebruiken zonder tijdens het spelen direct in de programma-ROM te
  zoeken.
- C2-Phoenix genereert zijn hi-res-spriteatlas rechtstreeks uit `graphics.rom`
  en `proms.rom`; deze buildstap leest geen `program.rom`.

De samengestelde bestanden worden daarna door de projecten gebruikt:

![Projecten die de samengestelde ROMs gebruiken](diagrams/rom-assembled-consumers.nl.svg)

Staan je ROM-bestanden in een andere map, geef die dan expliciet op:

```sh
make romprepare ROM_DIR=/pad/naar/phoenix-amstar-chips
```

Het commando stopt als een bestand ontbreekt, de verkeerde grootte heeft
of niet bij de verwachte set hoort. Zo wordt voorkomen dat de projecten per
ongeluk met een andere Phoenix-revisie draaien.

`make rombuild` is beschikbaar wanneer je alleen de drie samengestelde
ROM-bestanden wilt maken en de afgeleide C-bronbestanden niet hoeft te
vernieuwen.

## 3. Start een project

Ga met de samengestelde bestanden terug naar de repository-root en kies een
project in de [hoofdinstructies](../README.nl.md#kies-je-startpunt). De
Java-emulator leest de samengestelde bestanden direct. De C-projecten
gebruiken dezelfde gecontroleerde ROM-set bij het bouwen van hun game-assets.

## Meer informatie

[`phoenix-amstar/rom-set.json`](phoenix-amstar/rom-set.json) is het manifest
dat de controlecommando's gebruiken. Het bevat de verwachte chips,
bestandsgroottes en controlesommen. Normaal hoef je het niet aan te passen.

De precieze koppeling tussen fysieke chips en de samengestelde bestanden:

| Samengesteld bestand | Chipbestanden |
| --- | --- |
| `program.rom` | `ic45`, `ic46`, `ic47`, `ic48`, `h5-ic49.5a`, `h6-ic50.6a`, `h7-ic51.7a`, `h8-ic52.8a` |
| `graphics.rom` | `b1-ic39.3b`, `b2-ic40.4b`, `ic23.3d`, `ic24.4d` |
| `proms.rom` | `mmi6301.ic40`, `mmi6301.ic41` |
