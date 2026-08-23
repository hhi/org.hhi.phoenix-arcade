# Phoenix-browservariant

🇳🇱 Nederlands · 🇬🇧 [English](README.md)

Dit is een experimentele, statische browseruitgave van Phoenix. De
spelmechanica draait niet opnieuw in JavaScript: dezelfde C-core als de
Redot-poort wordt met Emscripten naar WebAssembly gecompileerd. JavaScript
levert alleen toetsenbord-invoer, browseraudio en presentatie.

## Status

De WebAssembly-build, game-loop, besturing en audio-brug zijn aanwezig. De
WebGL-presentatie moet nog visueel worden vrijgegeven tegen de Redot-uitgave;
gebruik deze variant daarom nog niet als distributieproduct. De bestaande
Redot-uitgave blijft volledig afzonderlijk werken.

## Voor spelers

Je installeert geen app of plug-in. Iemand moet eerst de bestanden bouwen en
op een webserver plaatsen; daarna open je de webpagina in de browser.

## Voor ontwikkelaars: installeren, bouwen en starten

1. Installeer [Emscripten via de officiële SDK](https://emscripten.org/docs/getting_started/downloads.html).
   De standaardinstallatie op macOS/Linux is:

   ```sh
   git clone https://github.com/emscripten-core/emsdk.git
   cd emsdk
   ./emsdk install latest
   ./emsdk activate latest
   source ./emsdk_env.sh
   ```

   Controleer daarna dat `emcc --version` werkt. Activeer
   `emsdk_env.sh` opnieuw in elke nieuwe shell, tenzij je de SDK bewust in je
   shellprofiel opneemt.
2. Bouw JavaScript en WebAssembly vanuit de repository-root:

   ```sh
   make web
   ```

   Dit schrijft `phoenix_core.js` en `phoenix_core.wasm` naar
   `redot-port/web/build/`. Die gegenereerde bestanden horen niet in Git.
3. Serveer de webmap via HTTP:

   ```sh
   python3 -m http.server 8080 --directory redot-port/web
   ```

   Open vervolgens <http://127.0.0.1:8080>. Open `index.html` niet met een
   `file://`-URL: ES-modules en WebAssembly laden betrouwbaar via HTTP(S).

Na een wijziging in de C-core of browser-shell herhaal je stap 3 en vernieuw je
de pagina zonder cache.

De browserbuild gebruikt de versiebeheerde header
`c-phoenix/phoenix_render_assets.h`. Er is geen `romprepare`-stap en er
zijn geen ROM-bestanden nodig. ROM-voorbereiding geldt alleen voor de
JPhoenix-emulatorroute.

## Bediening

| Functie | Toets |
| --- | --- |
| Munt | C |
| Eén speler starten | 1 of Enter |
| Twee spelers starten | 2 |
| Bewegen | pijl-links/-rechts of A/D |
| Vuren | spatie of Z |
| Schild | Shift of X |

Klik eerst op **Klik om te starten** om browseraudio toe te staan. Dit is een
beveiligingsregel van browsers, geen verschil in Phoenix-mechanics.

## Compatibiliteit

De uitgave vereist een moderne browser met WebAssembly, ES-modules, Web Audio
en WebGL 2. Windows, macOS en Linux maken voor de speler niet uit: de browser
is de runtime. Test wel per browser; vooral audio-autoplay en grafische
drivers kunnen verschillen tussen Safari, Chrome, Edge en Firefox.

## Controle

Voer naast de webbuild altijd de bestaande native core-smoketest uit:

```sh
make -C redot-port/native test
```

De browsermap is een statische artefactmap. Publicatie op een echte
HTTPS-webserver is pas aan de orde nadat de renderer visueel is gevalideerd.
