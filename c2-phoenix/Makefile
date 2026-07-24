.PHONY: help test demo compare summary native run replayrun headlessrun demorun native-check native-compare native-clean

PYTHON ?= python3
OPEN ?= open
SCENARIO ?= bird-investigation
TRACE ?= /tmp/$(SCENARIO)-semantic.json
VIEWER ?= /tmp/$(SCENARIO)-c2.html
DUMP ?= /tmp/port_$(SCENARIO).bin
REFERENCE_DUMP ?= /tmp/ref_$(SCENARIO).bin
REFERENCE_TRACE ?= /tmp/ref_$(SCENARIO)-semantic.json
PORT_TRACE ?= /tmp/port_$(SCENARIO)-semantic.json
SUMMARY_ARGS ?=
C2_VARIANT ?=
NATIVE_TARGET ?= build/native$(if $(C2_VARIANT),/$(C2_VARIANT))/c2-phoenix
# Keep replay controls aligned with c-phoenix. Input scripts are always
# addressed as context/... by users; this prefix resolves that location from
# the C2 directory. The NATIVE_* spellings remain supported for existing use.
CONTEXT_ROOT ?= ../c-phoenix/context
resolve_context_path = $(if $(filter context/%,$(1)),$(CONTEXT_ROOT)/$(patsubst context/%,%,$(1)),$(1))
REPLAY_SCRIPT ?= $(CONTEXT_ROOT)/input-scripts/basic_playthrough.txt
REPLAY_FRAMES ?= 1200
REPLAY_EXTRA_ARGS ?=
NATIVE_REPLAY_SCRIPT ?= $(REPLAY_SCRIPT)
NATIVE_REPLAY_FRAMES ?= $(REPLAY_FRAMES)
NATIVE_EXTRA_ARGS ?= $(REPLAY_EXTRA_ARGS)
DEMO_SCRIPT ?= $(CONTEXT_ROOT)/input-scripts/bird-investigation.txt
DEMO_FRAMES ?= 13935
DEMO_NAME ?= bird-investigation
DEMO_DUMP ?= /tmp/c2-phoenix-$(DEMO_NAME).bin
DEMO_TRACE_OUTPUT ?= /tmp/c2-phoenix-$(DEMO_NAME)-tracer.html
DEMO_TRACE_KIND ?= all
DEMO_TRACE_PLAYER ?= all
DEMO_EXTRA_ARGS ?=
NATIVE_REFERENCE_DUMP ?=
NATIVE_DUMP ?= /tmp/c2-$(SCENARIO).bin
NATIVE_COMPARE_REGIONS ?= 4340-47FF,4B40-4BE5
NATIVE_COMPARE_STOP_AFTER ?= 999999

help:
	@echo "c2-phoenix make targets"
	@echo ""
	@echo "  make native          Build the interactive SDL C2 application"
	@echo "  make run             Build and run C2 interactively"
	@echo "  make replayrun       Visibly replay an input script"
	@echo "  make headlessrun     Run a deterministic, headless replay"
	@echo "  make demorun         Run the default demo and create a standalone C2 tracer"
	@echo "  make native-compare  Compare a native C2 replay against a JPhoenix dump"
	@echo "  make native-check    Verify that the C2 binary contains no graphics/PROM symbols"
	@echo "  make native-clean    Remove generated native C2 build artefacts"
	@echo "  make test            Run C2 contract tests"
	@echo "  make demo            Export a RAM dump to a semantic HTML viewer"
	@echo "  make compare         Compare semantic exports from JPhoenix and C-Phoenix"
	@echo "  make summary         Report semantic scenario coverage"
	@echo "  make help            Show this help"
	@echo ""
	@echo "requirements"
	@echo "  native/run/replayrun/headlessrun: gcc and SDL2"
	@echo "  native-compare: also a JPhoenix RAM dump"
	@echo "  demo/compare/summary: Python 3 and the relevant RAM dumps"
	@echo ""
	@echo "replay defaults"
	@echo "  CONTEXT_ROOT=$(CONTEXT_ROOT)"
	@echo "  REPLAY_SCRIPT=$(REPLAY_SCRIPT)"
	@echo "  REPLAY_FRAMES=$(REPLAY_FRAMES) (headlessrun and native-compare only)"
	@echo "  REPLAY_EXTRA_ARGS=$(if $(REPLAY_EXTRA_ARGS),$(REPLAY_EXTRA_ARGS),(none))"
	@echo "  NATIVE_REPLAY_SCRIPT/NATIVE_REPLAY_FRAMES/NATIVE_EXTRA_ARGS remain supported aliases"
	@echo ""
	@echo "demorun defaults"
	@echo "  DEMO_SCRIPT=$(DEMO_SCRIPT)"
	@echo "  DEMO_FRAMES=$(DEMO_FRAMES)"
	@echo "  DEMO_NAME=$(DEMO_NAME)"
	@echo "  DEMO_DUMP=$(DEMO_DUMP)"
	@echo "  DEMO_TRACE_OUTPUT=$(DEMO_TRACE_OUTPUT)"
	@echo "  DEMO_TRACE_KIND=$(DEMO_TRACE_KIND)"
	@echo "  DEMO_TRACE_PLAYER=$(DEMO_TRACE_PLAYER)"
	@echo "  DEMO_EXTRA_ARGS=$(if $(DEMO_EXTRA_ARGS),$(DEMO_EXTRA_ARGS),(none))"
	@echo ""
	@echo "examples"
	@echo "  make run"
	@echo "  make replayrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt"
	@echo "  make headlessrun REPLAY_SCRIPT=context/input-scripts/bird-investigation.txt REPLAY_FRAMES=13935"
	@echo "  make demorun"
	@echo "  make native C2_VARIANT=hires2"
	@echo "  make native-compare NATIVE_REFERENCE_DUMP=/tmp/ref_bird-investigation.bin REPLAY_FRAMES=13935"

test:
	$(PYTHON) -m unittest discover tests

demo:
	@test -f "$(DUMP)" || { \
		echo "RAM dump not found: $(DUMP)"; \
		echo "Create it first from c-phoenix:"; \
		echo "  make -C ../c-phoenix tracerun COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt COMPARE_FRAMES=13935 COMPARE_NAME=bird-investigation COMPARE_STOP_AFTER=999999"; \
		exit 2; \
	}
	$(PYTHON) tools/extract_semantic_frames.py $(DUMP) --output $(TRACE)
	$(PYTHON) tools/render_semantic_trace.py $(TRACE) --output $(VIEWER)
	@echo "C2 viewer: $(VIEWER)"

compare:
	@test -f "$(REFERENCE_DUMP)" || { echo "Reference dump not found: $(REFERENCE_DUMP)"; exit 2; }
	@test -f "$(DUMP)" || { echo "C-Phoenix dump not found: $(DUMP)"; exit 2; }
	$(PYTHON) tools/extract_semantic_frames.py $(REFERENCE_DUMP) --output $(REFERENCE_TRACE)
	$(PYTHON) tools/extract_semantic_frames.py $(DUMP) --output $(PORT_TRACE)
	$(PYTHON) tools/compare_semantic_frames.py $(REFERENCE_TRACE) $(PORT_TRACE)

summary:
	@test -f "$(DUMP)" || { echo "C-Phoenix dump not found: $(DUMP)"; exit 2; }
	$(PYTHON) tools/extract_semantic_frames.py $(DUMP) --output $(TRACE)
	$(PYTHON) tools/summarize_semantic_scenario.py $(TRACE) --name $(SCENARIO) $(SUMMARY_ARGS)

native:
	$(MAKE) -C ../c-phoenix c2 C2_VARIANT=$(C2_VARIANT)

run: native
	./$(NATIVE_TARGET) $(NATIVE_EXTRA_ARGS)

replayrun: native
	./$(NATIVE_TARGET) --input-script=$(call resolve_context_path,$(NATIVE_REPLAY_SCRIPT)) $(NATIVE_EXTRA_ARGS)

headlessrun: native
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./$(NATIVE_TARGET) --run-frames=$(NATIVE_REPLAY_FRAMES) --input-script=$(call resolve_context_path,$(NATIVE_REPLAY_SCRIPT)) --no-render $(NATIVE_EXTRA_ARGS)

# Standalone C2 object tracer: no JPhoenix dump or comparison needed.
demorun: native
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./$(NATIVE_TARGET) --run-frames=$(DEMO_FRAMES) --input-script=$(call resolve_context_path,$(DEMO_SCRIPT)) --no-render --ram-dump=$(DEMO_DUMP) $(DEMO_EXTRA_ARGS)
	$(PYTHON) ../c-phoenix/tools/view_sprite_trace.py $(DEMO_DUMP) --reference-label c2-phoenix --kind $(DEMO_TRACE_KIND) --player $(DEMO_TRACE_PLAYER) --title "C2-Phoenix $(DEMO_NAME) object tracer" --output=$(DEMO_TRACE_OUTPUT)
	$(OPEN) "$(DEMO_TRACE_OUTPUT)"
	@echo "Opened C2-Phoenix object tracer: $(DEMO_TRACE_OUTPUT)"

native-check: native
	@if nm "$(NATIVE_TARGET)" | grep -E 'gfx_mem|palette_prom|init_phoenix_palette|get_phoenix_color' >/dev/null; then \
		echo "native C2 unexpectedly contains graphics/PROM symbols"; exit 1; \
	fi
	@echo "native C2 binary contains no graphics or colour-PROM symbols"

native-compare: native
	@test -n "$(NATIVE_REFERENCE_DUMP)" || { echo "Set NATIVE_REFERENCE_DUMP=/path/to/jphoenix.bin"; exit 2; }
	@test -f "$(NATIVE_REFERENCE_DUMP)" || { echo "Reference dump not found: $(NATIVE_REFERENCE_DUMP)"; exit 2; }
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./$(NATIVE_TARGET) --run-frames=$(NATIVE_REPLAY_FRAMES) --input-script=$(call resolve_context_path,$(NATIVE_REPLAY_SCRIPT)) --no-render --ram-dump=$(NATIVE_DUMP) $(NATIVE_EXTRA_ARGS)
	python3 ../c-phoenix/tools/compare_ram_dumps.py $(NATIVE_REFERENCE_DUMP) $(NATIVE_DUMP) --align-c98 --regions $(NATIVE_COMPARE_REGIONS) --stop-after $(NATIVE_COMPARE_STOP_AFTER)

native-clean:
	$(MAKE) -C ../c-phoenix c2-clean
