# Phoenix-browservariant

🇳🇱 Nederlands · 🇬🇧 [English](README.md)

Dit is een experimentele, statische browseruitgave van Phoenix. De
spelmechanica draait niet opnieuw in JavaScript: de canonieke C-core onder
`c-phoenix/` wordt met Emscripten naar WebAssembly gecompileerd. JavaScript
levert alleen toetsenbord-invoer, browseraudio en presentatie; Redot is niet
nodig.

## Status

De WebAssembly-build, game-loop, besturing en audio-brug zijn aanwezig. De
WebGL-presentatie moet nog visueel worden vrijgegeven tegen de Redot-uitgave;
gebruik deze variant daarom nog niet als distributieproduct. De bestaande
Redot-uitgave blijft volledig afzonderlijk werken.

## Voor spelers

Je installeert geen app of plug-in. Iemand moet eerst de bestanden bouwen en
op een webserver plaatsen; daarna open je de webpagina in de browser.

### De GitHub-release gebruiken

Het releasebestand `phoenix-browser.zip` bevat het gebouwde spel al. Zo speel
je het lokaal:

1. Download en pak `phoenix-browser.zip` uit.
2. Ga in een terminal naar de uitgepakte map en start een lokale server:

   ```sh
   python3 -m http.server 8080
   ```

3. Open <http://127.0.0.1:8080> in een actuele browser en klik op
   **Click to start**.

Open `index.html` niet rechtstreeks met een `file://`-URL: browsers laden de
JavaScriptmodule en WebAssembly betrouwbaar alleen via HTTP(S). Je hebt voor
de releasedownload geen Redot, Emscripten, ROM-bestanden of native Phoenix-
installatie nodig.

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
   `browser-port/build/`. Die gegenereerde bestanden horen niet in Git.

   Maak in plaats daarvan het ZIP-bestand voor een GitHub-release met:

   ```sh
   make web-package
   ```

   Dit schrijft `browser-port/build/phoenix-browser.zip`. Het archief is een
   complete statische site: pak het uit en serveer de inhoud via HTTP(S).
3. Serveer de webmap via HTTP:

   ```sh
   python3 -m http.server 8080 --directory browser-port
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
| Schild | pijl-omlaag, Shift of X |

beveiligingsregel van browsers, geen verschil in Phoenix-mechanics.
Klik eerst op **Click to start** om browseraudio toe te staan. Dit is een
beveiligingsregel van browsers, geen verschil in Phoenix-mechanics.
beveiligingsregel van browsers, geen verschil in Phoenix-mechanics.

## Compatibiliteit

De uitgave vereist een moderne browser met WebAssembly, ES-modules, Web Audio
en WebGL 2. Windows, macOS en Linux maken voor de speler niet uit: de browser
is de runtime. Test wel per browser; vooral audio-autoplay en grafische
drivers kunnen verschillen tussen Safari, Chrome, Edge en Firefox.

## Controle

Voer naast de webbuild altijd de C-core- en Redot-adapter-smoketests uit:

```sh
make c-test
make -C redot-port/native test
```

De browsermap is een statische artefactmap. Publicatie op een echte
HTTPS-webserver is pas aan de orde nadat de renderer visueel is gevalideerd.

## GitHub-releases

Elke gepubliceerde release met browserondersteuning moet
`phoenix-browser.zip` als release-asset bevatten. Daarmee kunnen spelers en
sitebeheerders de webuitgave gebruiken zonder Emscripten te installeren of uit
broncode te bouwen. GitHub Actions bouwt en voegt dit pakket automatisch toe
wanneer een GitHub-release wordt gepubliceerd. Ontwikkelaars kunnen het pakket
altijd reproduceren met `make web-package`.
