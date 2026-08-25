EMCC ?= emcc
BUILD_DIR ?= build
CORE_DIR := ../../c-phoenix
ADAPTER_DIR := .
CORE_SOURCES := $(filter-out $(CORE_DIR)/platform_sdl.c,$(wildcard $(CORE_DIR)/*.c))
SOURCES := $(CORE_SOURCES) $(ADAPTER_DIR)/browser_platform.c
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -I$(CORE_DIR) -I$(ADAPTER_DIR)
MODULE := ../build/phoenix_core.js
PACKAGE_DIR := ../build/release
PACKAGE := ../build/phoenix-browser.zip
RENDER_ASSETS := $(CORE_DIR)/phoenix_render_assets.h

.PHONY: web package clean

web: $(MODULE)

package: $(PACKAGE)

$(PACKAGE): $(MODULE) ../README.md ../README.nl.md ../index.html ../main.js ../c2_hires_renderer.js ../style.css
	rm -rf $(PACKAGE_DIR)
	mkdir -p $(PACKAGE_DIR)/build
	cp ../README.md ../README.nl.md ../index.html ../main.js ../c2_hires_renderer.js ../style.css $(PACKAGE_DIR)/
	cp ../build/phoenix_core.js ../build/phoenix_core.wasm $(PACKAGE_DIR)/build/
	cd $(PACKAGE_DIR) && zip -qr ../$(notdir $(PACKAGE)) .

$(MODULE): $(SOURCES) $(RENDER_ASSETS)
	@mkdir -p ../build $(BUILD_DIR)/emscripten-cache
	EM_CACHE=$(abspath $(BUILD_DIR)/emscripten-cache) $(EMCC) $(CFLAGS) $(SOURCES) -lm --no-entry -O2 \
		-s MODULARIZE=1 -s EXPORT_ES6=1 -s ENVIRONMENT=web \
		-s ALLOW_MEMORY_GROWTH=1 \
		-s EXPORTED_RUNTIME_METHODS='["HEAPU8","HEAP16"]' \
		-s EXPORTED_FUNCTIONS='["_phoenix_web_create","_phoenix_web_set_input","_phoenix_web_step","_phoenix_web_background_layer","_phoenix_web_foreground_layer","_phoenix_web_layer_length","_phoenix_web_audio_buffer","_phoenix_web_audio_sample_count"]' \
		-o $@

clean:
	rm -rf $(BUILD_DIR) ../build
