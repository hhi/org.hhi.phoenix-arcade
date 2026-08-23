CC ?= cc
EMCC ?= emcc
BUILD_DIR ?= build
CORE_DIR := phoenix-core
CORE_SOURCES := $(filter-out $(CORE_DIR)/redot_platform.c,$(wildcard $(CORE_DIR)/*.c))
SOURCES := $(CORE_SOURCES) $(CORE_DIR)/redot_platform.c
CFLAGS ?= -std=c11 -O2 -fPIC -Wall -Wextra -I$(CORE_DIR)
RENDER_ASSETS := ../../c-phoenix/phoenix_render_assets.h
LDFLAGS ?= -shared
LIBRARY := $(BUILD_DIR)/libphoenix_redot_core.dylib
CORE_STATIC_LIBRARY := $(BUILD_DIR)/libphoenix_redot_core.a
SMOKE_TEST := $(BUILD_DIR)/phoenix_redot_core_smoke
WEB_DIR := ../web/build
WEB_MODULE := $(WEB_DIR)/phoenix_core.js
WEB_SOURCES := $(SOURCES)
REDOT_CPP_DIR := redot-cpp
REDOT_CPP_LIBRARY := $(REDOT_CPP_DIR)/bin/libredot-cpp.macos.template_debug.arm64.a
EXTENSION_SOURCES := extension/phoenix_core_extension.cpp extension/register_types.cpp
EXTENSION := $(BUILD_DIR)/libphoenix_redot_extension.macos.debug.arm64.dylib
CXX ?= c++
SCONS ?= scons
CXXFLAGS ?= -std=c++17 -O2 -fPIC -Wall -Wextra -DMACOS_ENABLED -DHOT_RELOAD_ENABLED -I$(CORE_DIR) -I$(REDOT_CPP_DIR)/include -I$(REDOT_CPP_DIR)/gen/include -I$(REDOT_CPP_DIR)/gdextension

.PHONY: all clean test extension web

all: $(LIBRARY)

$(LIBRARY): $(SOURCES) $(RENDER_ASSETS)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(SOURCES) $(LDFLAGS) -lm -o $@

$(CORE_STATIC_LIBRARY): $(SOURCES) $(RENDER_ASSETS)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $(SOURCES)
	ar rcs $@ *.o
	@rm -f *.o

$(REDOT_CPP_LIBRARY): extension_api.json redot-cpp-profile.json redot-cpp/SConstruct
	cd $(REDOT_CPP_DIR) && $(SCONS) platform=macos arch=arm64 custom_api_file=../extension_api.json build_profile=../redot-cpp-profile.json

$(EXTENSION): $(EXTENSION_SOURCES) $(CORE_STATIC_LIBRARY) $(REDOT_CPP_LIBRARY)
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(EXTENSION_SOURCES) $(CORE_STATIC_LIBRARY) -Wl,-force_load,$(REDOT_CPP_LIBRARY) -dynamiclib -Wl,-undefined,dynamic_lookup -lm -o $@

extension: $(EXTENSION)

$(SMOKE_TEST): tests/core_smoke.c $(SOURCES) $(RENDER_ASSETS)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) $(SOURCES) tests/core_smoke.c -lm -o $@

test: $(SMOKE_TEST)
	./$(SMOKE_TEST)

web: $(WEB_MODULE)

$(WEB_MODULE): $(WEB_SOURCES) $(RENDER_ASSETS)
	@mkdir -p $(WEB_DIR) $(BUILD_DIR)/emscripten-cache
	EM_CACHE=$(abspath $(BUILD_DIR)/emscripten-cache) $(EMCC) $(CFLAGS) $(WEB_SOURCES) -lm --no-entry -O2 \
		-s MODULARIZE=1 -s EXPORT_ES6=1 -s ENVIRONMENT=web \
		-s ALLOW_MEMORY_GROWTH=1 \
		-s EXPORTED_RUNTIME_METHODS='["HEAPU8","HEAP16"]' \
		-s EXPORTED_FUNCTIONS='["_phoenix_web_create","_phoenix_web_set_input","_phoenix_web_step","_phoenix_web_frame_buffer","_phoenix_web_frame_buffer_length","_phoenix_web_background_layer","_phoenix_web_foreground_layer","_phoenix_web_layer_length","_phoenix_web_audio_buffer","_phoenix_web_audio_sample_count"]' \
		-o $@

clean:
	rm -rf $(BUILD_DIR)
