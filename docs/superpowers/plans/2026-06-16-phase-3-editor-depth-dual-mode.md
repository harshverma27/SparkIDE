# Phase 3 — Editor Depth & Dual-Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a QScintilla-based editable code mode, folder-based multi-file Arduino projects (tabs + autosave + recent), and a block-authoritative block↔code model, while keeping the v1.1.0 block-only workflow fully intact.

**Architecture:** Pure, Qt-free project logic lives in a new `project/` package (model, recent store, autosave decision) covered by pytest. A new `ui/editor/` package wraps `QsciScintilla` into a themed `CodeEditor` and an `EditorTabs` host (read-only "Generated" tab + editable companion-file tabs) that replaces the old `ui/code_panel.py`. `MainWindow` owns project lifecycle, an autosave `QTimer`, and points `ArduinoJobWorker` at the project folder when one is open.

**Tech Stack:** Python 3, PyQt6, `PyQt6-QScintilla` (`QsciScintilla`, `QsciLexerCPP`), pytest (offscreen Qt), existing `cli/` + `arduino-cli`.

**Spec:** `docs/superpowers/specs/2026-06-16-phase-3-editor-depth-dual-mode-design.md`

**Conventions:** Run tests with `.venv/bin/python -m pytest <path> -v`. Run all tests with `make test`. Lint with `make lint`. Commit messages use `feat:`/`test:`/`docs:`/`refactor:` prefixes and end with the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer. Qt tests must run headless — set `QT_QPA_PLATFORM=offscreen` (the existing suite already relies on this via conftest/CI; pass it explicitly when running a single Qt test, e.g. `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_code_editor.py -v`).

---

## File Structure

**New (Qt-free, `project/`):**
- `project/__init__.py` — package marker.
- `project/model.py` — `ProjectFile`, `Project`, `create_project`, `open_project`, `is_sketch_folder`.
- `project/recent.py` — recent-projects MRU store (JSON under user config dir).
- `project/autosave.py` — `files_to_autosave` (pure dirty-set decision).

**New (`ui/editor/`):**
- `ui/editor/__init__.py` — package marker.
- `ui/editor/code_editor.py` — `CodeEditor(QsciScintilla)` themed C++ editor.
- `ui/editor/editor_tabs.py` — `EditorTabs(QWidget)` tabbed host.

**Modified:**
- `requirements.txt` — add `PyQt6-QScintilla`.
- `app_config.py` — add `USER_CONFIG_DIR`.
- `ui/workers.py` — `ArduinoJobWorker` gains optional `sketch_dir`.
- `ui/main_window.py` — swap `CodePanel`→`EditorTabs`, project menu/actions, autosave timer, project-aware compile.
- `CHANGELOG.md`, `CLAUDE.md`, version bump to `1.2.0`.

**Removed:**
- `ui/code_panel.py` (superseded by `ui/editor/`).

**New tests:**
- `tests/test_project_model.py`, `tests/test_recent_projects.py`, `tests/test_autosave.py`,
  `tests/test_code_editor.py`, `tests/test_editor_tabs.py`.
- Extend `tests/test_workers.py` and `tests/test_main_window.py`.

---

## Task 1: Dependency + user config dir

**Files:**
- Modify: `requirements.txt`
- Modify: `app_config.py:9-22`
- Test: `tests/test_app_config.py` (create or extend)

- [ ] **Step 1: Add the dependency**

Append to `requirements.txt` (after the `pyqtgraph` line):

```
# Code editor widget for the dual-mode editable code view (Phase 3)
PyQt6-QScintilla
```

- [ ] **Step 2: Install it into the venv**

Run: `.venv/bin/pip install PyQt6-QScintilla`
Expected: `Successfully installed PyQt6-QScintilla-2.x` (or "already satisfied").
Verify: `.venv/bin/python -c "from PyQt6.Qsci import QsciScintilla, QsciLexerCPP; print('ok')"` prints `ok`.

- [ ] **Step 3: Write the failing test for USER_CONFIG_DIR**

Create `tests/test_app_config.py` (or add to it if present):

```python
import importlib
from pathlib import Path


def test_user_config_dir_respects_xdg(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import app_config

    importlib.reload(app_config)
    assert app_config.USER_CONFIG_DIR == tmp_path / "SparkIDE"


def test_user_config_dir_defaults_to_home_config(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    import app_config

    importlib.reload(app_config)
    assert app_config.USER_CONFIG_DIR == Path.home() / ".config" / "SparkIDE"
```

- [ ] **Step 4: Run it to confirm failure**

Run: `.venv/bin/python -m pytest tests/test_app_config.py -v`
Expected: FAIL with `AttributeError: module 'app_config' has no attribute 'USER_CONFIG_DIR'`.

- [ ] **Step 5: Implement USER_CONFIG_DIR**

In `app_config.py`, add `import os` under the existing `from pathlib import Path`, and after the `SKETCH_FILE` line (line 22) add:

```python

# ── User config dir (recent projects, settings) ───────────────────────────────
def _user_config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / APP_NAME


USER_CONFIG_DIR = _user_config_dir()
```

- [ ] **Step 6: Run it to confirm pass**

Run: `.venv/bin/python -m pytest tests/test_app_config.py -v`
Expected: PASS (2 passed).

- [ ] **Step 7: Commit**

```bash
git add requirements.txt app_config.py tests/test_app_config.py
git commit -m "feat: add QScintilla dependency and USER_CONFIG_DIR

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Project model (`project/model.py`)

**Files:**
- Create: `project/__init__.py`, `project/model.py`
- Test: `tests/test_project_model.py`

- [ ] **Step 1: Write the failing tests**

Create `project/__init__.py` (empty file).
Create `tests/test_project_model.py`:

```python
import pytest

from project.model import (
    Project,
    create_project,
    is_sketch_folder,
    open_project,
)


def test_create_project_makes_sketch_folder(tmp_path):
    proj = create_project(tmp_path, "blinky")
    assert proj.root == tmp_path / "blinky"
    assert proj.name == "blinky"
    assert proj.main_ino == tmp_path / "blinky" / "blinky.ino"
    assert proj.main_ino.exists()
    assert proj.workspace_path == tmp_path / "blinky" / "blinky.blocks.json"
    assert proj.workspace_path.exists()


def test_create_project_rejects_duplicate(tmp_path):
    create_project(tmp_path, "blinky")
    with pytest.raises(FileExistsError):
        create_project(tmp_path, "blinky")


def test_create_project_rejects_bad_name(tmp_path):
    with pytest.raises(ValueError):
        create_project(tmp_path, "bad name/slash")


def test_is_sketch_folder(tmp_path):
    proj = create_project(tmp_path, "demo")
    assert is_sketch_folder(proj.root) is True
    assert is_sketch_folder(tmp_path) is False


def test_open_project_from_folder_or_file(tmp_path):
    created = create_project(tmp_path, "demo")
    by_folder = open_project(created.root)
    by_file = open_project(created.main_ino)
    assert by_folder.root == created.root
    assert by_file.root == created.root


def test_open_project_rejects_non_sketch(tmp_path):
    with pytest.raises(ValueError):
        open_project(tmp_path)


def test_files_tags_generated_main_and_lists_companions(tmp_path):
    proj = create_project(tmp_path, "demo")
    (proj.root / "helpers.h").write_text("// h")
    (proj.root / "extra.cpp").write_text("// cpp")
    files = proj.files()
    main = [f for f in files if f.is_generated]
    assert len(main) == 1
    assert main[0].path == proj.main_ino
    assert main[0].kind == "main_ino"
    companions = {f.path.name for f in proj.companion_files()}
    assert companions == {"helpers.h", "extra.cpp"}
```

- [ ] **Step 2: Run to confirm failure**

Run: `.venv/bin/python -m pytest tests/test_project_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'project.model'`.

- [ ] **Step 3: Implement `project/model.py`**

```python
"""
project/model.py — Qt-free model of a SparkIDE project (an Arduino sketch folder).

A project is a sketch folder named after its main sketch:
    blinky/
      blinky.ino          ← block-generated main sketch (authoritative)
      blinky.blocks.json  ← saved Blockly workspace
      helpers.h, ...      ← optional hand-edited companion files
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_VALID_NAME = re.compile(r"^[A-Za-z0-9_]+$")
_SOURCE_SUFFIXES = {".ino", ".h", ".cpp"}

_STARTER_INO = """\
void setup() {
  // put your setup code here, to run once:
}

void loop() {
  // put your main code here, to run repeatedly:
}
"""


@dataclass(frozen=True)
class ProjectFile:
    path: Path
    kind: str  # "main_ino" | "ino" | "header" | "source"
    is_generated: bool


@dataclass(frozen=True)
class Project:
    root: Path
    name: str

    @property
    def main_ino(self) -> Path:
        return self.root / f"{self.name}.ino"

    @property
    def workspace_path(self) -> Path:
        return self.root / f"{self.name}.blocks.json"

    def files(self) -> list[ProjectFile]:
        out: list[ProjectFile] = []
        for p in sorted(self.root.iterdir()):
            if not p.is_file() or p.suffix not in _SOURCE_SUFFIXES:
                continue
            if p == self.main_ino:
                out.append(ProjectFile(p, "main_ino", True))
            elif p.suffix == ".ino":
                out.append(ProjectFile(p, "ino", False))
            elif p.suffix == ".h":
                out.append(ProjectFile(p, "header", False))
            else:
                out.append(ProjectFile(p, "source", False))
        return out

    def companion_files(self) -> list[ProjectFile]:
        return [f for f in self.files() if not f.is_generated]


def is_sketch_folder(path: Path) -> bool:
    path = Path(path)
    if not path.is_dir():
        return False
    return (path / f"{path.name}.ino").exists()


def create_project(parent_dir: Path, name: str) -> Project:
    if not _VALID_NAME.match(name):
        raise ValueError(f"Invalid project name: {name!r} (letters, digits, underscore only)")
    root = Path(parent_dir) / name
    if root.exists():
        raise FileExistsError(f"Project folder already exists: {root}")
    root.mkdir(parents=True)
    proj = Project(root=root, name=name)
    proj.main_ino.write_text(_STARTER_INO, encoding="utf-8")
    proj.workspace_path.write_text("", encoding="utf-8")
    return proj


def open_project(path: Path) -> Project:
    path = Path(path)
    folder = path if path.is_dir() else path.parent
    if not is_sketch_folder(folder):
        raise ValueError(f"Not a SparkIDE/Arduino sketch folder: {folder}")
    return Project(root=folder, name=folder.name)
```

- [ ] **Step 4: Run to confirm pass**

Run: `.venv/bin/python -m pytest tests/test_project_model.py -v`
Expected: PASS (7 passed).

- [ ] **Step 5: Commit**

```bash
git add project/__init__.py project/model.py tests/test_project_model.py
git commit -m "feat: add Qt-free project (sketch-folder) model

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Recent-projects store (`project/recent.py`)

**Files:**
- Create: `project/recent.py`
- Test: `tests/test_recent_projects.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_recent_projects.py`:

```python
import project.recent as recent


def _redirect(monkeypatch, tmp_path):
    store = tmp_path / "recent_projects.json"
    monkeypatch.setattr(recent, "recent_store_path", lambda: store)
    return store


def test_add_and_load_roundtrip(monkeypatch, tmp_path):
    _redirect(monkeypatch, tmp_path)
    a = tmp_path / "a"
    a.mkdir()
    recent.add_recent(a)
    assert recent.load_recent() == [a]


def test_add_is_mru_and_dedupes(monkeypatch, tmp_path):
    _redirect(monkeypatch, tmp_path)
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    recent.add_recent(a)
    recent.add_recent(b)
    recent.add_recent(a)  # bump a to front, no dupe
    assert recent.load_recent() == [a, b]


def test_load_prunes_missing(monkeypatch, tmp_path):
    store = _redirect(monkeypatch, tmp_path)
    gone = tmp_path / "gone"
    store.write_text(f'["{gone}"]')
    assert recent.load_recent() == []


def test_cap_at_ten(monkeypatch, tmp_path):
    _redirect(monkeypatch, tmp_path)
    for i in range(12):
        d = tmp_path / f"p{i}"
        d.mkdir()
        recent.add_recent(d)
    assert len(recent.load_recent()) == 10


def test_clear(monkeypatch, tmp_path):
    _redirect(monkeypatch, tmp_path)
    d = tmp_path / "a"
    d.mkdir()
    recent.add_recent(d)
    recent.clear_recent()
    assert recent.load_recent() == []
```

- [ ] **Step 2: Run to confirm failure**

Run: `.venv/bin/python -m pytest tests/test_recent_projects.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'project.recent'`.

- [ ] **Step 3: Implement `project/recent.py`**

```python
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
```

- [ ] **Step 4: Run to confirm pass**

Run: `.venv/bin/python -m pytest tests/test_recent_projects.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add project/recent.py tests/test_recent_projects.py
git commit -m "feat: add recent-projects MRU store

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Autosave decision (`project/autosave.py`)

**Files:**
- Create: `project/autosave.py`
- Test: `tests/test_autosave.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_autosave.py`:

```python
from pathlib import Path

from project.autosave import files_to_autosave


def test_returns_only_dirty_buffers():
    a, b, c = Path("a.h"), Path("b.h"), Path("c.h")
    buffers = {a: "changed", b: "same", c: "also changed"}
    on_disk = {a: "original", b: "same", c: "original"}
    assert files_to_autosave(buffers, on_disk) == {a: "changed", c: "also changed"}


def test_new_file_not_on_disk_is_dirty():
    a = Path("new.h")
    assert files_to_autosave({a: "hello"}, {}) == {a: "hello"}


def test_no_dirty_returns_empty():
    a = Path("a.h")
    assert files_to_autosave({a: "x"}, {a: "x"}) == {}
```

- [ ] **Step 2: Run to confirm failure**

Run: `.venv/bin/python -m pytest tests/test_autosave.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'project.autosave'`.

- [ ] **Step 3: Implement `project/autosave.py`**

```python
"""
project/autosave.py — Qt-free decision of which editor buffers need writing.

The UI owns the timer and the actual disk I/O; this module only decides the
dirty set (buffers whose content differs from what is currently on disk).
"""

from __future__ import annotations

from pathlib import Path


def files_to_autosave(
    buffers: dict[Path, str], on_disk: dict[Path, str]
) -> dict[Path, str]:
    return {path: text for path, text in buffers.items() if on_disk.get(path) != text}
```

- [ ] **Step 4: Run to confirm pass**

Run: `.venv/bin/python -m pytest tests/test_autosave.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add project/autosave.py tests/test_autosave.py
git commit -m "feat: add pure autosave dirty-set decision

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Themed code editor (`ui/editor/code_editor.py`)

**Files:**
- Create: `ui/editor/__init__.py`, `ui/editor/code_editor.py`
- Test: `tests/test_code_editor.py`

**Note:** Inspect `ui/theme.py` first for the exact token names (e.g. `BG_PANEL`, `BG_DARK`, `BORDER`, `FONT_MONO`, `ACCENT_GRN`, `ACCENT_AMBER`, `TEXT_MAIN`). Use whichever names exist; the values below are illustrative literals if a token is missing.

- [ ] **Step 1: Write the failing tests**

Create `ui/editor/__init__.py` (empty file).
Create `tests/test_code_editor.py`:

```python
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication

from ui.editor.code_editor import CodeEditor


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_set_and_get_text(app):
    ed = CodeEditor()
    ed.setText("int x = 1;")
    assert ed.text() == "int x = 1;"


def test_read_only_toggle(app):
    ed = CodeEditor()
    ed.set_read_only(True)
    assert ed.isReadOnly() is True
    ed.set_read_only(False)
    assert ed.isReadOnly() is False


def test_modified_flag(app):
    ed = CodeEditor()
    ed.setText("seed")
    ed.setModified(False)
    assert ed.is_modified() is False
    ed.append_text(" more")
    assert ed.is_modified() is True
```

- [ ] **Step 2: Run to confirm failure**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_code_editor.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ui.editor.code_editor'`.

- [ ] **Step 3: Implement `ui/editor/code_editor.py`**

```python
"""
ui/editor/code_editor.py — QScintilla C++ editor themed to the Hybrid Lab Console.

Used both as the read-only "Generated" view and as the editable companion-file
editor. Theming lives entirely in _apply_theme so the palette is retuned in one
place.
"""

from PyQt6.QtGui import QColor, QFont, QFontMetrics
from PyQt6.Qsci import QsciLexerCPP, QsciScintilla

from ui import theme


class CodeEditor(QsciScintilla):
    """A themed C++ code editor (line numbers, folding, brace match)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont("Fira Code", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        if not font.exactMatch():
            font = QFont("JetBrains Mono", 11)
            font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        lexer = QsciLexerCPP(self)
        lexer.setFont(font)
        self._lexer = lexer
        self.setLexer(lexer)

        self.setUtf8(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(2)
        self.setAutoIndent(True)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, QFontMetrics(font).horizontalAdvance("0000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setCaretLineVisible(True)
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsDocument)
        self.setAutoCompletionThreshold(3)

        self._apply_theme()

    def _apply_theme(self):
        bg = QColor(theme.BG_PANEL)
        fg = QColor(getattr(theme, "TEXT_MAIN", "#e4f0e8"))
        margin_bg = QColor(theme.BG_DARK)
        accent = QColor(getattr(theme, "ACCENT_GRN", "#4ade80"))

        self.setColor(fg)
        self.setPaper(bg)
        self.setCaretForegroundColor(accent)
        self.setCaretLineBackgroundColor(QColor(theme.BG_DARK))
        self.setMarginsBackgroundColor(margin_bg)
        self.setMarginsForegroundColor(QColor(getattr(theme, "TEXT_DIM", "#5c7468")))
        self.setSelectionBackgroundColor(QColor("#1d3a2c"))
        self.setFoldMarginColors(margin_bg, margin_bg)

        lex = self._lexer
        lex.setDefaultPaper(bg)
        lex.setDefaultColor(fg)
        lex.setPaper(bg)  # all styles share the panel background
        lex.setColor(fg, QsciLexerCPP.Default)
        lex.setColor(QColor("#8aa6c4"), QsciLexerCPP.Keyword)
        lex.setColor(QColor("#7ee2a8"), QsciLexerCPP.GlobalClass)
        lex.setColor(QColor("#6fcfc0"), QsciLexerCPP.DoubleQuotedString)
        lex.setColor(QColor("#6fcfc0"), QsciLexerCPP.SingleQuotedString)
        lex.setColor(QColor("#d9b36a"), QsciLexerCPP.Number)
        lex.setColor(QColor(getattr(theme, "ACCENT_AMBER", "#f0a93e")), QsciLexerCPP.PreProcessor)
        lex.setColor(QColor("#5c7468"), QsciLexerCPP.Comment)
        lex.setColor(QColor("#5c7468"), QsciLexerCPP.CommentLine)

    # ── Public helpers ─────────────────────────────────────────────────────────

    def set_read_only(self, read_only: bool) -> None:
        self.setReadOnly(read_only)

    def is_modified(self) -> bool:
        return self.isModified()

    def append_text(self, text: str) -> None:
        self.append(text)
```

- [ ] **Step 4: Run to confirm pass**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_code_editor.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add ui/editor/__init__.py ui/editor/code_editor.py tests/test_code_editor.py
git commit -m "feat: add themed QScintilla code editor

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 6: Editor tabs (`ui/editor/editor_tabs.py`)

**Files:**
- Create: `ui/editor/editor_tabs.py`
- Test: `tests/test_editor_tabs.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_editor_tabs.py`:

```python
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication

from ui.editor.editor_tabs import EditorTabs


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_generated_tab_update_and_current(app):
    tabs = EditorTabs()
    tabs.update_code("void loop() {}")
    assert tabs.current_code() == "void loop() {}"


def test_open_file_creates_editable_tab(app, tmp_path):
    f = tmp_path / "helpers.h"
    f.write_text("#define PI 3")
    tabs = EditorTabs()
    tabs.open_file(f)
    assert f in tabs.open_paths()
    assert tabs.count() == 2  # Generated + helpers.h


def test_open_file_is_idempotent(app, tmp_path):
    f = tmp_path / "a.cpp"
    f.write_text("// a")
    tabs = EditorTabs()
    tabs.open_file(f)
    tabs.open_file(f)
    assert tabs.count() == 2


def test_dirty_buffers_reflect_edits(app, tmp_path):
    f = tmp_path / "a.cpp"
    f.write_text("// a")
    tabs = EditorTabs()
    tabs.open_file(f)
    tabs.editor_for(f).setText("// changed")
    assert tabs.dirty_buffers() == {f: "// changed"}


def test_close_file_removes_tab(app, tmp_path):
    f = tmp_path / "a.cpp"
    f.write_text("// a")
    tabs = EditorTabs()
    tabs.open_file(f)
    tabs.close_file(f)
    assert f not in tabs.open_paths()
    assert tabs.count() == 1
```

- [ ] **Step 2: Run to confirm failure**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_editor_tabs.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ui.editor.editor_tabs'`.

- [ ] **Step 3: Implement `ui/editor/editor_tabs.py`**

```python
"""
ui/editor/editor_tabs.py — tabbed multi-file editor host.

Tab 0 is the read-only block-generated "Generated" view (same update_code /
current_code surface the old CodePanel exposed, so bridge wiring is unchanged).
Further tabs are editable companion files backed by CodeEditor. Project lifecycle
and disk I/O policy live in MainWindow; this widget only edits files it is told to
open.
"""

from pathlib import Path

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui import theme
from ui.editor.code_editor import CodeEditor

SAMPLE_CODE = """\
// Generated C++ will appear here as you place blocks.

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
"""


class EditorTabs(QWidget):
    """Tabbed editor: read-only Generated view + editable companion files."""

    dirty_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editors: dict[Path, CodeEditor] = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.tabCloseRequested.connect(self._on_tab_close_requested)

        # ── Generated tab (header chrome + read-only editor) ──
        gen = QWidget()
        gl = QVBoxLayout(gen)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(36)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 0, 10, 0)
        self._live_dot = QLabel("Live sync")
        self._live_dot.setStyleSheet(
            f"color: {getattr(theme, 'ACCENT_GRN', '#4ade80')};"
            f" font-family: {theme.FONT_MONO}; font-size: 10px; font-weight: 600;"
        )
        hl.addWidget(self._live_dot)
        hl.addStretch()
        self._line_count = QLabel("0 lines")
        self._line_count.setStyleSheet(
            f"color: {getattr(theme, 'TEXT_DIM', '#5c7468')};"
            f" font-family: {theme.FONT_MONO}; font-size: 10px; margin-right: 8px;"
        )
        hl.addWidget(self._line_count)
        copy_btn = QPushButton("Copy")
        copy_btn.setFixedSize(60, 24)
        copy_btn.clicked.connect(self._copy_generated)
        hl.addWidget(copy_btn)
        gl.addWidget(header)

        self._generated = CodeEditor()
        self._generated.set_read_only(True)
        self._generated.setText(SAMPLE_CODE)
        self._generated.textChanged.connect(self._update_line_count)
        gl.addWidget(self._generated)

        self._tabs.addTab(gen, "Generated")
        # The Generated tab cannot be closed.
        self._tabs.tabBar().setTabButton(0, self._tabs.tabBar().ButtonPosition.RightSide, None)

        root.addWidget(self._tabs)
        self._update_line_count()

    # ── Generated view surface (matches the old CodePanel) ──────────────────────

    @pyqtSlot(str)
    def update_code(self, cpp_str: str) -> None:
        self._generated.setText(cpp_str)

    def current_code(self) -> str:
        return self._generated.text()

    # ── Companion files ─────────────────────────────────────────────────────────

    def open_file(self, path: Path) -> None:
        path = Path(path)
        if path in self._editors:
            self._tabs.setCurrentWidget(self._editors[path])
            return
        ed = CodeEditor()
        ed.setText(path.read_text(encoding="utf-8"))
        ed.setModified(False)
        ed.modificationChanged.connect(lambda _=None: self._on_modified(path))
        self._editors[path] = ed
        self._tabs.addTab(ed, path.name)
        self._tabs.setCurrentWidget(ed)
        self._refresh_tab_label(path)

    def new_file(self, path: Path) -> None:
        path = Path(path)
        path.write_text("", encoding="utf-8")
        self.open_file(path)

    def close_file(self, path: Path) -> None:
        ed = self._editors.pop(Path(path), None)
        if ed is not None:
            self._tabs.removeTab(self._tabs.indexOf(ed))
            ed.deleteLater()
        self.dirty_changed.emit(self.has_dirty())

    def editor_for(self, path: Path) -> CodeEditor:
        return self._editors[Path(path)]

    def open_paths(self) -> list[Path]:
        return list(self._editors.keys())

    def count(self) -> int:
        return self._tabs.count()

    def dirty_buffers(self) -> dict[Path, str]:
        return {p: ed.text() for p, ed in self._editors.items() if ed.is_modified()}

    def has_dirty(self) -> bool:
        return any(ed.is_modified() for ed in self._editors.values())

    def mark_saved(self, path: Path) -> None:
        ed = self._editors.get(Path(path))
        if ed is not None:
            ed.setModified(False)
            self._refresh_tab_label(Path(path))
        self.dirty_changed.emit(self.has_dirty())

    # ── Internal ──────────────────────────────────────────────────────────────

    def _on_modified(self, path: Path):
        self._refresh_tab_label(path)
        self.dirty_changed.emit(self.has_dirty())

    def _refresh_tab_label(self, path: Path):
        ed = self._editors.get(path)
        if ed is None:
            return
        idx = self._tabs.indexOf(ed)
        marker = "● " if ed.is_modified() else ""
        self._tabs.setTabText(idx, f"{marker}{path.name}")

    def _on_tab_close_requested(self, index: int):
        widget = self._tabs.widget(index)
        for path, ed in self._editors.items():
            if ed is widget:
                self.close_file(path)
                return

    def _update_line_count(self):
        n = len(self._generated.text().splitlines())
        self._line_count.setText(f"{n} line{'s' if n != 1 else ''}")

    def _copy_generated(self):
        QApplication.clipboard().setText(self._generated.text())
```

- [ ] **Step 4: Run to confirm pass**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_editor_tabs.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add ui/editor/editor_tabs.py tests/test_editor_tabs.py
git commit -m "feat: add tabbed multi-file editor host

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 7: `ArduinoJobWorker` sketch-dir override

**Files:**
- Modify: `ui/workers.py:38-70`
- Test: `tests/test_workers.py` (extend)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_workers.py`:

```python
def test_arduino_job_worker_accepts_sketch_dir(tmp_path):
    from ui.workers import ArduinoJobWorker

    sketch_dir = tmp_path / "blinky"
    w = ArduinoJobWorker("compile", "arduino:avr:uno", "", "void setup(){}\nvoid loop(){}", sketch_dir=sketch_dir)
    assert w._sketch_dir == sketch_dir
    # default stays None for the legacy build-dir behaviour
    w2 = ArduinoJobWorker("compile", "arduino:avr:uno", "", "x")
    assert w2._sketch_dir is None
```

- [ ] **Step 2: Run to confirm failure**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_workers.py::test_arduino_job_worker_accepts_sketch_dir -v`
Expected: FAIL with `TypeError: __init__() got an unexpected keyword argument 'sketch_dir'`.

- [ ] **Step 3: Implement the override**

In `ui/workers.py`, change the imports line `from app_config import BUILD_DIR, SKETCH_FILE` to also import `Path`:

```python
from pathlib import Path

from app_config import BUILD_DIR, SKETCH_FILE
```

Replace `ArduinoJobWorker.__init__` and `run` (lines 38-70) with:

```python
    def __init__(self, action: str, fqbn: str, port: str, code: str, parent=None, *, sketch_dir=None):
        super().__init__(parent)
        self._action = action
        self._fqbn = fqbn
        self._port = port
        self._code = code
        self._sketch_dir = Path(sketch_dir) if sketch_dir is not None else None

    def run(self):
        try:
            if self._sketch_dir is not None:
                build_dir = self._sketch_dir
                sketch_file = build_dir / f"{build_dir.name}.ino"
            else:
                build_dir = BUILD_DIR
                sketch_file = SKETCH_FILE
            build_dir.mkdir(parents=True, exist_ok=True)
            sketch_file.write_text(self._code, encoding="utf-8")
            self.line.emit(f"Sketch written to {sketch_file}", "dim")

            captured: list[str] = []

            def cb(line: str, level: str):
                captured.append(line)
                self.line.emit(line, level)

            cli = ArduinoCLI()
            if self._action == "compile":
                ok = cli.compile(self._fqbn, build_dir, cb)
                self.stats.emit(parse_compile_stats("\n".join(captured)))
                self.finished.emit(ok, "Compile complete." if ok else "Compile failed.")
            else:
                ok = cli.compile(self._fqbn, build_dir, cb)
                if ok:
                    ok = cli.upload(self._fqbn, self._port, build_dir, cb)
                self.stats.emit(parse_compile_stats("\n".join(captured)))
                self.finished.emit(ok, "Upload complete." if ok else "Upload failed.")
        except OSError as exc:
            self.line.emit(f"Could not write sketch: {exc}", "error")
            self.finished.emit(False, "Sketch write failed.")
```

- [ ] **Step 4: Run to confirm pass**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_workers.py -v`
Expected: PASS (all worker tests, including the new one).

- [ ] **Step 5: Commit**

```bash
git add ui/workers.py tests/test_workers.py
git commit -m "feat: let ArduinoJobWorker target a project sketch dir

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 8: Wire projects into `MainWindow`

**Files:**
- Modify: `ui/main_window.py` (imports, `_build_central`, `_setup_web_channel`, `_build_menu_bar`, `_start_job`, add project/autosave slots)
- Delete: `ui/code_panel.py`
- Test: `tests/test_main_window.py` (extend)

**Note:** Read the current `ui/main_window.py` in full before editing. The edits below are surgical; keep everything else intact.

- [ ] **Step 1: Write the failing test**

`tests/test_main_window.py` already builds a `MainWindow` under offscreen Qt via the
`qapp` fixture and a `_build_window()` helper that patches `QWebEngineView` and
`BoardRefreshWorker`. Reuse that helper. Add:

```python
def test_open_project_populates_tabs_and_state(qapp, tmp_path):
    from project.model import create_project

    proj = create_project(tmp_path, "demo")
    (proj.root / "helpers.h").write_text("#define X 1")

    window = _build_window()
    window._load_project(proj)

    assert window._project is not None
    assert window._project.root == proj.root
    # Generated tab + helpers.h companion are both open.
    assert proj.root / "helpers.h" in window._editor.open_paths()
```

Also update the existing `test_main_window_builds` assertion at line 49 — change
`assert window._code_panel is not None` to `assert window._editor is not None` (the
panel is being renamed in this task).

- [ ] **Step 2: Run to confirm failure**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_main_window.py::test_open_project_populates_tabs_and_state -v`
Expected: FAIL — `MainWindow` has no `_load_project` / `_editor` / `_project`.

- [ ] **Step 3: Swap CodePanel → EditorTabs**

In `ui/main_window.py`:

Replace the import `from ui.code_panel import CodePanel` with:

```python
from ui.editor.editor_tabs import EditorTabs
```

Add to the imports block:

```python
from PyQt6.QtCore import QTimer
from project.model import Project, create_project, open_project
from project import recent
from project.autosave import files_to_autosave
```

(Merge `QTimer` into the existing `from PyQt6.QtCore import Qt, QUrl` line instead of duplicating: `from PyQt6.QtCore import Qt, QTimer, QUrl`.)

In `_build_central` (line 114), replace `self._code_panel = CodePanel()` with `self._editor = EditorTabs()`, and replace `splitter.addWidget(self._code_panel)` with `splitter.addWidget(self._editor)`.

In `_setup_web_channel` (line 156), replace `self._bridge.code_changed.connect(self._code_panel.update_code)` with `self._bridge.code_changed.connect(self._editor.update_code)`.

In `_start_job` (line 352), replace `code = self._code_panel.current_code().strip()` with `code = self._editor.current_code().strip()`.

- [ ] **Step 4: Add project state + autosave timer to `__init__`**

In `MainWindow.__init__` (after `self._job_worker = None`, line 58), add:

```python
        self._project: Project | None = None
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(30_000)
        self._autosave_timer.timeout.connect(self._on_autosave)
```

- [ ] **Step 5: Add project actions to the File menu**

In `_build_menu_bar`, after the existing `file_menu` loop block (before `file_menu.addSeparator()` at line 94), add:

```python
        file_menu.addSeparator()
        for label, shortcut, slot, tip in [
            ("New &Project…", "Ctrl+Shift+N", self._on_new_project, "Create a sketch-folder project"),
            ("Open Pro&ject…", "Ctrl+Shift+O", self._on_open_project, "Open an existing sketch folder"),
            ("Ne&w File…", "", self._on_new_file, "Add a file to the current project"),
        ]:
            act = QAction(label, self)
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            act.setStatusTip(tip)
            act.triggered.connect(slot)
            file_menu.addAction(act)
        self._recent_menu = file_menu.addMenu("Open &Recent")
        self._recent_menu.aboutToShow.connect(self._rebuild_recent_menu)
```

- [ ] **Step 6: Add the project/autosave slots**

Add these methods to `MainWindow` (e.g. after `_on_clear`, around line 289):

```python
    # ── Project lifecycle ───────────────────────────────────────────────────────

    def _on_new_project(self):
        parent = QFileDialog.getExistingDirectory(self, "Choose parent folder for new project")
        if not parent:
            return
        name, ok = QInputDialog.getText(self, "New Project", "Project name (letters, digits, _):")
        if not ok or not name:
            return
        try:
            proj = create_project(Path(parent), name)
        except (ValueError, FileExistsError, OSError) as exc:
            self._show_warning(f"Could not create project: {exc}")
            return
        self._load_project(proj)

    def _on_open_project(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Project (sketch folder)")
        if not folder:
            return
        try:
            proj = open_project(Path(folder))
        except ValueError as exc:
            self._show_warning(str(exc))
            return
        self._load_project(proj)

    def _on_open_recent(self, path: Path):
        try:
            proj = open_project(path)
        except ValueError:
            # load_recent() prunes missing folders on its next read, so nothing to do here.
            self._show_warning(f"Project no longer found: {path}")
            return
        self._load_project(proj)

    def _load_project(self, proj: Project):
        self._project = proj
        recent.add_recent(proj.root)
        ws = proj.workspace_path.read_text(encoding="utf-8") if proj.workspace_path.exists() else ""
        if ws.strip():
            self._bridge.load_workspace(ws)
        for f in proj.companion_files():
            self._editor.open_file(f.path)
        self.setWindowTitle(f"{APP_NAME} — {proj.name}")
        self._autosave_timer.start()
        self._log_panel.append_line(f"Project opened: {proj.root}", "success")

    def _on_new_file(self):
        if self._project is None:
            self._show_warning("Open or create a project first.")
            return
        name, ok = QInputDialog.getText(self, "New File", "File name (e.g. helpers.h):")
        if not ok or not name:
            return
        path = self._project.root / name
        if path.exists():
            self._show_warning(f"File already exists: {name}")
            return
        self._editor.new_file(path)
        self._log_panel.append_line(f"Created {name}", "success")

    def _rebuild_recent_menu(self):
        self._recent_menu.clear()
        items = recent.load_recent()
        if not items:
            act = QAction("(no recent projects)", self)
            act.setEnabled(False)
            self._recent_menu.addAction(act)
            return
        for path in items:
            act = QAction(path.name, self)
            act.setStatusTip(str(path))
            act.triggered.connect(lambda _checked=False, p=path: self._on_open_recent(p))
            self._recent_menu.addAction(act)

    def _on_autosave(self):
        if self._project is None:
            return
        buffers = self._editor.dirty_buffers()
        on_disk = {}
        for path in buffers:
            try:
                on_disk[path] = path.read_text(encoding="utf-8")
            except OSError:
                on_disk[path] = None
        for path, text in files_to_autosave(buffers, on_disk).items():
            try:
                path.write_text(text, encoding="utf-8")
                self._editor.mark_saved(path)
            except OSError as exc:
                self._log_panel.append_line(f"Autosave failed for {path.name}: {exc}", "warning")

        def _save_ws(json_str: str):
            if json_str:
                try:
                    self._project.workspace_path.write_text(json_str, encoding="utf-8")
                except OSError:
                    pass

        self._bridge.get_workspace_json(_save_ws)
```

Add `QInputDialog` to the `PyQt6.QtWidgets` import block at the top.

- [ ] **Step 7: Make compile/upload target the project**

In `_start_job` (line 366), replace the worker construction:

```python
        self._job_worker = ArduinoJobWorker(action, fqbn, port, code, self)
```

with:

```python
        sketch_dir = self._project.root if self._project is not None else None
        if sketch_dir is not None:
            # keep companion files current before compiling the whole folder
            for path, text in self._editor.dirty_buffers().items():
                try:
                    path.write_text(text, encoding="utf-8")
                    self._editor.mark_saved(path)
                except OSError as exc:
                    self._log_panel.append_line(f"Could not save {path.name}: {exc}", "warning")
        self._job_worker = ArduinoJobWorker(action, fqbn, port, code, self, sketch_dir=sketch_dir)
```

- [ ] **Step 8: Delete the obsolete panel**

Run: `git rm ui/code_panel.py`
Then grep for any other references: `grep -rn "code_panel\|CodePanel" --include=*.py .`
Expected: no remaining references except possibly an old test — if `tests/test_code_panel.py` exists, `git rm tests/test_code_panel.py` (its coverage is replaced by `test_code_editor.py` / `test_editor_tabs.py`).

- [ ] **Step 9: Run the new test + full suite**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_main_window.py -v`
Expected: PASS including `test_open_project_populates_tabs_and_state`.
Run: `make test`
Expected: all tests pass.

- [ ] **Step 10: Smoke-run the app**

Run: `QT_QPA_PLATFORM=offscreen .venv/bin/python -c "from ui.main_window import MainWindow; from PyQt6.QtWidgets import QApplication; a=QApplication([]); w=MainWindow(); print('window built ok'); w.close()"`
Expected: prints `window built ok` with no traceback.

- [ ] **Step 11: Commit**

```bash
git add ui/main_window.py tests/test_main_window.py
git rm ui/code_panel.py
git commit -m "feat: wire folder-based projects, tabs, and autosave into the window

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 9: Docs, version bump, changelog

**Files:**
- Modify: `app_config.py` (version) via `make bump-version`
- Modify: `CHANGELOG.md`, `CLAUDE.md`

- [ ] **Step 1: Bump the version**

Run: `make bump-version VERSION=1.2.0`
Verify: `grep APP_VERSION app_config.py` shows `APP_VERSION = "1.2.0"`.

- [ ] **Step 2: Update CHANGELOG.md**

Add a new section at the top of the entries (match the existing format/heading style used for Phase 2):

```markdown
## [1.2.0] — Phase 3: Editor Depth & Dual-Mode

### Added
- QScintilla-based editable code mode (line numbers, folding, brace matching,
  autocomplete) themed to the Hybrid Lab Console palette.
- Folder-based multi-file Arduino projects: New/Open Project, file tabs,
  New File, Open Recent, and timer-based autosave of edited files + workspace.
- Block-authoritative block↔code model: blocks own the read-only generated
  sketch; companion `.h`/`.cpp`/`.ino` files are freely editable.
- Compile/upload now build the whole project folder when a project is open.

### Changed
- Replaced the read-only `CodePanel` with a tabbed `EditorTabs` editor.
```

- [ ] **Step 3: Update CLAUDE.md**

Document, in the architecture section: the new `project/` package (`model.py`,
`recent.py`, `autosave.py` — all Qt-free), the new `ui/editor/` package
(`code_editor.py`, `editor_tabs.py`) replacing `ui/code_panel.py`, the
`ArduinoJobWorker` `sketch_dir` override, the autosave timer + recent-projects flow
in `MainWindow`, and the block-authoritative interaction rule (generated sketch is
read-only; companion files are editable). Add `PyQt6-QScintilla` to the dependency
notes. Mirror the wording style of the existing Phase 2 entries.

- [ ] **Step 4: Run all quality gates**

Run: `make lint`
Expected: exit 0, all checks pass.
Run: `make test`
Expected: all pass.
Run: `make test-js`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add app_config.py CHANGELOG.md CLAUDE.md
git commit -m "docs: document Phase 3 features and bump version to 1.2.0

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Done When

A user can create/open a multi-file project, edit companion files in QScintilla tabs,
see autosave persist edits + workspace, reopen recent projects, and compile/upload the
whole project — with the block-only v1.1.0 flow intact and `make lint` / `make test` /
`make test-js` all green.
```
