#!/usr/bin/env python3
"""Validate and assemble the Phoenix ROM set from physical chip dumps.

Reads a byte-free manifest (see roms/phoenix-amstar/rom-set.json) describing
each physical chip's expected size and SHA-256, and each assembled image's
expected size and SHA-256. Never embeds or prints ROM bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

DEFAULT_MANIFEST = Path(__file__).resolve().parent.parent / "roms" / "phoenix-amstar" / "rom-set.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest(manifest_path: Path) -> dict:
    with manifest_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def expected_chips_by_hash(manifest: dict) -> dict[str, dict]:
    """Return the canonical chip metadata keyed by its content hash."""
    expected: dict[str, dict] = {}
    for image in manifest["images"]:
        for chip in image["chips"]:
            previous = expected.setdefault(chip["sha256"], chip)
            if previous["file"] != chip["file"]:
                raise ValueError(
                    "manifest contains the same chip hash under two filenames: "
                    f"{previous['file']} and {chip['file']}"
                )
    return expected


def normalize_chip_names(manifest: dict, rom_dir: Path) -> int:
    """Rename uniquely identified chip files to their manifest filenames.

    Content is the authority: an arbitrary supplied filename is accepted only
    when both its size and SHA-256 identify one expected physical chip. Unknown
    files, wrong revisions, and duplicate canonical chips are left untouched.
    """
    expected = expected_chips_by_hash(manifest)
    renamed = 0
    for candidate in sorted(rom_dir.iterdir()):
        if not candidate.is_file():
            continue
        size = candidate.stat().st_size
        digest = sha256_file(candidate)
        chip = expected.get(digest)
        if chip is None or size != chip["size"]:
            continue
        destination = rom_dir / chip["file"]
        if candidate == destination:
            continue
        if destination.exists():
            if sha256_file(destination) == digest:
                print(f"  keep {candidate.name}: canonical {destination.name} already exists")
            else:
                print(f"  skip {candidate.name}: canonical name {destination.name} is occupied")
            continue
        candidate.rename(destination)
        renamed += 1
        print(f"  rename {candidate.name} -> {destination.name} (SHA-256 match)")
    return renamed


def create_set_archive(manifest: dict, rom_dir: Path, archive_name: str) -> Path | None:
    """Create a canonical local archive only after all chip files validate."""
    archive_path = rom_dir / archive_name
    if archive_path.exists():
        print(f"  keep archive {archive_path}")
        return None
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
        for image in manifest["images"]:
            for chip in sorted(image["chips"], key=lambda item: item["offset"]):
                archive.write(rom_dir / chip["file"], arcname=chip["file"])
    print(f"  archive {archive_path}")
    return archive_path


def check_chips(manifest: dict, rom_dir: Path) -> list[str]:
    """Validate every physical chip dump against the manifest. Returns problems."""
    problems = []
    for image in manifest["images"]:
        for chip in image["chips"]:
            chip_path = rom_dir / chip["file"]
            label = f"{image['name']}/{chip['file']}"
            if not chip_path.is_file():
                problems.append(f"{label}: missing file {chip_path}")
                continue
            actual_size = chip_path.stat().st_size
            if actual_size != chip["size"]:
                problems.append(
                    f"{label}: size {actual_size} bytes, expected {chip['size']} bytes"
                )
                continue
            actual_sha256 = sha256_file(chip_path)
            if actual_sha256 != chip["sha256"]:
                problems.append(
                    f"{label}: sha256 {actual_sha256}, expected {chip['sha256']}"
                )
            else:
                print(f"  ok   {label} ({chip['size']} bytes)")
    return problems


def assemble_image(image: dict, rom_dir: Path) -> bytes:
    chips = sorted(image["chips"], key=lambda chip: chip["offset"])
    expected_offset = 0
    pieces = []
    for chip in chips:
        if chip["offset"] != expected_offset:
            raise ValueError(
                f"{image['name']}: gap or overlap before {chip['file']} "
                f"(expected offset {expected_offset}, got {chip['offset']})"
            )
        pieces.append((rom_dir / chip["file"]).read_bytes())
        expected_offset += chip["size"]
    return b"".join(pieces)


def cmd_check(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    rom_dir = Path(args.rom_dir).resolve()
    if not rom_dir.is_dir():
        print(f"ROM_DIR not found: {rom_dir}", file=sys.stderr)
        return 2
    print(f"Checking chip dumps in {rom_dir} against {args.manifest.name}")
    problems = check_chips(manifest, rom_dir)
    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    total_chips = sum(len(image["chips"]) for image in manifest["images"])
    print(f"\nAll {total_chips} chip dumps match the manifest.")
    return 0


def cmd_normalize(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    rom_dir = Path(args.rom_dir).resolve()
    if not rom_dir.is_dir():
        print(f"ROM_DIR not found: {rom_dir}", file=sys.stderr)
        return 2
    print(f"Matching chip dumps in {rom_dir} by SHA-256")
    renamed = normalize_chip_names(manifest, rom_dir)
    problems = check_chips(manifest, rom_dir)
    if problems:
        print(f"\n{len(problems)} problem(s); no archive created:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"\nAll chip dumps match after {renamed} rename(s).")
    create_set_archive(manifest, rom_dir, args.archive_name)
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    rom_dir = Path(args.rom_dir).resolve()
    if not rom_dir.is_dir():
        print(f"ROM_DIR not found: {rom_dir}", file=sys.stderr)
        return 2

    print(f"Matching chip dumps in {rom_dir} by SHA-256")
    renamed = normalize_chip_names(manifest, rom_dir)
    print(f"Checking chip dumps in {rom_dir} against {args.manifest.name}")
    problems = check_chips(manifest, rom_dir)
    if problems:
        print(f"\n{len(problems)} problem(s), aborting build:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    if renamed:
        print(f"\nRenamed {renamed} chip dump(s) to canonical manifest names.")
    create_set_archive(manifest, rom_dir, args.archive_name)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nAssembling {len(manifest['images'])} image(s) into {output_dir}")
    for image in manifest["images"]:
        try:
            assembled = assemble_image(image, rom_dir)
        except ValueError as error:
            print(f"  FAIL {image['name']}: {error}", file=sys.stderr)
            return 1
        if len(assembled) != image["size"]:
            print(
                f"  FAIL {image['name']}: assembled {len(assembled)} bytes, "
                f"expected {image['size']} bytes",
                file=sys.stderr,
            )
            return 1
        actual_sha256 = sha256_bytes(assembled)
        if actual_sha256 != image["sha256"]:
            print(
                f"  FAIL {image['name']}: assembled sha256 {actual_sha256}, "
                f"expected {image['sha256']}",
                file=sys.stderr,
            )
            return 1
        output_path = output_dir / image["output"]
        output_path.write_bytes(assembled)
        print(f"  ok   {image['name']} -> {output_path} ({len(assembled)} bytes)")

    print("\nAll images assembled and verified.")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"Path to a rom-set.json manifest (default: {DEFAULT_MANIFEST})",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Validate chip dumps against the manifest")
    check_parser.add_argument("--rom-dir", required=True, help="Directory containing chip dump files")
    check_parser.set_defaults(func=cmd_check)

    normalize_parser = subparsers.add_parser(
        "normalize",
        help="Identify chip dumps by SHA-256, rename matches, and create a canonical ZIP",
    )
    normalize_parser.add_argument("--rom-dir", required=True, help="Directory containing chip dump files")
    normalize_parser.add_argument(
        "--archive-name",
        default="phoenix_amstar-set1.zip",
        help="Local ZIP filename to create after a complete match",
    )
    normalize_parser.set_defaults(func=cmd_normalize)

    build_parser = subparsers.add_parser("build", help="Assemble chip dumps into ROM images")
    build_parser.add_argument("--rom-dir", required=True, help="Directory containing chip dump files")
    build_parser.add_argument(
        "--output-dir", required=True, help="Directory to write assembled .rom images into"
    )
    build_parser.add_argument(
        "--archive-name",
        default="phoenix_amstar-set1.zip",
        help="Local ZIP filename to create after a complete match",
    )
    build_parser.set_defaults(func=cmd_build)

    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
