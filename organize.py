#!/usr/bin/env python3
"""organize.py — CLI entry point for Bulk File Organizer.

Scans a target directory and organizes files into sorted category folders.

Usage:
    python organize.py --path "C:\\Users\\swarnabh\\Downloads"
    python organize.py --path "C:\\Users\\swarnabh\\Downloads" --dry-run
    python organize.py --path "C:\\Users\\swarnabh\\Downloads" --config config.json --verbose
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List

from organizer.config_manager import Config, ConfigManager
from organizer.file_classifier import FileClassifier
from organizer.file_mover import ConflictAction, FileMover, MoveResult, SimpleResolver
from organizer.logger_config import setup_logger


# ───────────── Constants ─────────────


RESOLVED_PATH = os.path.expanduser("~/Downloads")
RESOLVER = SimpleResolver(Path(RESOLVED_PATH))
DEFAULT_CONFIG_PATH = Path(__file__).parent / "config.json"


# ───────────── CLI ─────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="organize.py",
        description="Bulk File Organizer — scan a directory and sort files into categories.",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=RESOLVED_PATH,
        help=f"Target directory to organize (default: {RESOLVED_PATH})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without moving any files",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to custom config.json",
    )
    parser.add_argument(
        "--conflict",
        type=str,
        choices=["skip", "overwrite", "rename"],
        default="skip",
        help='Conflict strategy: skip, overwrite, or rename (default: skip)',
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging",
    )
    parser.add_argument(
        "--exclude-files",
        type=str,
        nargs="*",
        default=[],
        help="Filenames to exclude from scanning (e.g. README.md)",
    )
    parser.add_argument(
        "--exclude-dirs",
        type=str,
        nargs="*",
        default=["__pycache__", ".git", ".venv", "venv", "node_modules"],
        help="Directory names to skip during scan",
    )
    return parser.parse_args(argv)


def get_files(target_dir: Path, exclude_files: list[str], exclude_dirs: list[str]) -> List[Path]:
    """Collect all files in *target_dir*, skipping excluded dirs/names."""
    files: List[Path] = []
    for item in target_dir.rglob("*"):
        if not item.is_file():
            continue
        if item.name in exclude_files:
            continue
        # Skip excluded directories (check all parents)
        if any(d in item.parts for d in exclude_dirs):
            continue
        files.append(item)
    return files


def organize(
    target_dir: Path,
    config: Config,
    dry_run: bool,
    conflict: str,
    logger: object,
    exclude_files: list[str],
    exclude_dirs: list[str],
) -> List[MoveResult]:
    """Main orchestration: scan → classify → move."""
    # 1. Collect files
    files = get_files(target_dir, exclude_files, exclude_dirs)
    total = len(files)
    logger.info(f"Found {total} files in {target_dir}")

    # 2. Create classifier
    resolver = SimpleResolver(target_dir)
    classifier = FileClassifier(config)

    # 3. Create mover
    conflict_action = getattr(ConflictAction, conflict.upper(), ConflictAction.SKIP)
    mover = FileMover(resolver, conflict_action=conflict_action, dry_run=dry_run)

    # 4. Process each file
    results: List[MoveResult] = []
    for file_path in files:
        category = classifier.classify(file_path)
        if not classifier.has_category(file_path.suffix):
            logger.debug(f"Skipping unmapped file: {file_path.name}")
            continue
        result = mover.move(file_path, category)
        results.append(result)

    # 5. Summary
    status_counts: dict[str, int] = {}
    for r in results:
        status_counts[r.status] = status_counts.get(r.status, 0) + 1

    prefix = "[DRY-RUN] " if dry_run else ""
    summary_parts = [f"{k}: {v}" for k, v in sorted(status_counts.items())]
    logger.info(f"{prefix}Organized: {', '.join(summary_parts)}")

    if dry_run:
        logger.info(f"{prefix}No files were actually moved.")

    return results


# ───────────── Main ─────────────


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    target = Path(args.path)

    if not target.exists():
        print(f"Error: directory '{target}' does not exist.")
        sys.exit(1)

    if not target.is_dir():
        print(f"Error: '{target}' is not a directory.")
        sys.exit(1)

    logger = setup_logger(
        name="organizer",
        verbose=args.verbose,
        log_file=Path(args.path) / "organize.log",
    )

    # Load config
    config_path = Path(args.config) if args.config else DEFAULT_CONFIG_PATH
    config_manager = ConfigManager(config_path if config_path.exists() else None)
    config = config_manager.load()

    logger.info(f"Config: {len(config.categories)} categories, conflict={args.conflict}")
    logger.info(f"Target: {target.resolve()}")

    # Dry-run
    if args.dry_run:
        logger.info("Running in DRY-RUN mode — no files will be moved.")

    # Organize
    results = organize(
        target_dir=target,
        config=config,
        dry_run=args.dry_run,
        conflict=args.conflict,
        logger=logger,
        exclude_files=args.exclude_files,
        exclude_dirs=args.exclude_dirs,
    )

    # Show results
    for r in results:
        logger.debug(f"  {r.status}: {r.src.name} → {r.dst.name} ({r.message})")


if __name__ == "__main__":
    main()
