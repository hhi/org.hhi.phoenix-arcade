# Repository Guidelines

## Project Structure & Module Organization
- This repository is a hand-translated C port of the Phoenix arcade Z80 ROM.
- Core C sources live in the repository root (`*.c`, `*.h`) and are grouped by
  gameplay/hardware area: `alien_*`, `bird_*`, `mothership_*`, `state_*`,
  `weapon_collision.c`, `hw_video_audio.c`, `platform_sdl.c`, and related files.
- Build artifacts are generated next to the sources as `*.o` and the
  `c-phoenix` binary.
- Python tools live in `tools/`; they generate mappings/callgraphs, compare RAM
  dumps, mutate input scripts, and inspect sprite traces.
- Tests live in `tests/` and use Python `unittest`.
- Reference material lives in `context/`, especially `code-annotated.asm`,
  `code-annotated.md`, `RAMUse.md`, `mapping/`, and `input-scripts/`.
- Current project status and porting notes live in `context/STATUS.md`; proposed cleanup
  notes may live in `status2.md`.

## Build, Run, and Development Commands
- Build: `make`
- Clean: `make clean`
- Run interactively: `./c-phoenix`
- Headless deterministic run: `./c-phoenix --run-frames=3600 --no-render`
- Run with input script:
  `./c-phoenix --run-frames=4000 --input-script=context/input-scripts/basic_playthrough.txt --no-render`
- Generate a RAM dump:
  `./c-phoenix --run-frames=3610 --ram-dump=/tmp/port.bin --no-render`
- Compare RAM dumps:
  `python3 tools/compare_ram_dumps.py /tmp/jphx.bin /tmp/port.bin --align-c98 --stop-after 999999`
- Run tests:
  `python3 -m unittest discover tests`
- Generate mapping docs:
  `python3 tools/generate_mappings.py`
- Generate annotated ASM markdown:
  `python3 tools/generate_annotated_asm.py`

## Coding Style & Naming Conventions
- C: follow the existing local style in the touched file. Keep changes tightly
  scoped and avoid broad refactors during porting fixes.
- Preserve ASM-address anchors in comments (`[ASM: XXXX-YYYY]`) when changing
  translated code.
- `lNNNN` function names are acceptable when they preserve useful ASM traceability.
  Prefer semantic names for new externally visible helpers when the behavior is
  known, with the ASM address retained in the comment.
- Python tools should follow PEP 8, use `snake_case`, and stay deterministic.
- Do not introduce hardcoded absolute paths. Prefer CLI flags, `/tmp` for
  throwaway local artifacts, or existing project conventions.

## Testing & Verification Guidelines
- For pure documentation changes, a readback check is enough.
- For C behavior changes, at minimum run `make` and the relevant Python tests.
- For translated Z80 behavior changes, also run a deterministic headless replay
  and compare RAM dumps against a known jphoenix reference when available.
- When modifying mapping or annotation tooling, regenerate the affected docs and
  inspect the generated diff for bogus ranges, stale links, or "Unknown / None"
  regressions.
- Keep tests and scripts fast enough to run locally; prefer deterministic input
  scripts from `context/input-scripts/`.

## Commit & Pull Request Guidelines
- Use short, imperative commit subjects that describe the subsystem touched.
- Group behavior changes separately from generated documentation churn where
  practical.
- PRs should list changed behavior, touched commands, generated artifacts, and
  validation steps.
- Do not commit large runtime dumps, screenshots, generated experiments, or ROM
  assets unless explicitly requested.

## Security & Configuration Tips
- Do not commit ROM assets or machine-local paths.
- Keep large RAM dumps, coverage outputs, screenshots, and temporary viewers out
  of version control unless they are intentionally curated test fixtures.
- SDL2 is required for normal builds/runs; use dummy video/headless flags for
  automated runs where appropriate.

## AI Porting Rules
- Geen fantasievertalingen: code moet 100% de Z80 ASM volgen.
- Maak nooit ongevraagd wijzigingen in vertaalde gameplaycode; stel bij
  portingwijzigingen altijd eerst een implementatieplan op ter goedkeuring.
- Gebruik `context/code-annotated.asm` / `context/code-annotated.md` en de
  bestaande `[ASM: ...]` comments als bron van waarheid.
- Als een routine nog onduidelijk is, documenteer de onzekerheid in plaats van
  gedrag te verzinnen.
