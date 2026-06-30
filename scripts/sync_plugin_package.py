#!/usr/bin/env python3
"""Synchronize the marketplace-installable plugin package copy."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "plugins" / "humanizer-kr"
SYNC_PATHS = [
    ".codex-plugin",
    ".claude-plugin/plugin.json",
    "skills",
    "LICENSE",
    "README.md",
]


def copy_path(relative: str) -> None:
    source = ROOT / relative
    target = PACKAGE_ROOT / relative
    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def main() -> None:
    if PACKAGE_ROOT.exists():
        shutil.rmtree(PACKAGE_ROOT)
    PACKAGE_ROOT.mkdir(parents=True, exist_ok=True)
    for relative in SYNC_PATHS:
        copy_path(relative)
    print(f"Synced plugin package: {PACKAGE_ROOT}")


if __name__ == "__main__":
    main()
