# Semantic Trace Case: Template

Use this template when a lockstep investigation supports the meaning of a RAM
field, bit, routine, or transition. A case documents evidence; it does not
replace annotated ASM as the source of truth.

````md
# CASE-<SHORT-NAME>

## Question

What meaning or invariant is being investigated?

## Hypothesis

State a testable hypothesis. Include alternative explanations when they still
exist.

## Scenario

- Input script: `context/input-scripts/<name>.txt`
- Target window: record `N..M`
- Relevant RAM: `$....`, `$....`
- Expected states/level/player bank: ...

## Reproduction

```bash
tools/lockstep/dump_pair.sh context/input-scripts/<name>.txt <frames> <name>
python3 tools/lockstep/semantic_delta.py \
  /tmp/ref_<name>.bin /tmp/port_<name>.bin \
  --record <N> --window 1 --regions <ranges> \
  --output-json=/tmp/<name>.json --output-md=/tmp/<name>.md
```

## Static Evidence

- ASM: `$....-$....`; relevant instructions and branches.
- RAMUse: fields/addresses.
- C: function(s) and existing `[ASM: ...]` anchors.

## Dynamic Evidence

Describe only mutations observed in the delta window: which value changes at
which record, which parity differences exist, and which run is clean.

## Conclusion

The confirmed meaning, including its limits.

## Confidence

`high`, `medium`, or `low`, with a short reason. A clean lockstep run confirms
behaviour, but does not independently assign meaning to an unnamed field.
````

Keep only the completed Markdown case and small JSON excerpts in Git. Keep RAM
dumps and HTML viewers in `/tmp`, unless a trace case explicitly justifies them
as a compact, necessary regression fixture.
