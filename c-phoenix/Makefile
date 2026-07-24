CC = gcc
PYTHON ?= python3
CFLAGS = -Wall -Wextra -g -O0 $(shell pkg-config --cflags sdl2 || sdl2-config --cflags)
LDFLAGS = $(shell pkg-config --libs sdl2 || sdl2-config --libs)

# If on macOS, we might need some specific threading flags or frameworks
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    LDFLAGS += -framework OpenGL
    C2_LINKER_GC = -Wl,-dead_strip
else
    C2_LINKER_GC = -Wl,--gc-sections
endif

SRCS = $(wildcard *.c)
OBJS = $(SRCS:.c=.o)
TARGET = c-phoenix
C2_ROOT ?= ../c2-phoenix
C2_VARIANT ?=
C2_BUILD_DIR ?= $(C2_ROOT)/build/native$(if $(C2_VARIANT),/$(C2_VARIANT))
C2_TARGET ?= $(C2_BUILD_DIR)/c2-phoenix
C2_GAME_OBJS = $(patsubst %.c,$(C2_BUILD_DIR)/%.o,$(SRCS))
C2_RENDERER_OBJ = $(C2_BUILD_DIR)/c2_renderer.o
C2_ASSET_HEADER = $(C2_ROOT)/native/c2_hires_sprite_assets.h
C2_VARIANT_CFLAGS = $(if $(C2_VARIANT),-DC2_VARIANT_$(shell echo $(C2_VARIANT) | tr a-z A-Z)=1)
C2_CFLAGS = $(CFLAGS) -DC2_RENDERER $(C2_VARIANT_CFLAGS) -I. -I$(C2_ROOT)/native -ffunction-sections -fdata-sections
C2_LDFLAGS = $(LDFLAGS) $(C2_LINKER_GC)
RUNTIME_TARGET = build/runtime/c-phoenix-runtime
RUNTIME_OBJS = $(SRCS:%.c=build/runtime/%.o)
RUNTIME_SCENARIO ?=
RUNTIME_FRAMES ?= 0
RUNTIME_OUTPUT_DIR ?= $(CURDIR)/context/runtimegraphs/$(RUNTIME_SCENARIO)
REPLAY_SCRIPT ?= context/input-scripts/basic_playthrough.txt
REPLAY_FRAMES ?= 1200
REPLAY_RAM_DUMP ?=
REPLAY_COVERAGE_DUMP ?=
REPLAY_EXTRA_ARGS ?=
HEADLESS_ENV ?= SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
RECORD_NAME ?= c-phoenix-session-$(shell date +%Y%m%d-%H%M%S)
RECORD_SCRIPT ?= /tmp/$(RECORD_NAME).txt
RECORD_EXTRA_ARGS ?=
RECORD_TRACE_FRAMES ?= auto
RECORD_TRACE_TAIL_FRAMES ?= 400
RECORD_TRACE_STOP_AFTER ?= 999999
COMPARE_SCRIPT ?= $(REPLAY_SCRIPT)
COMPARE_FRAMES ?= $(REPLAY_FRAMES)
COMPARE_NAME ?= c-phoenix-compare
COMPARE_REF_DUMP ?= /tmp/ref_$(COMPARE_NAME).bin
COMPARE_PORT_DUMP ?= /tmp/port_$(COMPARE_NAME).bin
COMPARE_REGIONS ?= 4340-47FF,4B40-4BE5
COMPARE_STOP_AFTER ?= 5
COMPARE_EXTRA_ARGS ?=
VISUAL_TRACE_OUTPUT ?= /tmp/$(COMPARE_NAME)-diff.html
VISUAL_TRACE_PLAYER ?= 1
VISUAL_TRACE_KIND ?= auto
VISUAL_TRACE_EXTRA_ARGS ?=

.PHONY: all clean run recordrun recordtracerun replayrun headlessrun comparerun tracerun runtimegraph c2 c2-clean docs help

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

c2: $(C2_TARGET)

$(C2_TARGET): $(C2_GAME_OBJS) $(C2_RENDERER_OBJ)
	@mkdir -p $(dir $@)
	$(CC) $(C2_GAME_OBJS) $(C2_RENDERER_OBJ) -o $@ $(C2_LDFLAGS)

$(C2_BUILD_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(C2_CFLAGS) -c $< -o $@

$(C2_ASSET_HEADER): $(C2_ROOT)/tools/generate_hires_sprite_assets.py rom_data.c
	$(PYTHON) $(C2_ROOT)/tools/generate_hires_sprite_assets.py --rom-data rom_data.c --output $@

$(C2_RENDERER_OBJ): $(C2_ROOT)/native/c2_renderer.c $(C2_ROOT)/native/c2_renderer.h $(C2_ASSET_HEADER)
	@mkdir -p $(dir $@)
	$(CC) $(C2_CFLAGS) -c $< -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

build/runtime/%.o: %.c
	@mkdir -p build/runtime
	$(CC) $(CFLAGS) -finstrument-functions -c $< -o $@

$(RUNTIME_TARGET): $(RUNTIME_OBJS)
	$(CC) $(RUNTIME_OBJS) -o $@ $(LDFLAGS) -Wl,-no_pie

clean:
	rm -f $(OBJS) $(TARGET)

c2-clean:
	rm -rf $(C2_BUILD_DIR)

run: $(TARGET)
	./$(TARGET)

recordrun: $(TARGET)
	./$(TARGET) --record-input=$(RECORD_SCRIPT) $(RECORD_EXTRA_ARGS)

recordtracerun: recordrun
	@frames="$(RECORD_TRACE_FRAMES)"; \
	if [ "$$frames" = "auto" ]; then \
		last_frame=$$(awk '$$1 ~ /^[0-9]+$$/ && $$1 > last { last = $$1 } END { print last + 0 }' "$(RECORD_SCRIPT)"); \
		frames=$$((last_frame + $(RECORD_TRACE_TAIL_FRAMES))); \
		echo "Recorded input ends at frame $$last_frame; replaying $$frames frames."; \
	fi; \
	$(MAKE) tracerun COMPARE_SCRIPT=$(RECORD_SCRIPT) COMPARE_FRAMES=$$frames COMPARE_NAME=$(RECORD_NAME) COMPARE_STOP_AFTER=$(RECORD_TRACE_STOP_AFTER)

replayrun: $(TARGET)
	./$(TARGET) --input-script=$(REPLAY_SCRIPT) $(REPLAY_EXTRA_ARGS)

headlessrun: $(TARGET)
	$(HEADLESS_ENV) ./$(TARGET) --run-frames=$(REPLAY_FRAMES) --input-script=$(REPLAY_SCRIPT) --no-render $(if $(REPLAY_RAM_DUMP),--ram-dump=$(REPLAY_RAM_DUMP),) $(if $(REPLAY_COVERAGE_DUMP),--coverage-dump=$(REPLAY_COVERAGE_DUMP),) $(REPLAY_EXTRA_ARGS)

comparerun: $(TARGET)
	REF_DUMP=$(COMPARE_REF_DUMP) PORT_DUMP=$(COMPARE_PORT_DUMP) tools/lockstep/dump_pair.sh $(COMPARE_SCRIPT) $(COMPARE_FRAMES) $(COMPARE_NAME)
	python3 tools/compare_ram_dumps.py $(COMPARE_REF_DUMP) $(COMPARE_PORT_DUMP) --align-c98 --regions $(COMPARE_REGIONS) --stop-after $(COMPARE_STOP_AFTER) $(COMPARE_EXTRA_ARGS)

tracerun: comparerun
	python3 tools/view_sprite_trace.py $(COMPARE_REF_DUMP) --compare $(COMPARE_PORT_DUMP) --reference-label jphoenix --port-label c-phoenix --kind $(VISUAL_TRACE_KIND) --player $(VISUAL_TRACE_PLAYER) --output=$(VISUAL_TRACE_OUTPUT) $(VISUAL_TRACE_EXTRA_ARGS)
	@echo "Visual tracer: $(VISUAL_TRACE_OUTPUT)"

runtimegraph: $(RUNTIME_TARGET)
	@test -n "$(RUNTIME_SCENARIO)" || { echo "Usage: make runtimegraph RUNTIME_SCENARIO=<input-script-without-.txt> RUNTIME_FRAMES=<frames>"; exit 2; }
	@test "$(RUNTIME_FRAMES)" -gt 0 || { echo "RUNTIME_FRAMES must be a positive frame count"; exit 2; }
	mkdir -p $(RUNTIME_OUTPUT_DIR)
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy $(RUNTIME_TARGET) --run-frames=$(RUNTIME_FRAMES) --input-script=context/input-scripts/$(RUNTIME_SCENARIO).txt --no-render --runtime-call-trace=$(RUNTIME_OUTPUT_DIR)/c_phoenix_calls.bin
	python3 tools/generate_c_runtime_callgraph.py $(RUNTIME_OUTPUT_DIR)/c_phoenix_calls.bin --binary $(RUNTIME_TARGET) --output-dir $(RUNTIME_OUTPUT_DIR)
	python3 tools/generate_c_design_runtime_comparison.py --source-dir . --runtime $(RUNTIME_OUTPUT_DIR)/c_phoenix_runtime_calls.csv --output-dir $(RUNTIME_OUTPUT_DIR)

help:
	@echo "c-phoenix make targets"
	@echo ""
	@echo "  make all              Build $(TARGET) (default)"
	@echo "  make run              Build and run interactively"
	@echo "  make recordrun        Build and run interactively while recording input"
	@echo "  make recordtracerun   Record an interactive session, then compare and trace it"
	@echo "  make replayrun        Build and visibly replay an input script"
	@echo "  make headlessrun      Build and run a headless replay; optionally dump RAM"
	@echo "  make comparerun       Run replay through jphoenix and c-phoenix, then compare RAM"
	@echo "  make tracerun         Run comparerun and generate an interactive visual tracer"
	@echo "  make runtimegraph     Generate an executed C-function call graph"
	@echo "  make c2               Build the native C2 renderer"
	@echo "  make c2-clean         Remove C2 native build artefacts"
	@echo "  make docs             Regenerate mapping and graph documentation"
	@echo "  make clean            Remove object files and $(TARGET)"
	@echo "  make help             Show this help"
	@echo ""
	@echo "requirements"
	@echo "  recordrun/replayrun/headlessrun: c-phoenix, gcc, and SDL2"
	@echo "  comparerun/tracerun/recordtracerun: also JDK 11+ and sibling jphoenix"
	@echo "  runtimegraph: c-phoenix, gcc, SDL2, Python 3, and Graphviz (dot)"
	@echo "  c2: c-phoenix, gcc, and SDL2; it keeps program data for game rules but discards graphics and colour-PROM data from the final binary"
	@echo "  expected jphoenix path: ../jphoenix-emulator-port"
	@echo "  build jphoenix once: (cd ../jphoenix-emulator-port && make)"
	@echo ""
	@echo "runtimegraph example"
	@echo "  make runtimegraph RUNTIME_SCENARIO=bird-investigation RUNTIME_FRAMES=13935"
	@echo "  output: context/runtimegraphs/<scenario>/ (ignored by Git)"
	@echo ""
	@echo "recordrun defaults"
	@echo "  RECORD_SCRIPT=$(RECORD_SCRIPT)"
	@echo "  RECORD_EXTRA_ARGS=$(if $(RECORD_EXTRA_ARGS),$(RECORD_EXTRA_ARGS),(none))"
	@echo "  RECORD_TRACE_FRAMES=$(RECORD_TRACE_FRAMES)"
	@echo "  RECORD_TRACE_TAIL_FRAMES=$(RECORD_TRACE_TAIL_FRAMES)"
	@echo "  RECORD_TRACE_STOP_AFTER=$(RECORD_TRACE_STOP_AFTER)"
	@echo ""
	@echo "replay and headlessrun defaults"
	@echo "  REPLAY_SCRIPT=$(REPLAY_SCRIPT)"
	@echo "  REPLAY_FRAMES=$(REPLAY_FRAMES) (headlessrun only)"
	@echo "  REPLAY_RAM_DUMP=$(if $(REPLAY_RAM_DUMP),$(REPLAY_RAM_DUMP),(disabled))"
	@echo "  REPLAY_COVERAGE_DUMP=$(if $(REPLAY_COVERAGE_DUMP),$(REPLAY_COVERAGE_DUMP),(disabled))"
	@echo "  HEADLESS_ENV=$(HEADLESS_ENV)"
	@echo "  REPLAY_EXTRA_ARGS=$(if $(REPLAY_EXTRA_ARGS),$(REPLAY_EXTRA_ARGS),(none))"
	@echo ""
	@echo "comparerun defaults"
	@echo "  COMPARE_SCRIPT=$(COMPARE_SCRIPT)"
	@echo "  COMPARE_FRAMES=$(COMPARE_FRAMES)"
	@echo "  COMPARE_NAME=$(COMPARE_NAME)"
	@echo "  COMPARE_REF_DUMP=$(COMPARE_REF_DUMP)"
	@echo "  COMPARE_PORT_DUMP=$(COMPARE_PORT_DUMP)"
	@echo "  COMPARE_REGIONS=$(COMPARE_REGIONS)"
	@echo "  COMPARE_STOP_AFTER=$(COMPARE_STOP_AFTER)"
	@echo "  COMPARE_EXTRA_ARGS=$(if $(COMPARE_EXTRA_ARGS),$(COMPARE_EXTRA_ARGS),(none))"
	@echo ""
	@echo "tracerun defaults"
	@echo "  VISUAL_TRACE_OUTPUT=$(VISUAL_TRACE_OUTPUT)"
	@echo "  VISUAL_TRACE_PLAYER=$(VISUAL_TRACE_PLAYER)"
	@echo "  VISUAL_TRACE_KIND=$(VISUAL_TRACE_KIND)"
	@echo "  VISUAL_TRACE_EXTRA_ARGS=$(if $(VISUAL_TRACE_EXTRA_ARGS),$(VISUAL_TRACE_EXTRA_ARGS),(none))"
	@echo ""
	@echo "examples"
	@echo "  make recordrun"
	@echo "  make replayrun"
	@echo "  make replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt"
	@echo "  make headlessrun REPLAY_FRAMES=4000 REPLAY_RAM_DUMP=/tmp/trace.bin"
	@echo "  make headlessrun REPLAY_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt REPLAY_FRAMES=9000"
	@echo "  make comparerun COMPARE_SCRIPT=/tmp/c-phoenix-session.txt COMPARE_FRAMES=9000 COMPARE_NAME=session"
	@echo "  make tracerun COMPARE_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt COMPARE_FRAMES=9000 COMPARE_NAME=last-grown-bird COMPARE_STOP_AFTER=999999"
	@echo "  make recordtracerun RECORD_NAME=bird-investigation"
	@echo "  make recordtracerun RECORD_NAME=bird-investigation RECORD_TRACE_FRAMES=15000"

docs:
	@echo "Generating architecture mappings and graphs..."
	@python3 tools/generate_mappings.py
	@python3 tools/generate_annotated_asm.py
	@python3 tools/generate_callgraph.py
	@python3 tools/generate_file_callgraph.py
	@python3 tools/generate_func_prefix_callgraph.py
	@python3 tools/generate_rom_bank_callgraph.py
	@python3 tools/generate_cross_domain_callgraph.py
	@python3 tools/generate_internal_domain_callgraph.py
	@python3 tools/generate_execution_tree_callgraph.py
	@python3 tools/generate_coverage_callgraph.py
	@python3 tools/generate_stub_hunter_callgraph.py
	@echo "All documentation and graphs successfully generated in context/ !"
