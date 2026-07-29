#!/usr/bin/env python3
"""Validate the Phoenix annotated documentation without modifying it.

The validator deliberately checks only facts that can be derived from this
checkout: local Markdown targets, the number of SVG assets, linked C function
names, and the ROM address/step-count metadata repeated in the pattern SVGs.

Usage:
    python3 tools/validate_documentation.py
    python3 tools/validate_documentation.py --root c-phoenix
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlparse


MARKDOWN_LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)(?:\s+[^)]*)?\)")
SVG_COUNT_RE = re.compile(r"\b(\d+)\s+(?:individuele\s+)?SVG-(?:animaties|bestanden|patroonbestanden)\b", re.I)
FUNCTION_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
SVG_PATTERN_RE = re.compile(
    r"Cluster ([AB]) (?:Patroon|Pattern) (\d+) \(ROM \$([0-9A-F]+), (\d+) (?:Stappen|Steps)\)"
)
DOC_PATTERN_RE = re.compile(
    r"Patroon (\d+) \(ROM \$([0-9A-F]+), (\d+)b\s+—"
)
IGNORED_SCHEMES = {"http", "https", "mailto", "data"}


def local_target(raw_target: str) -> str | None:
    target = raw_target.strip("<>")
    parsed = urlparse(target)
    if target.startswith("#") or parsed.scheme in IGNORED_SCHEMES or parsed.scheme:
        return None
    return unquote(parsed.path)


def c_function_names(source: Path) -> set[str]:
    """Return function-like names from a C source, excluding call sites.

    The C port uses uncomplicated top-level declarations and definitions. A
    line with an opening brace after the parameter list captures definitions;
    the fallback covers declarations in the few source files that document an
    extern function link instead of its implementation.
    """
    names: set[str] = set()
    definition_re = re.compile(
        r"^\s*(?:static\s+)?(?:[A-Za-z_]\w*\s+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{",
        re.M,
    )
    declaration_re = re.compile(
        r"^\s*(?:extern\s+)?(?:[A-Za-z_]\w*\s+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*;",
        re.M,
    )
    text = source.read_text(encoding="utf-8")
    names.update(definition_re.findall(text))
    names.update(declaration_re.findall(text))
    return names


def validate_markdown_links(root: Path, documents: list[Path]) -> list[str]:
    problems: list[str] = []
    for document in documents:
        text = document.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            target = local_target(match.group(2))
            if target is None:
                continue
            resolved = (document.parent / target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                problems.append(f"{document.relative_to(root)}: link escapes root: {target}")
            else:
                if not resolved.exists():
                    problems.append(f"{document.relative_to(root)}: missing link target: {target}")
    return problems


def validate_c_function_links(root: Path, documents: list[Path]) -> list[str]:
    problems: list[str] = []
    cache: dict[Path, set[str]] = {}
    for document in documents:
        text = document.read_text(encoding="utf-8")
        for label, raw_target in MARKDOWN_LINK_RE.findall(text):
            if not re.fullmatch(r"[A-Za-z_]\w*", label):
                continue
            target = local_target(raw_target)
            if target is None or not target.endswith(".c"):
                continue
            source = (document.parent / target).resolve()
            if not source.is_file():
                continue  # Reported by the local-link validation.
            names = cache.setdefault(source, c_function_names(source))
            if label not in names:
                problems.append(
                    f"{document.relative_to(root)}: `{label}` is not declared or defined in "
                    f"{source.relative_to(root)}"
                )
    return problems


import xml.etree.ElementTree as ET


def validate_svg_xml_syntax(root: Path) -> list[str]:
    problems: list[str] = []
    for svg in sorted((root / "animations").rglob("*.svg")) + sorted((root / "c-annotated").rglob("*.svg")):
        try:
            ET.parse(svg)
        except Exception as err:
            problems.append(f"{svg.relative_to(root)}: XML parse error: {err}")
    return problems


def validate_svg_count(root: Path) -> list[str]:
    animation_root = root / "animations"
    readme = animation_root / "nl" / "README.md"
    if not readme.is_file():
        readme = animation_root / "README.md"
    if not readme.is_file():
        return ["animations/nl/README.md: missing"]
    actual = len(list(animation_root.rglob("*.svg")))
    stated = [int(value) for value in SVG_COUNT_RE.findall(readme.read_text(encoding="utf-8"))]
    if not stated:
        return ["animations/nl/README.md: no SVG asset count found"]
    return [
        f"animations/nl/README.md: states {value} SVG assets, found {actual}"
        for value in stated
        if value != actual
    ]


def validate_pattern_metadata(root: Path) -> list[str]:
    animations = root / "animations"
    trajectory = animations / "nl" / "animation-trajectory.md"
    if not trajectory.is_file():
        trajectory = animations / "animation-trajectory.md"
    if not trajectory.is_file():
        return ["animations/nl/animation-trajectory.md: missing"]

    documented = {
        int(number): (address, int(steps))
        for number, address, steps in DOC_PATTERN_RE.findall(trajectory.read_text(encoding="utf-8"))
    }
    problems: list[str] = []
    svg_patterns: dict[int, tuple[str, int, Path]] = {}
    for svg in sorted(animations.glob("cluster_*/*.svg")):
        match = SVG_PATTERN_RE.search(svg.read_text(encoding="utf-8"))
        if not match:
            problems.append(f"{svg.relative_to(root)}: missing pattern title metadata")
            continue
        _, number, address, steps = match.groups()
        svg_patterns[int(number)] = (address, int(steps), svg)

    for number, (address, steps) in sorted(documented.items()):
        actual = svg_patterns.get(number)
        if actual is None:
            problems.append(f"animation-trajectory.md: pattern {number:02d} has no SVG metadata")
        elif actual[:2] != (address, steps):
            problems.append(
                f"pattern {number:02d}: Markdown says ${address}, {steps} steps; "
                f"{actual[2].relative_to(root)} says ${actual[0]}, {actual[1]} steps"
            )
    for number, (_, _, svg) in sorted(svg_patterns.items()):
        if number not in documented:
            problems.append(f"{svg.relative_to(root)}: no matching pattern entry in animation-trajectory.md")
    return problems


def validate_english_locale_quality(root: Path, documents: list[Path]) -> list[str]:
    """Ensure documents under en/ subdirectories contain zero residual Dutch words."""
    dutch_words_regex = re.compile(
        r"\b(het|een|van|met|wordt|functie|Werking|Overzicht|Inhoudsopgave|Aangeroepen|Aanroepen|Beschrijving|Stap|Gesloten|Lus|Patroon|Patronen|Vogel|Vogels|Gedeelde|Moederschip|Scherm|tegel|spelerschip|vijandelijke|bommen|kogels|botsingen|treffer|buiten|binnen|formatie|punten|toegekend)\b"
    )
    problems: list[str] = []
    for doc in documents:
        rel_path = doc.relative_to(root).as_posix()
        if "/en/" not in f"/{rel_path}":
            continue
        text = doc.read_text(encoding="utf-8")
        matches = set(dutch_words_regex.findall(text))
        if matches:
            problems.append(
                f"{rel_path}: English locale document contains residual Dutch words: {', '.join(sorted(matches))}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("c-phoenix"), help="Phoenix source root")
    args = parser.parse_args()
    root = args.root.resolve()
    documents = sorted((root / "c-annotated").rglob("*.md")) + sorted((root / "animations").rglob("*.md"))
    if not documents:
        raise SystemExit(f"No documentation found below {root}")

    problems = []
    problems.extend(validate_svg_xml_syntax(root))
    problems.extend(validate_markdown_links(root, documents))
    problems.extend(validate_c_function_links(root, documents))
    problems.extend(validate_svg_count(root))
    problems.extend(validate_pattern_metadata(root))
    problems.extend(validate_english_locale_quality(root, documents))
    if problems:
        print("Documentation validation failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print(f"Documentation validation: OK ({len(documents)} Markdown files, {len(list((root / 'animations').rglob('*.svg')))} SVG assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
