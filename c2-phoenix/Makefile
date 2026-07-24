.PHONY: help test demo compare summary native run replayrun headlessrun native-check native-compare native-clean

PYTHON ?= python3
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
NATIVE_REPLAY_SCRIPT ?= ../c-phoenix/context/input-scripts/basic_playthrough.txt
NATIVE_REPLAY_FRAMES ?= 1200
NATIVE_EXTRA_ARGS ?=
NATIVE_REFERENCE_DUMP ?=
NATIVE_DUMP ?= /tmp/c2-$(SCENARIO).bin
NATIVE_COMPARE_REGIONS ?= 4340-47FF,4B40-4BE5
NATIVE_COMPARE_STOP_AFTER ?= 999999

help:
	@echo "C2-Phoenix semantic renderer prototype"
	@echo "  make test                         Run contract tests"
	@echo "  make demo DUMP=/path/to/dump.bin  Export frames and create an HTML viewer"
	@echo "  make compare                      Compare JPhoenix and C-Phoenix semantic exports"
	@echo "  make summary                      Report semantic scenario coverage"
	@echo "  make native                       Build the interactive SDL C2 application"
	@echo "  make run                          Build and play C2 interactively"
	@echo "  make replayrun                    Visibly replay an input script in C2"
	@echo "  make headlessrun                  Run a deterministic native C2 replay"
	@echo "  make native-check                 Verify that native C2 has no graphics/PROM symbols"
	@echo "  make native-compare               Compare a native C2 replay against a JPhoenix dump"
	@echo "  make native C2_VARIANT=hires2     Build a named rendering variant into its own binary"

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
	./$(NATIVE_TARGET) --input-script=$(NATIVE_REPLAY_SCRIPT) $(NATIVE_EXTRA_ARGS)

headlessrun: native
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./$(NATIVE_TARGET) --run-frames=$(NATIVE_REPLAY_FRAMES) --input-script=$(NATIVE_REPLAY_SCRIPT) --no-render $(NATIVE_EXTRA_ARGS)

native-check: native
	@if nm "$(NATIVE_TARGET)" | grep -E 'gfx_mem|palette_prom|init_phoenix_palette|get_phoenix_color' >/dev/null; then \
		echo "native C2 unexpectedly contains graphics/PROM symbols"; exit 1; \
	fi
	@echo "native C2 binary contains no graphics or colour-PROM symbols"

native-compare: native
	@test -n "$(NATIVE_REFERENCE_DUMP)" || { echo "Set NATIVE_REFERENCE_DUMP=/path/to/jphoenix.bin"; exit 2; }
	@test -f "$(NATIVE_REFERENCE_DUMP)" || { echo "Reference dump not found: $(NATIVE_REFERENCE_DUMP)"; exit 2; }
	SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./$(NATIVE_TARGET) --run-frames=$(NATIVE_REPLAY_FRAMES) --input-script=$(NATIVE_REPLAY_SCRIPT) --no-render --ram-dump=$(NATIVE_DUMP) $(NATIVE_EXTRA_ARGS)
	python3 ../c-phoenix/tools/compare_ram_dumps.py $(NATIVE_REFERENCE_DUMP) $(NATIVE_DUMP) --align-c98 --regions $(NATIVE_COMPARE_REGIONS) --stop-after $(NATIVE_COMPARE_STOP_AFTER)

native-clean:
	$(MAKE) -C ../c-phoenix c2-clean
