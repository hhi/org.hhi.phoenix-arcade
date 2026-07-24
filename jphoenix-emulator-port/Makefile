JAVAC ?= javac
JAVA ?= java

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

.PHONY: all compile run runtimegraph libgdx run-libgdx verify verify-libgdx artifacts clean

all: compile

compile:
	mkdir -p $(RUNTIME_CLASSES)
	$(JAVAC) -Xlint:all -d $(RUNTIME_CLASSES) $(RUNTIME_SOURCES)

run: compile
	$(JAVA) -cp $(RUNTIME_CLASSES) PhoenixDesktop $(if $(ROM_DIR),--rom-dir=$(ROM_DIR))

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
