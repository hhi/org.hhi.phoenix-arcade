.PHONY: help build all clean c-build c-asm-docs c-asm-view c-asm-view-only c-tracer-view c-tracer-view-only c2-build c2-run c2-tracer-view c2-tracer-view-only c2-demo-view c2-demo-view-only j-build j-tracer-view j-tracer-view-only c-test j-test c2-test verify links large-files public-audit romcheck romnormalize rombuild romprepare gen-phoenix-tables

ROM_DIR ?= roms/local
ROM_SET ?= roms/phoenix-amstar/rom-set.json
ROM_OUTPUT_DIR ?= roms/assembled
ASM_VIEW_PORT ?= 8765
TRACER_VIEW_PORT ?= 8766
C2_VIEW_PORT ?= 8767

help:
	@echo "Phoenix Arcade monorepo"
	@echo "  make build        Build C-Phoenix, C2-Phoenix, and JPhoenix"
	@echo "  make all          Alias for make build"
	@echo "  make clean        Remove local C, C2-native, and Java build artefacts"
	@echo "  make c-build      Build C-Phoenix"
	@echo "  make c-asm-docs   Generate interactive Phoenix ASM documentation"
	@echo "  make c-asm-view   Generate and serve Phoenix ASM documentation locally"
	@echo "  make c-asm-view-only Serve existing Phoenix ASM documentation locally"
	@echo "  make c-tracer-view Generate and serve the C-Phoenix comparison tracer"
	@echo "  make c-tracer-view-only Serve an existing C-Phoenix tracer locally"
	@echo "  make c2-build     Build the native interactive C2-Phoenix application"
	@echo "  make c2-run       Build and run native C2-Phoenix"
	@echo "  make c2-tracer-view Generate and serve the standalone C2-Phoenix tracer"
	@echo "  make c2-tracer-view-only Serve an existing C2-Phoenix tracer locally"
	@echo "  make c2-demo-view Generate and serve the C2 semantic HTML viewer"
	@echo "  make c2-demo-view-only Serve an existing C2 semantic HTML viewer locally"
	@echo "  make j-build      Build JPhoenix"
	@echo "  make j-tracer-view Generate and serve the JPhoenix tracer locally"
	@echo "  make j-tracer-view-only Serve an existing JPhoenix tracer locally"
	@echo "  make c-test       Run C-Phoenix tests"
	@echo "  make c2-test      Run C2-Phoenix semantic contract tests"
	@echo "  make j-test       Run JPhoenix verification"
	@echo "  make verify       Build and verify both projects"
	@echo "  make links        Verify local Markdown links"
	@echo "  make large-files  Audit repository file sizes"
	@echo "  make public-audit Report private-only material before a public export"
	@echo "  make romcheck     Validate ROM_DIR chip dumps against ROM_SET (default: $(ROM_DIR))"
	@echo "  make romnormalize Match ROM_DIR chip hashes, normalize names, and create phoenix_amstar-set1.zip"
	@echo "  make rombuild     Assemble ROM_DIR chip dumps into ROM_OUTPUT_DIR (default: $(ROM_OUTPUT_DIR))"
	@echo "  make romprepare   Assemble the ROMs and regenerate the derived C sources"
	@echo "  make gen-phoenix-tables Regenerate c-phoenix/phoenix_tables.c from ROM_OUTPUT_DIR (aborts on mismatch)"

# Build every runnable implementation.  This deliberately excludes tests,
# documentation generation, trace generation, ROM preparation, and viewers.
build: c-build c2-build j-build

# Conventional alias for build systems and CI callers.
all: build

# Remove only generated compilation output.  ROMs, generated documentation,
# traces, recordings, and source files are intentionally preserved.
clean:
	$(MAKE) -C c-phoenix clean
	$(MAKE) -C c-phoenix c2-clean
	$(MAKE) -C jphoenix-emulator-port clean

c-build:
	$(MAKE) -C c-phoenix

c-asm-docs:
	$(MAKE) -C c-phoenix interactive-asm

c-asm-view:
	$(MAKE) -C c-phoenix interactive-asm-view ASM_VIEW_PORT=$(ASM_VIEW_PORT)

c-asm-view-only:
	$(MAKE) -C c-phoenix interactive-asm-view-only ASM_VIEW_PORT=$(ASM_VIEW_PORT)

c-tracer-view:
	$(MAKE) -C c-phoenix tracer-view TRACER_VIEW_PORT=$(TRACER_VIEW_PORT)

c-tracer-view-only:
	$(MAKE) -C c-phoenix tracer-view-only TRACER_VIEW_PORT=$(TRACER_VIEW_PORT)

c2-build:
	$(MAKE) -C c2-phoenix native

c2-run:
	$(MAKE) -C c2-phoenix run

c2-tracer-view:
	$(MAKE) -C c2-phoenix tracer-view TRACER_VIEW_PORT=$(C2_VIEW_PORT)

c2-tracer-view-only:
	$(MAKE) -C c2-phoenix tracer-view-only TRACER_VIEW_PORT=$(C2_VIEW_PORT)

c2-demo-view:
	$(MAKE) -C c2-phoenix demo-view TRACER_VIEW_PORT=$(C2_VIEW_PORT)

c2-demo-view-only:
	$(MAKE) -C c2-phoenix demo-view-only TRACER_VIEW_PORT=$(C2_VIEW_PORT)

j-build:
	$(MAKE) -C jphoenix-emulator-port

j-tracer-view:
	$(MAKE) -C jphoenix-emulator-port tracer-view TRACER_VIEW_PORT=$(TRACER_VIEW_PORT)

j-tracer-view-only:
	$(MAKE) -C jphoenix-emulator-port tracer-view-only TRACER_VIEW_PORT=$(TRACER_VIEW_PORT)

c-test:
	python3 -m unittest discover c-phoenix/tests

c2-test:
	$(MAKE) -C c2-phoenix test

j-test:
	$(MAKE) -C jphoenix-emulator-port verify

verify: c-build j-build c-test c2-test j-test links large-files

links:
	python3 tools/check_markdown_links.py .

large-files:
	python3 tools/audit_large_files.py .

public-audit:
	python3 tools/audit_public_export.py .

romcheck:
	python3 tools/rom_tool.py --manifest $(ROM_SET) check --rom-dir $(ROM_DIR)

romnormalize:
	python3 tools/rom_tool.py --manifest $(ROM_SET) normalize --rom-dir $(ROM_DIR)

rombuild:
	python3 tools/rom_tool.py --manifest $(ROM_SET) build --rom-dir $(ROM_DIR) --output-dir $(ROM_OUTPUT_DIR)

# The normal preparation workflow: turn a validated local chip set into the
# assembled ROM images and verify/regenerate the C sources derived from them.
romprepare: rombuild gen-phoenix-tables

# Both targets below only ever write when the regenerated bytes exactly
# match the currently-committed file (they abort otherwise), so they are
# safe to run against the tracked c-phoenix sources directly: a match is a
# no-op, a mismatch aborts without touching anything. Pass ALLOW_MISMATCH=1
# to force an update after a genuine chip-set change.
gen-phoenix-tables: rombuild
	python3 tools/generate_phoenix_tables.py \
		--header c-phoenix/phoenix_tables.h \
		--existing c-phoenix/phoenix_tables.c \
		--prg-mem $(ROM_OUTPUT_DIR)/program.rom \
		--output c-phoenix/phoenix_tables.c \
		$(if $(ALLOW_MISMATCH),--allow-mismatch)
