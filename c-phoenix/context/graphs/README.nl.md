# C-Phoenix Grafieken

🇳🇱 Nederlands · 🇬🇧 [English](README.md)

Negen callgraphs van de C-port, elk met antwoord op één vraag over hoe de code
samenhangt. Ze worden allemaal uit de broncode gegenereerd door een script in
[`c-phoenix/tools/`](../../tools/README.nl.md); niets hier is met de hand getekend. Wijkt
een graaf af van de code, dan is de code veranderd en de graaf niet.

Elke graaf bestaat uit drie bestanden: de Graphviz-bron (`.dot`), de gerenderde
afbeelding (`.svg`) en een korte toelichting (`.md`).

## Welke graaf heb ik nodig?

Begin bij de vraag die je werkelijk hebt:

| Wil je weten… | Open | Waarom die |
| --- | --- | --- |
| Waar begin ik met lezen in deze port? | [file_callgraph](file_callgraph.md) | Eén knoop per bronbestand, gegroepeerd in clusters. De enige graaf die klein genoeg is om in één blik te overzien. |
| Wie roept deze functie aan, en wat roept zij aan? | [callgraph](callgraph.md) | Elke functie en elke pijl. Groot — open de SVG en zoom in, lees hem niet in zijn geheel. |
| Steekt deze wijziging een architectuurgrens over? | [cross_domain_callgraph](cross_domain_callgraph.md) | Toont alleen pijlen die hun eigen domein verlaten, dus een onverwachte springt eruit. |
| Is dit domein een samenhangend geheel of een rommelbak? | [internal_domain_callgraph](internal_domain_callgraph.md) | Het spiegelbeeld: alleen de pijlen *binnen* één domein. |
| Welke onderdelen van het spel praten met elkaar? | [func_prefix_callgraph](func_prefix_callgraph.md) | Groepeert functies op naamfamilie (`bird_*`, `mothership_*`, …) in plaats van op bestand. |
| Wat draait er van boven naar beneden? | [execution_tree_callgraph](execution_tree_callgraph.md) | De aanroephiërarchie als boom, met de instappunten als wortel. |
| Uit welke originele ROM-bank komt deze code? | [rom_bank_callgraph](rom_bank_callgraph.md) | Sorteert functies op het `[ASM: nnnn-nnnn]`-adres in hun doc-commentaar. Handig bij vergelijken met `Phoenix.asm`. |
| Leunen we nog op compatibiliteitsstubs? | [stub_hunter_callgraph](stub_hunter_callgraph.md) | Alleen de aanroepers die nog een ROM-compat-stub bereiken. |
| Welke functies hebben de testscripts werkelijk uitgevoerd? | [coverage_callgraph](coverage_callgraph.md) | De enige graaf die uit een *run* komt in plaats van uit de brontekst. |

**De eerste acht zijn ontwerptijd**: ze lezen de `.c`-bestanden en beschrijven
wat de broncode zegt, ongeacht of die code ooit draait. **`coverage_callgraph`
is anders** — die heeft `.gcov`-uitvoer van een geïnstrumenteerde build nodig en
toont dus wat een bepaalde reeks replays bereikte.

## Begin hier: hoe de C-port is opgebouwd

`file_callgraph` is het leesbare overzicht — welk bronbestand van welk ander
afhangt, gegroepeerd in de architectuurclusters van de port:

![Welke C-bronbestanden van elkaar afhangen, gegroepeerd in clusters: spelstatus, entiteitslogica, botsingsmechanica, rendering, audio, hulpfuncties en kernarchitectuur](file_callgraph.svg)

Die afbeelding is de snelste manier om je te oriënteren: entiteitslogica in het
midden, botsingen en scoring erboven, platform en audio rechtsonder, en
`utilities.c` waar bijna alles aan trekt.

Alleen `file_callgraph` staat hier als afbeelding, en dat is bewust. De grafen
op functieniveau zijn erg groot — `func_prefix_callgraph` is ongeveer
2300 × 8100 punten en `execution_tree_callgraph` ruim 10.000 punten breed — dus
een miniatuur zou een onleesbare veeg zijn. Open die SVG's rechtstreeks en zoom
in.

`stub_hunter_callgraph.svg` rendert op dit moment leeg. Dat is het resultaat,
geen storing: geen enkele actieve C-aanroeper bereikt nog een
ROM-compatibiliteitsstub.

## De generatoren

| Graaf | Script | Leest |
| --- | --- | --- |
| [callgraph](callgraph.md) | [`generate_callgraph.py`](../../tools/generate_callgraph.py) | de `.c`-bronnen |
| [file_callgraph](file_callgraph.md) | [`generate_file_callgraph.py`](../../tools/generate_file_callgraph.py) | de `.c`-bronnen |
| [func_prefix_callgraph](func_prefix_callgraph.md) | [`generate_func_prefix_callgraph.py`](../../tools/generate_func_prefix_callgraph.py) | de `.c`-bronnen |
| [cross_domain_callgraph](cross_domain_callgraph.md) | [`generate_cross_domain_callgraph.py`](../../tools/generate_cross_domain_callgraph.py) | de `.c`-bronnen |
| [internal_domain_callgraph](internal_domain_callgraph.md) | [`generate_internal_domain_callgraph.py`](../../tools/generate_internal_domain_callgraph.py) | de `.c`-bronnen |
| [execution_tree_callgraph](execution_tree_callgraph.md) | [`generate_execution_tree_callgraph.py`](../../tools/generate_execution_tree_callgraph.py) | de `.c`-bronnen |
| [rom_bank_callgraph](rom_bank_callgraph.md) | [`generate_rom_bank_callgraph.py`](../../tools/generate_rom_bank_callgraph.py) | de `.c`-bronnen plus hun `[ASM: …]`-commentaar |
| [stub_hunter_callgraph](stub_hunter_callgraph.md) | [`generate_stub_hunter_callgraph.py`](../../tools/generate_stub_hunter_callgraph.py) | de `.c`-bronnen plus `rom_compat_stubs.c` |
| [coverage_callgraph](coverage_callgraph.md) | [`generate_coverage_callgraph.py`](../../tools/generate_coverage_callgraph.py) | `.gcov`-bestanden uit een coverage-build |

## Hoe de scripts werken

Alle negen volgen dezelfde drie stappen, en geen van hen compileert iets:

1. **De broncode als tekst aftasten.** Elk `.c`-bestand in `c-phoenix/` wordt
   regel voor regel gelezen. Een regel die op een functiedefinitie lijkt
   registreert een functie en het bestand waarin ze staat; daarna telt elke naam
   gevolgd door `(` op een latere regel als aanroep — maar alleen als die naam al
   bekend staat als gedefinieerde functie, zodat `if (`, casts en
   bibliotheekaanroepen buiten beeld blijven.
2. **Indelen in domeinen.** Elk script bevat een hardgecodeerde
   `categories`-tabel die bronbestanden aan clusters toewijst (Core Architecture,
   Game State, Entity Logic, Collision Mechanics, Rendering, Audio, Utilities).
   Die tabel maakt van een platte lijst pijlen een gegroepeerde afbeelding, en is
   ook de reden dat een nieuw bronbestand in elke generator een regel aanpassing
   vraagt om ergens te landen.
3. **`.dot` schrijven, dan renderen.** Het script schrijft Graphviz-bron en roept
   `dot -Tsvg` aan voor de afbeelding. **Graphviz moet geïnstalleerd zijn**;
   zonder dat wordt het `.dot`-bestand wel geschreven en de `.svg` overgeslagen
   met een melding.

Twee scripts wijken af. `generate_rom_bank_callgraph.py` leest daarnaast de
`[ASM: nnnn-nnnn]`-tag in het doc-commentaar van elke functie en sorteert de
functie op zijn startadres — zo is een moderne C-functie terug te voeren op een
originele ROM-bank. `generate_coverage_callgraph.py` kijkt helemaal niet naar
aanroepstructuur maar leest `.gcov`-bestanden en markeert per functie of die is
uitgevoerd. Er moet dus eerst een coverage-build gedraaid hebben, en het
resultaat weerspiegelt de replays die daarbij zijn gebruikt.

## Wat deze grafen niet zien

Het aftasten is tekstueel, geen compilerdoorloop, en dat heeft gevolgen die je
moet kennen voordat je een graaf als volledig beschouwt:

- **Functiedefinities worden op hun retourtype herkend.** Het patroon dekt
  `void`, `uint8_t`, `uint16_t`, `int` en `bool`. In de huidige broncode herkent
  dat 296 functies en mist het er 29 — die met een ander retourtype (`float`,
  `double`, `const char*`) of met een attribuutmacro zoals `NO_INSTRUMENT`. Een
  gemiste functie is geen knoop, en aanroepen ernaartoe zijn geen pijlen.
- **Commentaar wordt niet weggefilterd.** Een functienaam die in commentaar
  binnen een functielichaam wordt genoemd, telt als aanroep. Er staan ongeveer
  399 commentaarregels in de broncode die op een aanroep lijken, dus een klein
  aantal pijlen kan documentatie zijn in plaats van code.
- **Aanroepen via functiepointers zijn onzichtbaar**, zoals voor elke tekstuele
  scan.

Dit maakt de grafen niet onjuist als overzicht — het maakt ze een kaart, geen
bewijs. Doet een pijl ertoe voor een bewering die je doet, controleer hem dan
tegen de broncode. Voor een aanroeplijst die is *opgenomen* in plaats van
afgeleid, gebruik je de runtime-grafen hieronder.

## Gebruik naast de knowledge base

Elk `.c`-bestand in deze port heeft een geannoteerde tegenhanger in
[`c-annotated/`](../../c-annotated/README.md), en `file_callgraph` werkt daar
meteen als index op: het bestand dat een knoop noemt is de pagina die je zoekt,
en de pijlen vertellen welke pagina's je erbij moet lezen.
`rom_bank_callgraph` gebruikt dezelfde `[ASM: nnnn-nnnn]`-tags waar de
annotaties en [`context/mapping/`](../mapping/README.nl.md) op gebouwd zijn — de
drie beelden (tabel, annotatie en graaf) beschrijven dus één en dezelfde
koppeling.

## Opnieuw genereren

Vanuit `c-phoenix/`, de hele set plus de overige gegenereerde documentatie:

```bash
make docs
```

Of één tegelijk, als je maar één ding hebt gewijzigd:

```bash
python3 tools/generate_file_callgraph.py
python3 tools/generate_rom_bank_callgraph.py
```

`coverage_callgraph` is de uitzondering: die heeft `.gcov`-bestanden nodig, dus
draai eerst de coverage-build.

## Niet hetzelfde als de runtime-grafen

Verwar deze grafen niet met de **runtime**-grafen per scenario in
`context/runtimegraphs/<scenario>/`, gegenereerd met `make runtimegraph`. Die
gebruiken werkelijke aanroepen, opgenomen terwijl een inputscript speelt, en
tonen dus wat er gebeurd is in plaats van wat de broncode toelaat. De
vergelijking daar onderscheidt bovendien ontworpen aanroeppijlen van pijlen die
in die run zijn waargenomen — de eerlijke manier om zowel dode code als
ongedocumenteerde paden te vinden.
