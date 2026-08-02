# C/ASM-mapping en verificatiestatus

🇳🇱 Nederlands · 🇬🇧 [English](README.md)

Vier bestanden die vanuit verschillende hoeken één vraag beantwoorden: **welke
C-functie vervangt welk stuk van de originele ROM, en hoe zeker weten we dat?**

De C-port is met de hand vertaald uit Z80-assembly. Daarbij moet je twee dingen
bijhouden — de koppeling zelf (dit ROM-adres werd die C-functie), en het bewijs
dat de vertaling zich ook werkelijk hetzelfde gedraagt. De eerste twee bestanden
hieronder zijn de kaart, de andere twee zijn het bewijs.

## Wat hier staat

| Bestand | Beantwoordt | Herkomst |
| --- | --- | --- |
| [`c_functions_by_address.md`](c_functions_by_address.md) | Als je de ROM vanaf `$0000` doorloopt, wat staat er op elk adres — een C-functie, een geanalyseerd gat, of opvulling? | Gegenereerd |
| [`c_functions_per_file.md`](c_functions_per_file.md) | Dezelfde koppeling, gesorteerd per C-bronbestand: welke ASM-bereiken dekt dit bestand? | Gegenereerd |
| [`jphoenix_crosscheck.md`](jphoenix_crosscheck.md) | Bij de functies waar "leeft deze vertaling, en klopt hij?" niet vanzelf sprak: wat concludeerde de audit? | Met de hand geschreven |
| [`lockstep_verified.json`](lockstep_verified.json) | Welke functies zijn byte-exact geverifieerd tegen de originele ROM, en met welke replay-scripts? | Gegenereerd |

### Begin bij de adrestabel

[`c_functions_by_address.md`](c_functions_by_address.md) is het bestand om eerst
te openen. Het is de volledige 16 KB ROM-ruimte in één tabel, en de
**Status**-kolom is waar de twee helften samenkomen: een rij met *"Geverifieerd:
byte-exacte scripted lockstep + PC-dekking"* heeft bewijs achter zich, een rij
met een lege Status is op die manier nog niet onderzocht.

Lees de notitie bovenaan dat bestand goed. Er staat dat de ROM 100% gedekt is,
en dat betekent dat elke byte een naam of een expliciete gatmarkering heeft —
**niet** dat elke vertaling bevestigd correct is. Dat zijn twee verschillende
beweringen, en de Status-kolom is wat ze scheidt.

### Waar het bewijs vandaan komt

`lockstep_verified.json` wordt gemaakt door
[`tools/lockstep/aggregate.py`](../../tools/lockstep/aggregate.py), dat de
uitkomsten verzamelt van dezelfde inputscripts door zowel de Java-emulator (de
echte ROM uit 1980) als de C-port, met een byte-voor-byte RAM-vergelijking. Het
criterium staat in het bestand zelf: een schone run betekent dat de spelstaat
(`$4340-$4BE5`, exclusief gedocumenteerde ruis op `438A-438D`) de hele run exact
overeenkwam.

**Huidige inhoud: gegenereerd op 2026-07-12, 176 functies geverifieerd, 38
gedeeltelijk, over 57 schone scripts.** De repository telt inmiddels 59
inputscripts, dus een verse aggregatie zou iets meer dekken. Dat is een
momentopname, geen fout — maar het is wél de reden dat de datum ertoe doet als
je deze cijfers citeert.

`jphoenix_crosscheck.md` is de menselijke kant van datzelfde werk: de 33
functies waar statische analyse en coverage elkaar tegenspraken, stuk voor stuk
uitgezocht en ondergebracht als dood duplicaat, geïnlinede hulproutine,
harnas-artefact of echt gat.

## Hetzelfde als plaatje

De mapping is een tabel; soms is de vorm makkelijker te lezen.
[`rom_bank_callgraph`](../graphs/rom_bank_callgraph.md) sorteert dezelfde
functies op dezelfde `[ASM: nnnn-nnnn]`-tags, maar dan als graaf — zo zie je in
één oogopslag welke C-modules uit welk deel van de originele ROM stammen, en
waar de functies van een bank over meerdere bestanden verspreid zijn geraakt.
Zie [`../graphs/README.nl.md`](../graphs/README.nl.md) voor de rest van de set.

## Opnieuw genereren

De twee tabellen komen uit één script, te draaien vanuit `c-phoenix/`:

```bash
python3 tools/generate_mappings.py     # of: make docs
```

Het leest de `[ASM: nnnn-nnnn]`-tags in het doc-commentaar van de C-bronnen,
koppelt die aan de ROM-disassembly, en verwerkt de verificatiestatus uit
`lockstep_verified.json` — daarom overleeft de Status-kolom een regeneratie in
plaats van overschreven te worden.

De JSON wordt apart ververst, na een lockstep-run:

```bash
python3 tools/lockstep/aggregate.py
```

Zie [`tools/lockstep/README.nl.md`](../../tools/lockstep/README.nl.md) voor de
volledige procedure.

`jphoenix_crosscheck.md` wordt niet gegenereerd. Het is een auditconclusie en
wordt met de hand bijgewerkt wanneer de audit opnieuw wordt gedaan.

## Achterhaald materiaal

`uncovered_functions.md` stond hier eerder. Het was de ruwe uitvoer van een
coverage-run die 63 niet-bereikte functies leek te tonen; de vervolg-audit heeft
vrijwel al die bevindingen herroepen. Het staat nu bij de andere momentopnamen
in
[`../verification/2026-07-10/`](../verification/2026-07-10/uncovered_functions.md),
omdat het vastlegt hóe de conclusie tot stand kwam en niet wat de huidige status
is. Gebruik daarvoor de Status-kolom hier en `jphoenix_crosscheck.md`.
