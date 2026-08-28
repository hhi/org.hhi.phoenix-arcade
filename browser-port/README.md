# Phoenix browser variant

🇬🇧 English · 🇳🇱 [Nederlands](README.nl.md)

This is an experimental static browser edition of Phoenix. Game mechanics are
not reimplemented in JavaScript: the canonical `c-phoenix/` core is compiled
to WebAssembly with Emscripten. JavaScript supplies only keyboard input,
browser audio and presentation. It neither requires nor uses Redot.

## Status

The WebAssembly build, game loop, controls and audio bridge are present. The
WebGL presentation still needs visual sign-off against the Redot edition, so
do not use this variant as a distribution product yet. The existing Redot
edition remains fully separate.

## For players

There is no app or plug-in to install. Someone must first build the files and
place them on a web server; then open the page in a browser.

### Use the GitHub release download

The `phoenix-browser.zip` release asset already contains the built game. To
play it locally:

1. Download and unzip `phoenix-browser.zip`.
2. In a terminal, change to the unzipped directory and start a local server:

   ```sh
   python3 -m http.server 8080
   ```

3. Open <http://127.0.0.1:8080> in a current browser and click **Click to
   start**.

Do not open `index.html` directly with a `file://` URL: browsers load the
JavaScript module and WebAssembly reliably only through HTTP(S). You do not
need Redot, Emscripten, ROM files or a native Phoenix installation to play
the release download.

## For developers: install, build and run

1. Install [Emscripten using the official SDK](https://emscripten.org/docs/getting_started/downloads.html).
   The standard macOS/Linux installation is:

   ```sh
   git clone https://github.com/emscripten-core/emsdk.git
   cd emsdk
   ./emsdk install latest
   ./emsdk activate latest
   source ./emsdk_env.sh
   ```

   Then verify that `emcc --version` works. Activate `emsdk_env.sh` again
   in every new shell unless you deliberately add the SDK to your shell profile.
2. Build JavaScript and WebAssembly from the repository root:

   ```sh
   make web
   ```

   This writes `phoenix_core.js` and `phoenix_core.wasm` to
   `browser-port/build/`. Those generated files do not belong in Git.

   To produce the ZIP attached to a GitHub release instead, run:

   ```sh
   make web-package
   ```

   It writes `browser-port/build/phoenix-browser.zip`. The archive is a
   complete static site: unzip it and serve its contents over HTTP(S).
3. Serve the web directory over HTTP:

   ```sh
   python3 -m http.server 8080 --directory browser-port
   ```

   Then open <http://127.0.0.1:8080>. Do not open `index.html` with a
   `file://` URL: ES modules and WebAssembly load reliably over HTTP(S).

After changing the C core or browser shell, repeat step 3 and refresh without
using a cached page.

The browser build uses the versioned
`c-phoenix/phoenix_render_assets.h` header. It has no `romprepare` step
and does not require ROM files. ROM preparation applies only to the JPhoenix
emulator route.

## Controls

| Function | Key |
| --- | --- |
| Insert coin | C |
| Start one player | 1 or Enter |
| Start two players | 2 |
| Move | Left/Right arrows or A/D |
| Fire | Space or Z |
| Shield | Down arrow, Shift or X |

Click **Click to start** first to allow browser audio. This is browser security
behaviour, not a Phoenix-mechanics difference.

## Compatibility

The edition requires a current browser with WebAssembly, ES modules, Web Audio
and WebGL 2. Windows, macOS and Linux do not matter to a player; the browser is
the runtime. Test each browser, though: audio-autoplay and graphics drivers can
differ between Safari, Chrome, Edge and Firefox.

## Verification

Run the canonical-core and Redot-adapter smoke tests alongside the web build:

```sh
make c-test
make -C redot-port/native test
```

The browser directory is a static artifact directory. Publishing to a real
HTTPS server comes only after visual renderer validation.

## GitHub releases

Each published browser-capable release should include
`phoenix-browser.zip` as a release asset. It lets players or site hosts use
the web edition without installing Emscripten or building from source. GitHub
Actions builds and attaches the package automatically when a GitHub release is
published. Developers can still reproduce the asset with `make web-package`.
