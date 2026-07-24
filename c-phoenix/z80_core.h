#ifndef Z80_CORE_H
#define Z80_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include "phoenix_state.h"
#include "phoenix_hw.h"

/*
 * Central Z80 address-space decoder: the sole path for all memory and
 * memory-mapped I/O access, replacing the raw `(uint8_t*)&state +
 * offset` pointer arithmetic previously scattered across the codebase.
 * An address that's ever computed wrong (an 8-bit wraparound, a stale
 * pointer, an off-by-one) now reads as 0 / writes as a no-op instead of
 * silently corrupting adjacent PhoenixState fields or reading past
 * prg_mem's bounds.
 *
 * Real hardware map (see context/RAMUse.md and phoenix_hw.h):
 *   $0000-$3FFF  ROM (read-only)
 *   $4000-$4BFF  RAM (PhoenixState)
 *   $5000        video register (write)
 *   $5800        scroll register (write)
 *   $6000        sound A (write)
 *   $6800        sound B (write)
 *   $7000        inputs / IN0 (read)
 *   $7800        DIP switches (read)
 * Each port is aliased across a $400 range on real hardware (only the
 * high bits are decoded), matched here for parity with mem_write's
 * existing port ranges.
 */
extern PhoenixState state;
extern const uint8_t prg_mem[0x4000];

static inline uint8_t mem_read(uint16_t addr) {
    if (addr < 0x4000) {
        return prg_mem[addr];
    } else if (addr < 0x4C00) {
        uint8_t* ram = (uint8_t*)&state;
        return ram[addr - 0x4000];
    } else if (addr >= 0x7000 && addr < 0x7400) {
        return hw_read_inputs();
    } else if (addr >= 0x7800 && addr < 0x7C00) {
        return hw_read_dsw();
    }
    return 0;
}

static inline void mem_write(uint16_t addr, uint8_t val) {
    if (addr >= 0x4000 && addr < 0x4C00) {
        uint8_t* ram = (uint8_t*)&state;
        ram[addr - 0x4000] = val;
    } else if (addr >= 0x5000 && addr < 0x5400) {
        hw_write_video_register(val);
    } else if (addr >= 0x5800 && addr < 0x5C00) {
        hw_write_scroll_register(val);
    } else if (addr >= 0x6000 && addr < 0x6400) {
        hw_write_sound_a(val);
    } else if (addr >= 0x6800 && addr < 0x6C00) {
        hw_write_sound_b(val);
    }
}

#endif // Z80_CORE_H
