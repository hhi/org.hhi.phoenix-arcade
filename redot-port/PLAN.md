# Phoenix browservariant — historisch ontwerp

> Dit document is het oorspronkelijke ontwerp. Voor de actuele installatie,
> bediening en experimentele status zie [web/README.nl.md](web/README.nl.md).
> De implementatie wijkt op drie punten af: de browserbestanden staan direct
> onder `web/` (niet onder `web/src/`), de bridge levert afzonderlijke
> voor- en achtergrondlagen, en de presentatie gebruikt een WebGL 2-poort van
> de Redot-C2-route. De bestaande Redot-uitgave blijft daarbij ongewijzigd.

## Doel

Maak een zelfstandige browseruitgave van Phoenix die de bestaande
`native/phoenix-core` ongewijzigd als game-mechanische bron gebruikt. De
browser verzorgt alleen invoer, presentatie en audio; alle spelstatus,
timers, botsingen, score en levelovergangen blijven in de C-core draaien.

## Afbakening

- Geen herimplementatie in JavaScript of een nieuw gameframework.
- Geen server, accounts, leaderboard of netwerkfunctionaliteit in de eerste
  versie.
- De versiebeheerde `c-phoenix/phoenix_render_assets.h` blijft de bron voor
  tiles, palet en sprites.
- De huidige native build en Redot-integratie blijven naast de webbuild
  bestaan en moeten na iedere browserwijziging blijven bouwen en testen.

## Architectuur

```text
Keyboard / touch / gamepad
             |
             v
      browser shell (JavaScript)
             |
             v
 Phoenix core compiled to WebAssembly
  input -> step -> RGBA frame + PCM audio
             |                 |
             v                 v
       Canvas (416 x 512)   Web Audio API
```

De bestaande public core-API is de grens tussen shell en mechanics:

- `phoenix_redot_create()` initialiseert een sessie;
- `phoenix_redot_set_input()` ontvangt actieve-lage cabinet-inputbits;
- `phoenix_redot_step()` voert één Phoenix-frame uit;
- `phoenix_redot_frame_rgba()` levert het samengestelde RGBA-frame;
- `phoenix_redot_audio_pcm()` levert de PCM-samples van dat frame.

## Bestandsindeling

Voeg onder `redot-port/web/` toe:

- `index.html` — canvas, start-overlay en toegankelijke bedieningshulp;
- `src/main.js` — WASM-lifecycle, 60 Hz-loop, input en framepresentatie;
- `src/audio.js` — AudioContext, buffering en hervatten na gebruikersactie;
- `src/input.js` — toetsenbord-, touch- en gamepadvertaling naar cabinetbits;
- `src/style.css` — responsieve, pixel-scherpe presentatie;
- `test/` — browser-smoke- en invoertests.

Voeg onder `redot-port/native/` een afzonderlijk Emscripten-buildtarget toe.
Dat target gebruikt dezelfde corebronnen en renderassets als `make test`, maar
vervangt alleen de host/toolchain en exporteert de vijf corefuncties hierboven.
Het bestaande `make test`, de native bibliotheek en het GDExtension-builddoel
worden niet vervangen of hernoemd.

## Bediening

| Phoenixfunctie | Toetsenbord | Touch/gamepad |
| --- | --- | --- |
| Start / 1 speler | `1` of Enter | Startknop / Start |
| Start / 2 spelers | `2` | Tweede startknop |
| Munt | `C` | Coin-knop |
| Links / rechts | pijltjes of A/D | virtuele knoppen / D-pad |
| Vuren | spatie of Z | Fire / knop A |
| Schild | Shift of X | Shield / knop B |

De browser-shell houdt de Phoenix-logica actief-laag: geen ingedrukte knop is
`0xFF`; een ingedrukte knop wist uitsluitend het bijbehorende cabinetbit.

## Fasen

1. **WASM-build**
   - Installeer/controleer Emscripten lokaal.
   - Voeg `make web` of gelijkwaardig toe dat `phoenix_core.js` en
     `phoenix_core.wasm` produceert.
   - Exporteer een kleine C-wrapper die WASM-geheugen voor RGBA en PCM beheert.
   - Acceptatie: de browser kan initialiseren, invoer sturen en een framebuffer
     lezen zonder de native build te wijzigen.

2. **Canvas en game-loop**
   - Presenteer het 416×512 RGBA-frame op één canvas met integer scaling en
     `image-rendering: pixelated`.
   - Gebruik een vaste 60 Hz-simulatiestap; `requestAnimationFrame` presenteert
     het nieuwste frame zonder de game te versnellen op snelle schermen.
   - Acceptatie: titel/demo is zichtbaar en vensterschaal verandert geen
     game-snelheid.

3. **Invoer en startflow**
   - Implementeer keyboard, touch en gamepad volgens de tabel.
   - Toon een overlay die wegens browser-audioregels vraagt om een eerste klik
     of toets voordat audio start.
   - Acceptatie: munt → start → bewegen → vuren → schild werkt met toetsenbord
     in ten minste Chrome en Safari.

4. **Audio**
   - Converteer de door `phoenix_redot_audio_pcm()` geleverde 48 kHz mono PCM
     naar Web Audio buffers of een AudioWorklet-ringbuffer.
   - Houd een kleine buffer aan om tikken bij frame-jitter te voorkomen.
   - Acceptatie: schieten, explosies en muziek zijn hoorbaar zonder gestage
     onderbrekingen in Chrome, Edge en Safari.

5. **Kwaliteitscontrole**
   - Vergelijk vaste core-snapshots en RGBA-checksums tussen native en WASM voor
     een korte deterministische inputreeks.
   - Gebruik browserautomatisering voor laden, audio-startoverlay en
     toetsenbordinteractie.
   - Controleer handmatig Chrome/Edge op Windows en Chrome/Safari op macOS.
   - Voer daarnaast na elke webwijziging `make -C redot-port/native test` uit.
   - Acceptatie: geen consolefouten, correcte aspectratio, bedienbare startflow,
     dezelfde corestate na de gedeelde testreeks én een geslaagde bestaande
     native smoke-test.

## Risico's en besluiten

- Safari vereist een gebruikersactie voor audio. Dat is een UX-voorwaarde,
  geen verschil in gamecode.
- Emscripten gebruikt dezelfde versiebeheerde renderassetheader als de
  Redot-build; er is geen ROM- of assetgeneratiestap.
- De core rendeert al RGBA. Canvas 2D is de eerste implementatie; alleen bij
  gemeten prestatieproblemen wordt WebGL toegevoegd.
- Browsercompatibiliteit wordt bepaald door WASM, Canvas en Web Audio, niet
  door macOS versus Windows.

## Klaar-criterium voor versie 1

Een statische webmap kan lokaal worden geserveerd en toont een speelbare Phoenix
sessie. De browser gebruikt dezelfde C-core als de native build, werkt met
toetsenbord, heeft hoorbare audio na een gebruikersactie, en passeert native- én
browser-smoke-tests in Chrome en Safari.
