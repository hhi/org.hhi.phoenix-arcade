"""Canonical lockstep comparison criteria shared by batch tooling."""

# RAM offsets relative to $4000 that carry machine-local or display noise.
NOISE_OFFSETS = {0x388, 0x389, 0x38A, 0x38B, 0x38C, 0x38D, 0x161, 0x181}

# Initialisation can cross a dump boundary differently in the two runtimes.
GAME_START_RECORD_START = 40
GAME_START_RECORD_END = 60

# A one-record game-state mismatch that immediately re-synchronises is known
# dump-phase noise. Two consecutive records indicate a real state divergence.
MAX_TRANSIENT_STATE_RECORDS = 1

# Screen RAM may lag gameplay state at a dump boundary. Longer runs are dirty.
MAX_TRANSIENT_SCREEN_RECORDS = 8


def is_game_start_record(record_index: int) -> bool:
    return GAME_START_RECORD_START <= record_index <= GAME_START_RECORD_END


def is_screen_offset(offset: int) -> bool:
    """Return whether an offset belongs to foreground or background screen RAM."""
    return offset < 0x340 or 0x800 <= offset < 0xB40

