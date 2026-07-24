JAVAC ?= javac
JAVA ?= java
OPEN ?= open

BUILD_DIR := build
RUNTIME_CLASSES := $(BUILD_DIR)/classes
TEST_CLASSES := $(BUILD_DIR)/test-classes
RUNTIME_SOURCES := \
	I8080.java \
	JavaSoundPcmSink.java \
	MameLofiResampler.java \
	PcmSink.java \
	PcCoverage.java \
	Phoenix.java \
	PhoenixCanvas.java \
	PhoenixCoverageRunner.java \
	PhoenixDesktop.java \
	PhoenixFrameBuffer.java \
	PhoenixGraphicsDecoder.java \
	PhoenixPalette.java \
	PhoenixInputScript.java \
	PhoenixSaveState.java \
	PhoenixStateHotkeys.java \
	PhoenixVideoRenderer.java \
	RomLoader.java \
	RuntimeCallTrace.java \
	Sound.java \
	SoundControlMapping.java \
	TMS36XX.java
TEST_SOURCES := $(wildcard tests/*.java)
TEST_SUPPORT_SOURCES := $(wildcard tools/sound/*.java)
RUNTIME_SCENARIO ?=
RUNTIME_SCRIPT ?= ../c-phoenix/context/input-scripts/$(RUNTIME_SCENARIO).txt
RUNTIME_FRAMES ?= 0
RUNTIME_OUTPUT_DIR ?= $(CURDIR)/context/runtimegraphs/$(RUNTIME_SCENARIO)
RUNTIME_PC_COVERAGE_DIR ?= $(RUNTIME_OUTPUT_DIR)/pc-coverage
RUNTIME_LABELS ?= ../c-phoenix/context/code-annotated.asm
ROM_DIR ?= ../roms/assembled
DEMO_SCRIPT ?= ../c-phoenix/context/input-scripts/bird-investigation.txt
DEMO_FRAMES ?= 13935
DEMO_NAME ?= bird-investigation
DEMO_DUMP ?= /tmp/jphoenix-$(DEMO_NAME).bin
DEMO_COVERAGE_DIR ?= /tmp/jphoenix-$(DEMO_NAME)-coverage
DEMO_TRACE_OUTPUT ?= /tmp/jphoenix-$(DEMO_NAME)-tracer.html
DEMO_TRACE_KIND ?= all
DEMO_TRACE_PLAYER ?= all

.PHONY: all compile run demorun runtimegraph libgdx run-libgdx verify verify-libgdx artifacts clean help

all: compile

compile:
	mkdir -p $(RUNTIME_CLASSES)
	$(JAVAC) -Xlint:all -d $(RUNTIME_CLASSES) $(RUNTIME_SOURCES)

run: compile
	$(JAVA) -cp $(RUNTIME_CLASSES) PhoenixDesktop $(if $(ROM_DIR),--rom-dir=$(ROM_DIR))

# Standalone JPhoenix object tracer: runs an input script, records RAM, and
# renders the same HTML tracer used by the C implementations.
demorun: compile
	mkdir -p $(DEMO_COVERAGE_DIR)
	$(JAVA) -Dphoenix.inputclock=poll -Dphoenix.romdir=$(ROM_DIR) -Dphoenix.ramdump=$(DEMO_DUMP) -Dphoenix.ramdump.frames=$(DEMO_FRAMES) -cp $(RUNTIME_CLASSES) PhoenixCoverageRunner $(DEMO_SCRIPT) $(DEMO_COVERAGE_DIR) $(DEMO_FRAMES)
	python3 ../c-phoenix/tools/view_sprite_trace.py $(DEMO_DUMP) --reference-label jphoenix --kind $(DEMO_TRACE_KIND) --player $(DEMO_TRACE_PLAYER) --title "JPhoenix $(DEMO_NAME) object tracer" --output=$(DEMO_TRACE_OUTPUT)
	$(OPEN) "$(DEMO_TRACE_OUTPUT)"
	@echo "Opened JPhoenix object tracer: $(DEMO_TRACE_OUTPUT)"

runtimegraph: compile
	@test -n "$(RUNTIME_SCENARIO)" || { echo "Usage: make runtimegraph RUNTIME_SCENARIO=<input-script-without-.txt> RUNTIME_FRAMES=<frames>"; exit 2; }
	@test "$(RUNTIME_FRAMES)" -gt 0 || { echo "RUNTIME_FRAMES must be a positive frame count"; exit 2; }
	mkdir -p $(RUNTIME_OUTPUT_DIR) $(RUNTIME_PC_COVERAGE_DIR)
	$(JAVA) -Dphoenix.inputclock=poll -Dphoenix.runtimecalltrace=$(RUNTIME_OUTPUT_DIR)/jphoenix_calls.csv $(if $(ROM_DIR),-Dphoenix.romdir=$(ROM_DIR)) -cp $(RUNTIME_CLASSES) PhoenixCoverageRunner $(RUNTIME_SCRIPT) $(RUNTIME_PC_COVERAGE_DIR) $(RUNTIME_FRAMES)
	python3 tools/generate_runtime_callgraph.py $(RUNTIME_OUTPUT_DIR)/jphoenix_calls.csv --output-dir $(RUNTIME_OUTPUT_DIR) --title "JPhoenix runtime calls: $(RUNTIME_SCENARIO)" --labels $(RUNTIME_LABELS)
	python3 tools/generate_8080_design_runtime_comparison.py --asm $(RUNTIME_LABELS) --runtime $(RUNTIME_OUTPUT_DIR)/jphoenix_calls.csv --output-dir $(RUNTIME_OUTPUT_DIR)
	python3 tools/generate_8080_semantic_callgraph.py --asm $(RUNTIME_LABELS) --runtime $(RUNTIME_OUTPUT_DIR)/jphoenix_calls.csv --output-dir $(RUNTIME_OUTPUT_DIR)
	python3 tools/generate_8080_boot_flow.py --runtime $(RUNTIME_OUTPUT_DIR)/jphoenix_calls.csv --output-dir $(RUNTIME_OUTPUT_DIR)
	@echo "Runtime call graph: $(RUNTIME_OUTPUT_DIR)/jphoenix_runtime_callgraph.svg"

libgdx:
	./gradlew classes

run-libgdx:
	./gradlew run

verify:
	mkdir -p $(TEST_CLASSES)
	$(JAVAC) -Xlint:all -d $(TEST_CLASSES) $(RUNTIME_SOURCES) $(TEST_SUPPORT_SOURCES) $(TEST_SOURCES)
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) RomLoaderTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PhoenixPaletteTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PhoenixGraphicsDecoderTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PhoenixVideoRendererTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PhoenixVideoRegisterTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PhoenixRamDumpTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PhoenixInputScriptTest
	$(JAVA) -Djava.awt.headless=true -Dphoenix.inputclock=poll -cp $(TEST_CLASSES) PhoenixInputClockPollTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PcCoverageTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PhoenixSaveStateTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) PhoenixPauseTest
	$(JAVA) -Djava.awt.headless=true -cp $(TEST_CLASSES) I8080ExecutionStopTest
	$(JAVA) -cp $(TEST_CLASSES) TMS36XXTuneLengthTest
	$(JAVA) -cp $(TEST_CLASSES) SoundVerificationTest

verify-libgdx:
	./gradlew verifyLibgdx

artifacts: verify
	$(JAVA) -cp $(TEST_CLASSES) SoundArtifactDump

clean:
	rm -rf $(BUILD_DIR) sound-renders
	rm -f *.class

help:
	@echo "jphoenix-emulator-port make targets"
	@echo ""
	@echo "  make compile    Compile JPhoenix"
	@echo "  make run        Build and run the desktop emulator"
	@echo "  make demorun    Run the default demo and create a standalone JPhoenix tracer"
	@echo "  make verify     Run the Java verification suite"
	@echo "  make help       Show this help"
	@echo ""
	@echo "demorun defaults"
	@echo "  DEMO_SCRIPT=$(DEMO_SCRIPT)"
	@echo "  DEMO_FRAMES=$(DEMO_FRAMES)"
	@echo "  DEMO_NAME=$(DEMO_NAME)"
	@echo "  DEMO_DUMP=$(DEMO_DUMP)"
	@echo "  DEMO_TRACE_OUTPUT=$(DEMO_TRACE_OUTPUT)"
	@echo ""
	@echo "example"
	@echo "  make demorun"
