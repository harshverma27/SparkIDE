"""
project/recent.py — Qt-free persistence of the recent-projects MRU list.

Stored as a JSON list of folder paths under the user config dir. Most-recent
first, deduped, capped, and pruned of folders that no longer exist on load.
"""

from __future__ import annotations

import json
from pathlib import Path

from app_config import USER_CONFIG_DIR

_MAX = 10


def recent_store_path() -> Path:
    return USER_CONFIG_DIR / "recent_projects.json"


def load_recent() -> list[Path]:
    store = recent_store_path()
    try:
        raw = json.loads(store.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out: list[Path] = []
    for item in raw:
        p = Path(item)
        if p.exists() and p not in out:
            out.append(p)
    return out[:_MAX]


def _write(paths: list[Path]) -> None:
    store = recent_store_path()
    store.parent.mkdir(parents=True, exist_ok=True)
    store.write_text(json.dumps([str(p) for p in paths]), encoding="utf-8")


def add_recent(path: Path) -> list[Path]:
    path = Path(path)
    current = [p for p in load_recent() if p != path]
    updated = [path, *current][:_MAX]
    _write(updated)
    return updated


def clear_recent() -> None:
    _write([])
