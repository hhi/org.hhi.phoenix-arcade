CC ?= cc
EMCC ?= emcc
BUILD_DIR ?= build
CORE_DIR := ../../c-phoenix
ADAPTER_DIR := adapter
CORE_SOURCES := $(filter-out $(CORE_DIR)/platform_sdl.c,$(wildcard $(CORE_DIR)/*.c))
SOURCES := $(CORE_SOURCES) $(ADAPTER_DIR)/redot_platform.c $(ADAPTER_DIR)/redot_c2_renderer.c
CFLAGS ?= -std=c11 -O2 -fPIC -Wall -Wextra -I$(CORE_DIR) -I$(ADAPTER_DIR)
RENDER_ASSETS := ../../c-phoenix/phoenix_render_assets.h
LDFLAGS ?= -shared
LIBRARY := $(BUILD_DIR)/libphoenix_redot_core.dylib
CORE_STATIC_LIBRARY := $(BUILD_DIR)/libphoenix_redot_core.a
SMOKE_TEST := $(BUILD_DIR)/phoenix_redot_core_smoke
REDOT_CPP_DIR := redot-cpp
REDOT_CPP_LIBRARY := $(REDOT_CPP_DIR)/bin/libredot-cpp.macos.template_debug.arm64.a
EXTENSION_SOURCES := extension/phoenix_core_extension.cpp extension/register_types.cpp
EXTENSION := $(BUILD_DIR)/libphoenix_redot_extension.macos.debug.arm64.dylib
CXX ?= c++
SCONS ?= scons
CXXFLAGS ?= -std=c++17 -O2 -fPIC -Wall -Wextra -DMACOS_ENABLED -DHOT_RELOAD_ENABLED -I$(CORE_DIR) -I$(ADAPTER_DIR) -I$(REDOT_CPP_DIR)/include -I$(REDOT_CPP_DIR)/gen/include -I$(REDOT_CPP_DIR)/gdextension

.PHONY: all clean test extension

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

clean:
	rm -rf $(BUILD_DIR)
