CC = gcc
PYTHON ?= python3
BUILD_DIR ?= build
OBJ_DIR ?= $(BUILD_DIR)/obj
GENERATED_DIR ?= $(BUILD_DIR)/generated
CFLAGS = -Wall -Wextra -g -O0 -fdata-sections $(shell pkg-config --cflags sdl2 || sdl2-config --cflags)
LDFLAGS = $(shell pkg-config --libs sdl2 || sdl2-config --libs)

# If on macOS, we might need some specific threading flags or frameworks
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    LDFLAGS += -framework OpenGL -Wl,-dead_strip
    C2_LINKER_GC = -Wl,-dead_strip
else
    LDFLAGS += -Wl,--gc-sections
    C2_LINKER_GC = -Wl,--gc-sections
endif

SRCS = $(wildcard *.c)
OBJS = $(patsubst %.c,$(OBJ_DIR)/%.o,$(SRCS))
TARGET = $(BUILD_DIR)/c-phoenix
C2_ROOT ?= ../c2-phoenix
C2_VARIANT ?=
C2_BUILD_DIR ?= $(C2_ROOT)/build/native$(if $(C2_VARIANT),/$(C2_VARIANT))
C2_TARGET ?= $(C2_BUILD_DIR)/c2-phoenix
C2_GAME_OBJS = $(patsubst %.c,$(C2_BUILD_DIR)/%.o,$(SRCS))
C2_RENDERER_OBJ = $(C2_BUILD_DIR)/c2_renderer.o
C2_ASSET_HEADER = $(C2_BUILD_DIR)/generated/c2_hires_sprite_assets.h
CLASSIC_ASSET_HEADER = phoenix_render_assets.h
C2_VARIANT_CFLAGS = $(if $(C2_VARIANT),-DC2_VARIANT_$(shell echo $(C2_VARIANT) | tr a-z A-Z)=1)
C2_CFLAGS = $(CFLAGS) -DC2_RENDERER $(C2_VARIANT_CFLAGS) -I. -I$(C2_ROOT)/native -ffunction-sections -fdata-sections
C2_LDFLAGS = $(LDFLAGS) $(C2_LINKER_GC)
RUNTIME_TARGET = build/runtime/c-phoenix-runtime
RUNTIME_OBJS = $(SRCS:%.c=build/runtime/%.o)
RUNTIME_SCENARIO ?=
RUNTIME_FRAMES ?= 0
RUNTIME_OUTPUT_DIR ?= $(CURDIR)/context/runtimegraphs/$(RUNTIME_SCENARIO)
RUNTIME_EXPLORER_OUTPUT ?= $(CURDIR)/tools/runtime-trace-explorer/index.html
# Shared input scripts are addressed as context/... from every implementation.
# In this directory the shared context lives locally; sibling implementations
# override CONTEXT_ROOT with ../c-phoenix/context.
CONTEXT_ROOT ?= context
resolve_context_path = $(if $(filter context/%,$(1)),$(CONTEXT_ROOT)/$(patsubst context/%,%,$(1)),$(1))
REPLAY_SCRIPT ?= $(CONTEXT_ROOT)/input-scripts/basic_playthrough.txt
REPLAY_FRAMES ?= 1200
REPLAY_RAM_DUMP ?=
REPLAY_COVERAGE_DUMP ?=
REPLAY_EXTRA_ARGS ?=
HEADLESS_ENV ?= SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
DEMO_SCRIPT ?= $(CONTEXT_ROOT)/input-scripts/bird-investigation.txt
DEMO_FRAMES ?= 13935
DEMO_NAME ?= bird-investigation
# DEMO_DUMP is shared with C2-Phoenix and JPhoenix. Keep the older
# DEMO_RAM_DUMP spelling as a compatibility alias for existing commands.
DEMO_RAM_DUMP ?=
DEMO_DUMP ?= $(if $(DEMO_RAM_DUMP),$(DEMO_RAM_DUMP),/tmp/c-phoenix-$(DEMO_NAME).bin)
DEMO_TRACE_OUTPUT ?= /tmp/c-phoenix-$(DEMO_NAME)-tracer.html
DEMO_TRACE_KIND ?= all
DEMO_TRACE_PLAYER ?= all
DEMO_EXTRA_ARGS ?=
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
ASM_VIEW_PORT ?= 8765
TRACER_VIEW_PORT ?= 8766
TRACE_VIEW_OUTPUT ?= $(VISUAL_TRACE_OUTPUT)
TRACE_VIEW_DIR ?= $(dir $(TRACE_VIEW_OUTPUT))

.PHONY: all clean run recordrun recordtracerun replayrun headlessrun demorun demo-tracer-view demo-tracer-view-only comparerun tracerun tracer-view tracer-view-only runtimegraph c2 c2-clean verify-rom-free docs interactive-asm interactive-asm-view interactive-asm-view-only knowledge-graph-visual wave-screenshots bottargets botsearch spritesheets help

all: $(TARGET) verify-rom-free


$(CLASSIC_ASSET_HEADER): tools/generate_classic_render_assets.py ../roms/assembled/graphics.rom ../roms/assembled/proms.rom
	$(PYTHON) tools/generate_classic_render_assets.py --graphics ../roms/assembled/graphics.rom --proms ../roms/assembled/proms.rom --output $@

$(OBJ_DIR)/platform_sdl.o build/runtime/platform_sdl.o: $(CLASSIC_ASSET_HEADER)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

verify-rom-free: $(TARGET)
	@if nm $(TARGET) | grep -Eq '(^|_)prg_mem$$|(^|_)gfx_mem$$|(^|_)palette_prom_[ab]$$'; then \
		echo "raw ROM data leaked into $(TARGET)"; exit 1; \
	fi

c2: $(C2_TARGET)

$(C2_TARGET): $(C2_GAME_OBJS) $(C2_RENDERER_OBJ)
	@mkdir -p $(dir $@)
	$(CC) $(C2_GAME_OBJS) $(C2_RENDERER_OBJ) -o $@ $(C2_LDFLAGS)

$(C2_BUILD_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(C2_CFLAGS) -c $< -o $@

$(C2_ASSET_HEADER): $(C2_ROOT)/tools/generate_hires_sprite_assets.py ../roms/assembled/graphics.rom ../roms/assembled/proms.rom
	@mkdir -p $(dir $@)
	$(PYTHON) $(C2_ROOT)/tools/generate_hires_sprite_assets.py --graphics ../roms/assembled/graphics.rom --proms ../roms/assembled/proms.rom --output $@

$(C2_RENDERER_OBJ): $(C2_ROOT)/native/c2_renderer.c $(C2_ROOT)/native/c2_renderer.h $(C2_ASSET_HEADER)
	@mkdir -p $(dir $@)
	$(CC) $(C2_CFLAGS) -I$(dir $(C2_ASSET_HEADER)) -c $< -o $@

$(OBJ_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

build/runtime/%.o: %.c
	@mkdir -p build/runtime
	$(CC) $(CFLAGS) -finstrument-functions -c $< -o $@

$(RUNTIME_TARGET): $(RUNTIME_OBJS)
	$(CC) $(RUNTIME_OBJS) -o $@ $(LDFLAGS) -Wl,-no_pie

clean:
	rm -rf $(BUILD_DIR)
	rm -f $(SRCS:.c=.o) c-phoenix

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
	./$(TARGET) --input-script=$(call resolve_context_path,$(REPLAY_SCRIPT)) $(REPLAY_EXTRA_ARGS)

headlessrun: $(TARGET)
	$(HEADLESS_ENV) ./$(TARGET) --run-frames=$(REPLAY_FRAMES) --input-script=$(call resolve_context_path,$(REPLAY_SCRIPT)) --no-render $(if $(REPLAY_RAM_DUMP),--ram-dump=$(REPLAY_RAM_DUMP),) $(if $(REPLAY_COVERAGE_DUMP),--coverage-dump=$(REPLAY_COVERAGE_DUMP),) $(REPLAY_EXTRA_ARGS)

# Standalone C-Phoenix object tracer: no JPhoenix dump or comparison needed.
demorun: $(TARGET)
	$(HEADLESS_ENV) ./$(TARGET) --run-frames=$(DEMO_FRAMES) --input-script=$(call resolve_context_path,$(DEMO_SCRIPT)) --no-render --ram-dump=$(DEMO_DUMP) $(DEMO_EXTRA_ARGS)
	$(PYTHON) tools/view_sprite_trace.py $(DEMO_DUMP) --reference-label c-phoenix --kind $(DEMO_TRACE_KIND) --player $(DEMO_TRACE_PLAYER) --title "C-Phoenix $(DEMO_NAME) object tracer" --output=$(DEMO_TRACE_OUTPUT)
	@echo "C-Phoenix object tracer generated: $(DEMO_TRACE_OUTPUT)"

demo-tracer-view: demorun demo-tracer-view-only

demo-tracer-view-only:
	@$(MAKE) tracer-view-only TRACE_VIEW_OUTPUT=$(DEMO_TRACE_OUTPUT) TRACER_VIEW_PORT=$(TRACER_VIEW_PORT)

comparerun: $(TARGET)
	REF_DUMP=$(COMPARE_REF_DUMP) PORT_DUMP=$(COMPARE_PORT_DUMP) tools/lockstep/dump_pair.sh $(COMPARE_SCRIPT) $(COMPARE_FRAMES) $(COMPARE_NAME)
	python3 tools/compare_ram_dumps.py $(COMPARE_REF_DUMP) $(COMPARE_PORT_DUMP) --align-c98 --regions $(COMPARE_REGIONS) --stop-after $(COMPARE_STOP_AFTER) $(COMPARE_EXTRA_ARGS)

tracerun: comparerun
	python3 tools/view_sprite_trace.py $(COMPARE_REF_DUMP) --compare $(COMPARE_PORT_DUMP) --reference-label jphoenix --port-label c-phoenix --kind $(VISUAL_TRACE_KIND) --player $(VISUAL_TRACE_PLAYER) --output=$(VISUAL_TRACE_OUTPUT) $(VISUAL_TRACE_EXTRA_ARGS)
	@echo "Visual tracer: $(VISUAL_TRACE_OUTPUT)"

tracer-view: tracerun tracer-view-only

tracer-view-only:
	@test -f "$(TRACE_VIEW_OUTPUT)" || { echo "Tracer HTML not found: $(TRACE_VIEW_OUTPUT)"; exit 2; }
	@echo "Open http://127.0.0.1:$(TRACER_VIEW_PORT)/$(notdir $(TRACE_VIEW_OUTPUT))"
	@echo "Press Ctrl-C to stop the local tracer viewer."
	@$(PYTHON) -m http.server $(TRACER_VIEW_PORT) --bind 127.0.0.1 --directory "$(TRACE_VIEW_DIR)"

runtimegraph: $(RUNTIME_TARGET)
	@test -n "$(RUNTIME_SCENARIO)" || { echo "Usage: make runtimegraph RUNTIME_SCENARIO=<input-script-without-.txt> RUNTIME_FRAMES=<frames>"; exit 2; }
	@test "$(RUNTIME_FRAMES)" -gt 0 || { echo "RUNTIME_FRAMES must be a positive frame count"; exit 2; }
	mkdir -p $(RUNTIME_OUTPUT_DIR)
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy $(RUNTIME_TARGET) --run-frames=$(RUNTIME_FRAMES) --input-script=context/input-scripts/$(RUNTIME_SCENARIO).txt --no-render --runtime-call-trace=$(RUNTIME_OUTPUT_DIR)/c_phoenix_calls.bin
	python3 tools/generate_c_runtime_callgraph.py $(RUNTIME_OUTPUT_DIR)/c_phoenix_calls.bin --binary $(RUNTIME_TARGET) --output-dir $(RUNTIME_OUTPUT_DIR) --explorer-output $(RUNTIME_EXPLORER_OUTPUT)
	python3 tools/generate_c_design_runtime_comparison.py --source-dir . --runtime $(RUNTIME_OUTPUT_DIR)/c_phoenix_runtime_calls.csv --output-dir $(RUNTIME_OUTPUT_DIR)

BOT_SEED ?= context/input-scripts/extended_playthrough.txt
BOT_FRAMES ?= 6000
BOT_ITERATIONS ?= 8
BOT_GENERATIONS ?= 6
BOT_MODE ?= jitter
BOT_TARGET ?= bird_wave_gameplay
BOT_RANDOM_SEED ?= 1
BOT_OUTPUT_DIR ?= /tmp/input-bot

bottargets:
	@python3 tools/input_bot.py list-targets

botsearch:
	@test -n "$(BOT_TARGET)" || { echo "Usage: make botsearch BOT_TARGET=<name>  (see make bottargets)"; exit 2; }
	python3 tools/input_bot.py mutate \
	  --seed $(BOT_SEED) \
	  --frames $(BOT_FRAMES) \
	  --iterations $(BOT_ITERATIONS) \
	  --generations $(BOT_GENERATIONS) \
	  --mutation-mode $(BOT_MODE) \
	  --target $(BOT_TARGET) \
	  --random-seed $(BOT_RANDOM_SEED) \
	  --output-dir $(BOT_OUTPUT_DIR)

# Not part of `make docs`: the output depends on which recording you point it
# at, so a blanket regeneration could silently replace sheets built from a
# richer trace with thinner ones.
SPRITE_DUMP ?=
spritesheets:
	python3 tools/generate_sprite_sheets.py $(if $(SPRITE_DUMP),--dump $(SPRITE_DUMP),)

help:
	@echo "c-phoenix make targets"
	@echo ""
	@echo "  make all              Build $(TARGET) (default)"
	@echo "  make run              Build and run interactively"
	@echo "  make recordrun        Build and run interactively while recording input"
	@echo "  make recordtracerun   Record an interactive session, then compare and trace it"
	@echo "  make replayrun        Build and visibly replay an input script"
	@echo "  make headlessrun      Build and run a headless replay; optionally dump RAM"
	@echo "  make demorun          Run the default demo and create a standalone C-Phoenix tracer"
	@echo "  make demo-tracer-view Generate and serve the standalone C-Phoenix tracer"
	@echo "  make comparerun       Run replay through jphoenix and c-phoenix, then compare RAM"
	@echo "  make tracerun         Run comparerun and generate an interactive visual tracer"
	@echo "  make tracer-view      Generate and serve the comparison visual tracer"
	@echo "  make tracer-view-only Serve an existing visual tracer locally"
	@echo "  make runtimegraph     Generate detailed and functional runtime call graphs"
	@echo "  make c2               Build the native C2 renderer"
	@echo "  make c2-clean         Remove C2 native build artefacts"
	@echo "  make interactive-asm  Regenerate interactive Phoenix ASM documentation"
	@echo "  make interactive-asm-view Generate ASM documentation and serve it locally"
	@echo "  make interactive-asm-view-only Serve existing ASM documentation locally"
	@echo "  make knowledge-graph-visual Regenerate the knowledge graph architecture SVG"
	@echo "  make docs             Regenerate mapping, graph and generated reference docs"
	@echo "  make spritesheets     Regenerate the sprite sheets (SPRITE_DUMP=<recording>)"
	@echo ""
	@echo "input bot - name a game moment and search for a script that reaches it"
	@echo "  make bottargets       List the built-in targets and what each one checks"
	@echo "  make botsearch        Search for a script reaching BOT_TARGET"
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
	@echo "  CONTEXT_ROOT=$(CONTEXT_ROOT)"
	@echo "  REPLAY_SCRIPT=$(REPLAY_SCRIPT)"
	@echo "  REPLAY_FRAMES=$(REPLAY_FRAMES) (headlessrun only)"
	@echo "  REPLAY_RAM_DUMP=$(if $(REPLAY_RAM_DUMP),$(REPLAY_RAM_DUMP),(disabled))"
	@echo "  REPLAY_COVERAGE_DUMP=$(if $(REPLAY_COVERAGE_DUMP),$(REPLAY_COVERAGE_DUMP),(disabled))"
	@echo "  HEADLESS_ENV=$(HEADLESS_ENV)"
	@echo "  REPLAY_EXTRA_ARGS=$(if $(REPLAY_EXTRA_ARGS),$(REPLAY_EXTRA_ARGS),(none))"
	@echo ""
	@echo "demorun defaults"
	@echo "  DEMO_SCRIPT=$(DEMO_SCRIPT)"
	@echo "  DEMO_FRAMES=$(DEMO_FRAMES)"
	@echo "  DEMO_NAME=$(DEMO_NAME)"
	@echo "  DEMO_DUMP=$(DEMO_DUMP)"
	@echo "  DEMO_RAM_DUMP is supported as a legacy alias"
	@echo "  DEMO_TRACE_OUTPUT=$(DEMO_TRACE_OUTPUT)"
	@echo "  DEMO_TRACE_KIND=$(DEMO_TRACE_KIND)"
	@echo "  DEMO_TRACE_PLAYER=$(DEMO_TRACE_PLAYER)"
	@echo "  TRACER_VIEW_PORT=$(TRACER_VIEW_PORT)"
	@echo "  DEMO_EXTRA_ARGS=$(if $(DEMO_EXTRA_ARGS),$(DEMO_EXTRA_ARGS),(none))"
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
	@echo "  TRACE_VIEW_OUTPUT=$(TRACE_VIEW_OUTPUT)"
	@echo "  TRACE_VIEW_DIR=$(TRACE_VIEW_DIR)"
	@echo "  TRACER_VIEW_PORT=$(TRACER_VIEW_PORT)"
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
	@echo "  make demorun"
	@echo "  make demorun DEMO_SCRIPT=context/input-scripts/bird-investigation.txt DEMO_FRAMES=13935 DEMO_NAME=bird-investigation"
	@echo "  make comparerun COMPARE_SCRIPT=/tmp/c-phoenix-session.txt COMPARE_FRAMES=9000 COMPARE_NAME=session"
	@echo "  make tracerun COMPARE_SCRIPT=context/input-scripts/two_player_last_grown_bird.txt COMPARE_FRAMES=9000 COMPARE_NAME=last-grown-bird COMPARE_STOP_AFTER=999999"
	@echo "  make recordtracerun RECORD_NAME=bird-investigation"
	@echo "  make recordtracerun RECORD_NAME=bird-investigation RECORD_TRACE_FRAMES=15000"
	@echo "  make bottargets"
	@echo "  make botsearch BOT_TARGET=alien_kill"
	@echo "  make botsearch BOT_TARGET=gameplay_level_9 BOT_FRAMES=12000 BOT_GENERATIONS=10"
	@echo ""
	@echo "botsearch defaults"
	@echo "  BOT_SEED=$(BOT_SEED)"
	@echo "  BOT_FRAMES=$(BOT_FRAMES)  BOT_ITERATIONS=$(BOT_ITERATIONS)  BOT_GENERATIONS=$(BOT_GENERATIONS)"
	@echo "  BOT_MODE=$(BOT_MODE)  BOT_TARGET=$(BOT_TARGET)  BOT_RANDOM_SEED=$(BOT_RANDOM_SEED)"
	@echo "  BOT_OUTPUT_DIR=$(BOT_OUTPUT_DIR)"

interactive-asm:
	@echo "Generating interactive Phoenix ASM documentation..."
	@python3 tools/generate_code_annotated_asm.py
	@python3 tools/generate_annotated_asm.py
	@python3 tools/generate_interactive_asm_html.py
	@python3 tools/generate_interactive_asm_html.py context/code-annotated.md context/code-annotated.html
	@python3 tools/generate_c_source_html.py

interactive-asm-view: interactive-asm interactive-asm-view-only

interactive-asm-view-only:
	@echo "Open http://127.0.0.1:$(ASM_VIEW_PORT)/context/Phoenix.html"
	@echo "Light theme: http://127.0.0.1:$(ASM_VIEW_PORT)/context/Phoenix.html?theme=light"
	@echo "Press Ctrl-C to stop the local viewer."
	@$(PYTHON) -m http.server $(ASM_VIEW_PORT) --bind 127.0.0.1

wave-screenshots: $(TARGET)
	@$(PYTHON) tools/capture_initial_alien_waves.py --binary $(TARGET)

knowledge-graph-visual:
	@$(PYTHON) tools/generate_knowledge_graph_visual.py

docs:
	@echo "Generating architecture mappings and graphs..."
	@python3 tools/generate_mappings.py
	@python3 tools/generate_annotated_asm.py
	@python3 tools/generate_interactive_asm_html.py
	@python3 tools/generate_interactive_asm_html.py context/code-annotated.md context/code-annotated.html
	@python3 tools/generate_callgraph.py
	@python3 tools/generate_file_callgraph.py
	@python3 tools/generate_func_prefix_callgraph.py
	@python3 tools/generate_rom_bank_callgraph.py
	@python3 tools/generate_cross_domain_callgraph.py
	@python3 tools/generate_internal_domain_callgraph.py
	@python3 tools/generate_execution_tree_callgraph.py
	@python3 tools/generate_coverage_callgraph.py
	@python3 tools/generate_stub_hunter_callgraph.py
	@python3 tools/generate_knowledge_graph_visual.py
	@python3 tools/generate_table_reference.py
	@python3 tools/generate_input_bot_reference.py
	@python3 tools/generate_input_bot_visual.py
	@echo "All documentation and graphs successfully generated in context/ !"
