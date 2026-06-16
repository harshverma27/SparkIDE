"""
project/autosave.py — Qt-free decision of which editor buffers need writing.

The UI owns the timer and the actual disk I/O; this module only decides the
dirty set (buffers whose content differs from what is currently on disk).
"""

from __future__ import annotations

from pathlib import Path


def files_to_autosave(buffers: dict[Path, str], on_disk: dict[Path, str]) -> dict[Path, str]:
    return {path: text for path, text in buffers.items() if on_disk.get(path) != text}
