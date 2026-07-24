#!/usr/bin/env python3
"""Copy architecture markdown artifacts into the repository layout."""

import argparse
import re
from pathlib import Path


ARTIFACTS = (
    ("c_files_categorization.md", "context"),
    ("callgraph_artifact.md", "context/graphs"),
    ("file_callgraph_artifact.md", "context/graphs"),
    ("func_prefix_callgraph_artifact.md", "context/graphs"),
    ("rom_bank_callgraph_artifact.md", "context/graphs"),
    ("cross_domain_callgraph_artifact.md", "context/graphs"),
    ("internal_domain_callgraph_artifact.md", "context/graphs"),
    ("execution_tree_callgraph_artifact.md", "context/graphs"),
    ("coverage_callgraph_artifact.md", "context/graphs"),
    ("stub_hunter_callgraph_artifact.md", "context/graphs"),
)


def migrate(source_dir, project_root):
    for filename, destination in ARTIFACTS:
        source = source_dir / filename
        if not source.exists():
            continue

        content = source.read_text(encoding="utf-8")
        content = re.sub(
            r"!\[(.*?)\]\([^)]*/([^/]+\.svg)\)",
            r"![\1](./\2)",
            content,
        )
        content = re.sub(r"\(file://[^)]*/c-phoenix/(.*?)\)", r"(../../\1)", content)

        target_dir = project_root / destination
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / filename.replace("_artifact", "")
        target.write_text(content, encoding="utf-8")
        print(f"Migrated {source} to {target}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (default: inferred from this script)",
    )
    args = parser.parse_args()
    migrate(args.source_dir, args.project_root)


if __name__ == "__main__":
    main()
