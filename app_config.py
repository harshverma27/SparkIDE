"""
app_config.py — central application configuration.

Single source of truth for version, identity, key filesystem paths, and window
defaults. Importing this module has no side effects (no Qt imports), so it is
safe to use from tests and tooling.
"""

import os
from pathlib import Path

# ── Identity ──────────────────────────────────────────────────────────────────
APP_NAME = "SparkIDE"
APP_ORG = "SparkIDE"
APP_VERSION = "1.1.0"
APP_TAGLINE = "Visual Arduino programming for Linux."
REPO_URL = "https://github.com/harshverma27/SparkIDE"

# ── Filesystem paths ──────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent
BLOCKLY_HTML = ROOT_DIR / "blockly" / "index.html"
BUILD_DIR = ROOT_DIR / "build" / "sparkide_sketch"
SKETCH_FILE = BUILD_DIR / "sparkide_sketch.ino"


# ── User config dir (recent projects, settings) ───────────────────────────────
def _user_config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / APP_NAME


USER_CONFIG_DIR = _user_config_dir()

# ── Window defaults ───────────────────────────────────────────────────────────
WINDOW_MIN_SIZE = (1100, 680)
WINDOW_DEFAULT_SIZE = (1360, 800)


def version_label() -> str:
    """Short, human-facing version string, e.g. 'SparkIDE v1.0.0'."""
    return f"{APP_NAME} v{APP_VERSION}"
