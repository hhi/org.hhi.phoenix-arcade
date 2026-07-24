# Phoenix Sound Port Notes

This port intentionally follows the MAME hardware-emulation route rather than
the legacy `.au` sample playback route.

## Runtime Path

- `Phoenix` writes sound control A/B through `Sound.updateControlA/B`.
- `Sound` queues control writes by sample position within the current 60 Hz
  frame, then renders in `endFrame()`.
- Events are kept sorted by sample position. Events on the same sample preserve
  CPU write order, so the last write at the same sample wins.
- `Sound` receives a `PcmSink` and has no Java Sound dependency.
- The desktop runtime injects `JavaSoundPcmSink`, which opens one mono signed
  16-bit PCM output line.
- The LibGDX runtime injects `LibGdxPcmSink`, which converts the little-endian
  byte stream to signed samples for a LibGDX `AudioDevice`.
- Headless tests and WAV generation inject `PcmSink.discarding()` or a
  purpose-built recording sink.

The old `.au` samples and legacy frontend files are stored under `legacy/`.
Automated checks live under `tests/`, while sound verification and comparison
tools live under `tools/sound/`. Runtime source no longer references
`AudioClip`, `DesktopAudioClip`, `Clip`, or sample playback.

## MAME-Aligned Sound Sources

- Discrete sound core runs at 120 kHz, matching MAME's `DISCRETE(..., 120000, ...)`.
- Output is rendered at 48 kHz, above the minimum noted by MAME's discrete
  Phoenix sound comments.
- MAME route gains are preserved:
  - discrete route: `0.6`
  - custom noise route: `0.4`
  - TMS route: `0.5`
- `MAME_DISCRETE_OUTPUT_GAIN = 40000.0` is the MAME discrete mixer gain, not an
  output sample rate.
- TMS/MM6221AA uses the MAME Phoenix base clock and decay setup.
- Discrete probe values use the same voltage units as MAME. Effect 1 nodes
  23-25 and the effect output, plus effect 2 node 32 and its effect output,
  therefore remain in their circuit-voltage domain instead of being normalized
  to 0-1.
- `DEFAULT_TTL_V_LOGIC_1` is 3.4 V in MAME. Effect 1 node 23 and effect 2
  node 32 use 3.4 V (or 1.7 V for the divided effect 2 level), not the 5 V
  supply voltage.
- Discrete resistor/capacitor values and node state use `double`, matching
  MAME's discrete core.
- MAME's autonomous 555 reset performs one discrete-rate step. Effect 2 nodes
  33 and 34 are primed by that same step before Java renders its first sample.
  The CV-controlled 555s remain unadvanced because their reset control voltage
  is below MAME's 0.25 V cutoff.
- The custom-noise 18-bit polynomial uses unsigned 32-bit right shifts, as in
  MAME's `uint32_t` implementation.
- Both non-48 kHz sources use MAME's default LoFi four-sample cubic resampler
  and 24-bit phase: 23.808 kHz MM6221AA is upsampled and the 120 kHz discrete
  graph is downsampled with MAME's `source_divide` moving average. The port no
  longer uses zero-order sample hold for TMS or simple 2/3-step averaging for
  the discrete graph.

## Verification Commands

Compile and run the deterministic sound checks:

```bash
make verify
```

Generate all comparison artifacts, including isolated WAVs and Java-side
discrete-node CSVs:

```bash
make artifacts
```

Generate only isolated headless WAVs, or a custom Java-side discrete-node CSV
for MAME `WAVELOG` comparison:

```bash
java -cp build/test-classes SoundRenderDump
java -cp build/test-classes SoundNodeDump
java -cp build/test-classes SoundNodeDump sound-renders/nodes_effect1.csv 0x0f 0x18 60000
java -cp build/test-classes SoundNodeCsvCompare sound-renders/nodes_effect2_bird_hit.csv mame-nodes-effect2.csv
java -cp build/test-classes SoundNodeCsvCompare sound-renders/nodes_effect2_bird_hit.csv mame-nodes-effect2.csv 0.001 0.0001
```

The WAVs are written to `sound-renders/`:

- `effect2_bird_hit.wav`
- `effect1_shield_explosion.wav`
- `effect1_filtered.wav`
- `noise_control.wav`
- `music_tune.wav`

`SoundRenderDump` also prints duration, peak, RMS, and clipping counts. These
metrics are not a substitute for listening, but they make regressions and
MAME/PCB comparisons more objective. The same values are written to
`sound-renders/metrics.csv` for repeatable comparisons between runs.

`SoundNodeDump` writes Java-side equivalents of the MAME discrete nodes to CSV:
effect 1 nodes 20-25, effect 2 nodes 30-40 that are present in the MAME graph,
the final effect outputs, and final discrete mixer node 90. It is intended for
node-level comparison against MAME debug/WAVELOG captures, not for balance
tuning.

`SoundNodeCsvCompare` compares a Java node CSV with a MAME/reference node CSV
that uses the same column names. It reports per-node sample count, maximum
absolute difference, and RMS difference so mismatches can be traced to a node
before any code change. Optional max-absolute and RMS tolerances make the
comparison fail when a node exceeds the accepted difference. The comparison also
fails when the reference CSV is missing any Java-side node column, or when the
two files have no comparable node columns. This is intentional: a MAME
comparison should fail loudly if the capture does not represent the same nodes.
Native MAME `DISCRETE_CSVLOG` headers and names such as `NODE_33` are accepted
and normalized to the Java column name `node33`.

`SoundArtifactDump` runs the standard WAV render set and writes the standard
node CSV set for effect 2, effect 1, filtered effect 1, and mixed effect
scenarios. It also writes `sound-renders/manifest.csv` with file sizes and CRC32
checksums for the complete comparison set.

## Direct MAME Comparison

MAME 0.288 can capture the actual Phoenix sound writes and all three native
sound-device streams with `tools/sound/mame-phoenix-sound-trace.lua`. Set:

- `PHOENIX_SOUND_TRACE` to the latch-event CSV path,
- `PHOENIX_SOUND_RAW_DIR` to a directory for `discrete.f32`, `custom.f32`,
  `tms.f32`, and their manifest,
- optionally `PHOENIX_SOUND_FIXTURE=1` to force deterministic effect2,
  effect1, filtered effect1, noise, tune 2, and tune 3 intervals.

Replay and compare the exact MAME event timeline with:

```bash
java -cp build/test-classes SoundMameTraceReplay mame-events.csv java-mix.wav 24
java -cp build/test-classes SoundMameRawTraceReplay mame-events.csv java-raw 24
java -cp build/test-classes SoundMameNodeTraceReplay mame-events.csv java-nodes.csv 3
java -cp build/test-classes SoundWavCompare java-mix.wav mame-mix.wav 64
java -cp build/test-classes SoundFloatCompare java-raw/discrete.f32 mame-raw/discrete.f32 64
java -cp build/test-classes SoundFloatCompare java-raw/custom.f32 mame-raw/custom.f32 16
java -cp build/test-classes SoundFloatCompare java-raw/tms.f32 mame-raw/tms.f32 16
java -cp build/test-classes SoundNodeCsvCompare mame-discrete_0.csv java-nodes.csv
java -cp build/test-classes SoundNodeCsvCompare mame-discrete_1.csv java-nodes.csv
```

Measured against the local MAME 0.288 fixture:

- MM6221AA/TMS raw: correlation `1.0`, gain `1.0`, one capture sample offset.
- Custom-noise startup: correlation `0.999999978`, gain `0.999953596`.
- Effect 1: correlation `0.987200205`, gain `1.001368358`.
- Filtered effect 1: correlation `0.994318959`, gain `1.000241726`.
- Effect 2 over the complete two-second fixture interval: correlation `1.0`,
  gain `1.0`, lag `0`, and raw RMS difference `0.0`.
- Instrumented MAME nodes 33-40 match over 360,002 CSV rows with maximum
  absolute differences below `5e-7`, the six-decimal output precision of
  MAME's CSV logger.

The former long-window phase mismatch was in the offline trace replay, not in
the runtime synthesizer. MAME renders the stream through the write timestamp
with the old latch and applies the write to the following discrete sample. The
replay previously activated it one sample too early. At NODE_33, changing from
the 0.01 uF base capacitor to the 1.01 uF selection magnified that one-sample
boundary error into roughly 100 samples of later phase shift.

## Current Test Coverage

`SoundRenderSmokeTest` verifies:

- frame size at 48 kHz / 60 Hz,
- effect1, effect2, noise, and music paths produce non-silent PCM,
- rendered paths do not clip,
- mid-frame and late-frame events do not leak earlier in the frame,
- multiple writes in one frame are applied in chronological order,
- same-sample writes preserve write order,
- out-of-order queued events render chronologically.

`SoundNodeProbeTest` verifies that the Java-side MAME node probe produces finite
effect 1, effect 2, mixed, and final node-90 values across the exposed MAME node
chain.

`SoundNodeCsvCompareTest` verifies the node CSV comparison math used for
MAME/reference comparisons, including strict failures for missing or empty node
column matches.

`SoundNodeDumpRegressionTest` verifies the Java-side MAME node CSV format and
deterministic CRCs for effect 2, effect 1, filtered effect 1, and mixed
effect1/effect2 dumps, keeping the comparison artifacts stable for future MAME
`WAVELOG` checks.

`SoundArtifactManifestTest` verifies the complete generated artifact manifest,
including WAV metrics, WAV files, node CSV files, sizes, and CRC32 checksums.

`SoundSourceAuditTest` verifies that Java runtime source does not reintroduce
the legacy `.au`/`AudioClip` sample path or experimental effect tuning
properties. It also keeps `Sound` independent of Java Sound.

`PcmSinkTest` verifies that one 60 Hz sound frame is delivered as 1600 bytes of
48 kHz signed 16-bit mono PCM and that `Sound.stop()` closes the injected sink.

`SoundMameAlignmentTest` verifies the MAME route gains, sound sample rates,
Phoenix discrete component values, and MM6221AA/TMS timing constants used by the
Java implementation.

`SoundMameTraceabilityTest` verifies that Java source still exposes named
counterparts for the key MAME Phoenix discrete nodes and MM6221AA constants,
making future MAME source comparisons mechanical instead of guesswork.

`SoundMameLofiResamplerTest` verifies MAME's 24-bit resample phase, cubic
interpolation table anchors, the exact 23.808-to-48 kHz TMS phase step, the
120-to-48 kHz discrete phase step and `source_divide=3`, plus runtime wiring for
both sources.

`SoundNoisePolynomialTest` regenerates MAME's complete 18-bit custom-noise
polynomial and compares every packed 32-bit word against the runtime table.

`SoundControlMappingTest` verifies the control A/B bit mapping from MAME:
effect 2 data/frequency, custom noise controls, effect 1 data/frequency/filter,
and MM6221AA tune select.

`SoundMetricsRegressionTest` verifies fixed peak, RMS, and clipping metrics for
the isolated render cases generated by `SoundRenderDump`.

`SoundControlMatrixRegressionTest` renders a broader MAME control-latch matrix:
all effect 2 data/frequency combinations, all effect 1 data/frequency/filter
combinations, all noise enable combinations, and all MM6221AA tune selects. It
stores deterministic CRCs for those rendered PCM matrices so future changes
cannot silently alter the MAME-mapped control space.

`SoundVerificationTest` runs all sound audit, MAME alignment, mapping,
traceability, node comparison, artifact, metrics, control-matrix, and
verification-coverage checks in one command. `SoundVerificationCoverageTest`
fails if a `Sound*Test.java` file is added without being wired into the runner.

## Direct MAME Status

Direct MAME comparison is now reproducible and has identified and fixed the
5.0-versus-3.4 V TTL error, signed-versus-unsigned LFSR shift, component
precision, autonomous-555 reset state, and the trace-replay sample boundary.
TMS is sample-identical after alignment, custom noise is effectively identical,
and the discrete effect-2 stream is sample-identical. No pitch or gain
compensation is applied. A PCB recording remains useful as final perceptual
confirmation of MAME's analog model, but there is no remaining numerical
effect-2 gap between Java and MAME.

The repository contains the concatenated `program.rom` and `graphics.rom` plus
MAME's two 256-byte `mmi6301` color PROM dumps. All twelve 2 KiB program and
character segments and both PROMs match the official MAME `phoenix` SHA-1
values. The color PROMs do not participate in the sound circuit.
