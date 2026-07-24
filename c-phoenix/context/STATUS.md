# C-Phoenix status

Dutch version: [STATUS.nl.md](STATUS.nl.md).

## Current state

C-Phoenix is functionally complete. It has been verified against the Java
reference emulator through the attract cycle, active gameplay, a mothership
kill and the following round, and two-player bank switching. The project also
includes sound and MAME-accurate colours.

The final scripted-lockstep batch reports 57 of 57 scenarios clean. The shared
C game core has no direct or indirect program-ROM reads: its 50 catalogued data
regions are represented by named, tested tables in `phoenix_tables.c`.

## Open observations

This is a gameplay observation, not a confirmed defect.

1. **Brief music stutter at the start of a round.** Input can already respond
   while the music begins but the ship and birds are not yet visible. During
   that phase, the music can stutter briefly. This still needs a reproducible
   recording and a comparison with the Java emulator.

## Verified scope

- 57 scripted scenarios are record-for-record clean for game state.
- 176 functions have ground-truth verification through byte-exact runs; 38
  have partial coverage from dispatch or hardware-configuration branches.
- Three ROM routines are known dead code: `l00b6`, `l0e02_unused`, and
  `unused_bcd_subtracter`.
- The old duplicate stubs were removed after mapping each ROM range to its
  living implementation.

See [mapping/c_functions_by_address.md](mapping/c_functions_by_address.md) for
the function-level mapping and
[mapping/lockstep_verified.json](mapping/lockstep_verified.json) for the
machine-readable verification data.

## Repeating verification

Use [tools/lockstep/PROCEDURE.md](../tools/lockstep/PROCEDURE.md) for the
repeatable lockstep workflow. Scripted comparisons require jphoenix's
`-Dphoenix.inputclock=poll` option. Compare the `4000-4BE5` region; bytes above
that are Z80 stack residue that C-Phoenix does not reproduce by design.
