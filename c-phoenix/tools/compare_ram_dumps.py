#!/usr/bin/env python3
"""Lockstep-vergelijking van RAM-dumps: jphoenix (referentie) vs port3 (C-port).

Beide dumps gebruiken hetzelfde formaat per frame:
    4 bytes big-endian framenummer + 3072 bytes RAM (0x4000-0x4BFF)

Gebruik:
    python3 compare_ram_dumps.py <referentie.bin> <port3.bin> [--max-frames N]
        [--offset-ref N] [--offset-port N] [--regions 4340-43FF,4B40-4BFF]

Framenummers hoeven niet gelijk te lopen (beide tellen vanaf hun eigen start);
records worden op volgorde gepaard. Met --offset-* kun je frames aan het begin
overslaan om de startmomenten uit te lijnen.

Standaard worden de schermgebieden (foreground/background) genegeerd, omdat
die pas divergeren als de variabelen al fout zijn; met --regions kies je zelf.
"""
import argparse
import struct
import sys

FRAME_HDR = 4
RAM_SIZE = 0xC00
RECORD = FRAME_HDR + RAM_SIZE
BASE = 0x4000

# Bekende symbolen uit RAMUse.md voor leesbare rapportage
SYMBOLS = {
    0x435F: "M435F(alien mv cnt)", 0x4360: "PlayerMoved", 0x4361: "BulletTriggered",
    0x4363: "ParticleExplosion", 0x4381: "Score1high", 0x4382: "Score1mid",
    0x4383: "Score1low", 0x4389: "HiScorehigh", 0x438C: "SoundControlA",
    0x438D: "SoundControlB", 0x438F: "CoinCount", 0x4390: "Player1Lives",
    0x4391: "Player2Lives", 0x4398: "Counter98hi", 0x4399: "Counter98lo",
    0x439A: "Counter9A", 0x439B: "Counter9B", 0x43A0: "IN0Current",
    0x43A1: "IN0Previous", 0x43A2: "GameOrAttract", 0x43A3: "GameAndDemoOrSplash",
    0x43A4: "GameState", 0x43A5: "CounterA5", 0x43A6: "ShieldCount",
    0x43A7: "AnimationCounter", 0x43B4: "CounterB4", 0x43B8: "LevelAndRound",
    0x43B9: "CounterB9", 0x43BA: "AliensLeft", 0x43BB: "BirdsLeft",
    0x43BE: "BonusLivesAt", 0x43C0: "PlayerState", 0x43C1: "PlayerShape",
    0x43C2: "PlayerShipX", 0x43C3: "PlayerShipY", 0x43C4: "PlayerBulletState",
    0x43C6: "PlayerBulletX", 0x43C7: "PlayerBulletY",
}


def symbol(addr):
    if addr in SYMBOLS:
        return SYMBOLS[addr]
    if 0x4000 <= addr <= 0x433F:
        return "ForegroundScreen"
    if 0x4800 <= addr <= 0x4B3F:
        return "BackgroundScreen"
    if 0x43CC <= addr <= 0x43DF:
        return f"EnemyBullet{(addr - 0x43CC) // 4}"
    if 0x4B50 <= addr <= 0x4B6F:
        return f"Alien{(addr - 0x4B50) // 2:X} mv-ptr"
    if 0x4B70 <= addr <= 0x4BAF:
        return f"Alien{(addr - 0x4B70) // 4:X} state"
    if 0x4BF0 <= addr <= 0x4BFF:
        return "Stack"
    return f"M{addr:04X}"


def read_frames(path, skip):
    frames = []
    with open(path, "rb") as f:
        data = f.read()
    n = len(data) // RECORD
    for i in range(n):
        off = i * RECORD
        num = struct.unpack_from(">I", data, off)[0]
        frames.append((num, data[off + FRAME_HDR:off + RECORD]))
    return frames[skip:]


def parse_regions(spec):
    regions = []
    for part in spec.split(","):
        lo, hi = part.split("-")
        regions.append((int(lo, 16), int(hi, 16)))
    return regions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("port")
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--offset-ref", type=int, default=0)
    ap.add_argument("--offset-port", type=int, default=0)
    ap.add_argument("--regions", default="4340-43FF,4B40-4BFF",
                    help="komma-gescheiden hex-bereiken die vergeleken worden")
    ap.add_argument("--max-diffs-per-frame", type=int, default=8)
    ap.add_argument("--stop-after", type=int, default=5,
                    help="stop na N afwijkende frames")
    ap.add_argument("--align-c98", action="store_true",
                    help="lijn frames uit op de Counter98-waarde (4398:4399) "
                         "in plaats van op recordvolgorde; absorbeert drift "
                         "door extra vblank-waits")
    args = ap.parse_args()

    ref = read_frames(args.reference, args.offset_ref)
    port = read_frames(args.port, args.offset_port)
    regions = parse_regions(args.regions)

    if args.align_c98:
        def by_c98(frames):
            m = {}
            for num, ram in frames:
                c98 = (ram[0x398] << 8) | ram[0x399]
                if c98 not in m:  # eerste record met deze tellerwaarde
                    m[c98] = (num, ram)
            return m
        rmap, pmap = by_c98(ref), by_c98(port)
        keys = sorted(set(rmap) & set(pmap))
        ref = [rmap[k] for k in keys]
        port = [pmap[k] for k in keys]
        print(f"Uitgelijnd op Counter98: {len(keys)} gemeenschappelijke "
              f"tellerwaarden ({keys[0]:04X}..{keys[-1]:04X})" if keys else
              "Geen gemeenschappelijke Counter98-waarden")

    n = min(len(ref), len(port))
    if args.max_frames:
        n = min(n, args.max_frames)
    print(f"Vergelijk {n} frames (ref: {len(ref)}, port: {len(port)}), "
          f"regio's: {args.regions}")

    bad_frames = 0
    for i in range(n):
        rnum, rdata = ref[i]
        pnum, pdata = port[i]
        diffs = []
        for lo, hi in regions:
            for addr in range(lo, hi + 1):
                a, b = rdata[addr - BASE], pdata[addr - BASE]
                if a != b:
                    diffs.append((addr, a, b))
        if diffs:
            bad_frames += 1
            print(f"\nFrame-paar {i} (ref #{rnum} / port #{pnum}): "
                  f"{len(diffs)} verschil(len)")
            for addr, a, b in diffs[:args.max_diffs_per_frame]:
                print(f"  0x{addr:04X} {symbol(addr):24s} ref=0x{a:02X} port=0x{b:02X}")
            if len(diffs) > args.max_diffs_per_frame:
                print(f"  ... en {len(diffs) - args.max_diffs_per_frame} meer")
            if bad_frames >= args.stop_after:
                print(f"\nGestopt na {bad_frames} afwijkende frames.")
                return 1
    if bad_frames == 0:
        print("Geen verschillen gevonden.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
