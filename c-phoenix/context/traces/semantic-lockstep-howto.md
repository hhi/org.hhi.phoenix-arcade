# How-to: Semantic Lockstep Analysis

Use lockstep to substantiate the meaning of a RAM field, bit, routine, or
transition. The annotated Z80 assembly and `RAMUse.md` remain the source of
truth when evidence conflicts.

## Workflow

1. State a testable hypothesis and alternatives.
2. Select or record an input script that reaches the relevant moment.
3. Produce a jphoenix/C-Phoenix dump pair using the poll clock.
4. Locate the relevant record through `results.jsonl`, a trace, or the viewer.
5. Extract a small RAM window around that record.
6. Read ASM, C code, RAM mutations, and lockstep output together.
7. Record the conclusion as a curated semantic case.
8. Only then introduce a semantic C name, comment, or constant.

Build both projects, then create disposable dumps:

```sh
tools/lockstep/dump_pair.sh context/input-scripts/<script>.txt <frames> <name>
```

The jphoenix poll clock is essential because it places input events at
deterministic game moments. Dumps are written to `/tmp/ref_<name>.bin` and
`/tmp/port_<name>.bin`.

Extract the target record and a small RAM range:

```sh
python3 tools/lockstep/semantic_delta.py \
  /tmp/ref_<name>.bin /tmp/port_<name>.bin \
  --record <record> --window 1 --regions 43A0-43C7 \
  --output-json=/tmp/<name>-delta.json \
  --output-md=/tmp/<name>-delta.md
```

The report lists reference mutations, port mutations, and remaining parity
diffs. An empty parity-diff table proves equal behaviour in the chosen region;
it does not independently identify what an anonymous byte means. Connect every
observation to ASM, RAMUse, and the translated C call chain. Direct assignments
to `state` can bypass generic write hooks.

## Evidence Matrix

| Evidence | Question |
| --- | --- |
| ASM | Which instructions read, test, or write the byte? |
| RAMUse | Which address or structure is involved? |
| C | Which translated function matches the ASM range? |
| Delta window | What transition occurs at the target record? |
| Lockstep | Does the reference make the same transition? |

## Example: Last Grown Bird

The fixture is
[`two_player_last_grown_bird.txt`](../input-scripts/two_player_last_grown_bird.txt).
Use records `6999..7001` around target `7000` in `$43A0-$43C7`:

```sh
gzip -dc context/traces/two_player_last_grown_bird_compare/j-last-grown-bird.bin.gz > /tmp/j-last-grown-bird.bin
gzip -dc context/traces/two_player_last_grown_bird_compare/c-last-grown-bird.bin.gz > /tmp/c-last-grown-bird.bin
python3 tools/lockstep/semantic_delta.py \
  /tmp/j-last-grown-bird.bin \
  /tmp/c-last-grown-bird.bin \
  --record 7000 --window 1 --regions 43A0-43C7 \
  --output-json=/tmp/last-grown-bird-delta.json \
  --output-md=/tmp/last-grown-bird-delta.md
```

The reference and C port show equal transitions: `CounterB9` changes at 6999
and 7001; `PlayerShape` progresses `0x00 -> 0x04 -> 0x08 -> 0x0C`; and
`PlayerShipX` increments `0x4C -> 0x4D -> 0x4E -> 0x4F`. No parity diffs occur
in the selected region. This validates the extractor output, not a new meaning
for `CounterB9` beyond the existing ASM/RAM documentation.

For analysis or documentation changes, run the unit tests, Python compilation,
and `git diff --check`. The full scripted lockstep batch takes about two hours;
rerun it after gameplay, lockstep criteria, dump format, or comparison-logic
changes. Record real findings with
[semantic-case-template.md](semantic-case-template.md), retaining the
question, evidence, commands, conclusion, and confidence.
