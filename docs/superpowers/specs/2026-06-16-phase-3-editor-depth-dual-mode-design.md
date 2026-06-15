# Phase 3 — Editor Depth & Dual-Mode: Design

**Date:** 2026-06-16
**Status:** Approved
**Owner:** Harsh Verma
**Roadmap:** `docs/superpowers/specs/2026-06-15-professional-ide-roadmap.md` (Phase 3)
**Target version:** 1.2.0

## Goal

Let advanced users graduate beyond blocks without losing the beginner-first block
experience. A user can open or create a multi-file Arduino **project** (a sketch
folder), edit C++ companion files directly in a real code editor, switch between
open files in tabs, and have their work autosaved — while the block-generated main
sketch stays the authoritative, live, read-only source of truth.

## Scope (three features, one sequenced release)

1. **Editable text/code mode** — a `QScintilla`-based editor (folding, autocomplete,
   brace matching, find/replace, line numbers) themed to the Hybrid Lab Console
   palette, used for editable companion files. The block-generated sketch keeps a
   read-only view in the same editor.
2. **Multi-file projects** — a project is an Arduino sketch folder. File tabs across
   open files, New/Open/Close file, recent-projects list, and timer-based autosave.
3. **Block ↔ code interaction model** — **block-authoritative**: blocks own the
   generated main `.ino` (read-only preview); companion files (`.h`, `.cpp`, extra
   `.ino`) are fully editable. No code → block round-trip in this phase (deferred per
   roadmap).

Out of scope for Phase 3: code → block synchronisation / round-trip; non-AVR board
enablement (Phase 6); cross-platform packaging (Phase 4); a plugin API (Phase 5).

## Guiding constraints

- **Reuse existing patterns.** Pure/testable logic is Qt-free and lives outside
  `ui/` (new `project/` package, mirroring how `cli/` stays Qt-free); UI widgets pull
  tokens from `ui/theme.py`; paths/identity live in `app_config.py`; long-running
  work (none new expected here) would go through `ui/workers.py`.
- **Block-authoritative, no data loss.** The generated `.ino` is never hand-edited in
  place; edits happen only in companion files the user explicitly creates/opens. This
  removes the round-trip data-loss risk the roadmap calls out.
- **Backwards compatible.** With no project open, the app behaves exactly as v1.1.0:
  blocks generate code into `build/sparkide_sketch/` and compile/upload work
  unchanged. Projects are an opt-in layer on top.
- **Offline + testable.** QScintilla is a native Qt widget (no CDN/web bridge); the
  project model, recent-projects store, and autosave decision are pure functions
  covered by pytest without a running Qt app.

## Architecture

### New dependency (`requirements.txt`)

- `PyQt6-QScintilla` — the `QsciScintilla` code editor widget and `QsciLexerCPP`
  C++ lexer. Verified to install and import as `from PyQt6.Qsci import QsciScintilla,
  QsciLexerCPP` (v2.14.1).

### Project model (`project/` — new, Qt-free)

**`project/model.py`**

- `@dataclass ProjectFile` — `path: Path`, `kind: str` (`"main_ino" | "ino" | "header"
  | "source"`), `is_generated: bool` (True only for the block-generated main `.ino`).
- `@dataclass Project` — represents an Arduino **sketch folder**:
  - `root: Path` (the sketch folder), `name: str` (folder name == main sketch stem,
    per Arduino's sketch rule).
  - `main_ino` property → `root / f"{name}.ino"` (block-generated, authoritative).
  - `workspace_path` property → `root / f"{name}.blocks.json"` (the saved Blockly
    workspace for this project).
  - `files() -> list[ProjectFile]` — scans the folder for `.ino/.h/.cpp` and tags the
    main ino as generated.
  - `companion_files()` — `files()` minus the generated main ino.
- Module functions (pure, no Qt):
  - `create_project(parent_dir: Path, name: str) -> Project` — makes the folder,
    writes a starter `<name>.ino` and empty `<name>.blocks.json`; raises on
    name/collision errors.
  - `open_project(path: Path) -> Project` — accepts either the folder or a file inside
    it; validates it looks like a sketch folder.
  - `is_sketch_folder(path: Path) -> bool`.

**`project/recent.py`** — recent-projects persistence (Qt-free, JSON):

- `recent_store_path() -> Path` — under the user config dir
  (`app_config.USER_CONFIG_DIR`, e.g. `~/.config/SparkIDE/recent_projects.json`).
- `load_recent() -> list[Path]`, `add_recent(path) -> list[Path]` (dedupe, MRU order,
  cap at 10, drop entries that no longer exist), `clear_recent()`.

**`project/autosave.py`** — the *decision* logic, Qt-free and unit-tested:

- `files_to_autosave(buffers: dict[Path, str], on_disk: dict[Path, str]) ->
  dict[Path, str]` — returns only the buffers whose content differs from disk (dirty
  set). The timer that calls this lives in the UI; the decision is pure.

`app_config.py` gains `USER_CONFIG_DIR` (no Qt import — use `os`/`pathlib` +
`XDG_CONFIG_HOME` fallback to `~/.config`); it stays Qt-free and test-safe.

### Editor (`ui/editor/` — new package)

**`ui/editor/code_editor.py`** — `CodeEditor(QsciScintilla)`:

- A themed C++ editor: `QsciLexerCPP` recoloured to the Hybrid Lab Console palette
  (phosphor green, amber, monospace `FONT_MONO`), margin line numbers, current-line
  highlight, brace matching, auto-indent, and a built-in find/replace
  (`findFirst`/`replace`). Read-only mode toggles for the generated view.
- Exposes `text()`, `setText()`, `set_read_only(bool)`, `is_modified()`, and a
  `modificationChanged`-backed dirty signal.
- Theming lives in one `_apply_theme()` method so the palette is retuned in one place
  (consistent with the `ui/theme.py` philosophy).

**`ui/editor/editor_tabs.py`** — `EditorTabs(QWidget)` (a `QTabWidget` host):

- **Tab 0 — "Generated"**: the read-only block output. Keeps the chrome the old
  `CodePanel` had (Copy button, "Live sync" dot, line count) in a small header strip,
  but the body is a read-only `CodeEditor`. `update_code(cpp)` slot (same signature as
  the old `CodePanel.update_code`, so the bridge wiring is unchanged) and
  `current_code()` (used by compile validation).
- **Tabs 1..n — editable companion files**: one `CodeEditor` per open file, with a
  modified `●` marker in the tab label, close buttons, and save-on-close prompts.
- Public API consumed by `MainWindow`:
  - `update_code(cpp)`, `current_code()` (delegate to the generated tab),
  - `open_file(path)`, `new_file(path)`, `close_file(path)`,
  - `dirty_buffers() -> dict[Path, str]` (for autosave), `save_file(path)`,
    `save_all()`,
  - signal `dirty_changed(bool)` (drives the window title `*` and status).
- Holds no project/IO policy itself beyond reading/writing the files it is told to
  open; project lifecycle is owned by `MainWindow`.

The existing `ui/code_panel.py` (`CodePanel`, `CppHighlighter`) is **removed**; the
`SAMPLE_CODE` placeholder moves into the generated tab. (`CppHighlighter` is
superseded by `QsciLexerCPP`.)

### Wiring (`ui/main_window.py`)

- `_build_central()` swaps `CodePanel` for `EditorTabs` in the splitter (same
  position/sizes). Bridge wiring is unchanged: `code_changed -> editor.update_code`,
  and compile reads `editor.current_code()`.
- **Project state**: `MainWindow` holds an optional `self._project: Project | None`.
  - `_on_new_project()` / `_on_open_project()` — `QFileDialog` to pick a parent dir +
    name / a sketch folder; load `<name>.blocks.json` into Blockly via the existing
    `bridge.load_workspace`; open companion files into tabs; push onto recent list;
    update the window title to the project name.
  - `_on_open_recent(path)` — same as open, from the **File ▸ Open Recent** submenu
    (rebuilt from `project/recent.py` each time the menu opens).
  - File menu adds: **New Project…**, **Open Project…**, **Open Recent ▸**,
    **New File…**, **Save** (Ctrl+S — saves the active editable file; when no project,
    falls back to today's *Save Workspace* JSON behaviour), **Save Workspace** kept for
    the no-project block-only flow.
- **Autosave**: a `QTimer` (e.g. 30 s, only running while a project is open) calls
  `project/autosave.files_to_autosave(editor.dirty_buffers(), <disk contents>)`,
  writes the dirty buffers, and also re-saves `<name>.blocks.json` (fetched via
  `bridge.get_workspace_json`). Manual Save and app-close also flush.
- **Compile/upload targeting** (`_start_job`): when a project is open, write the
  generated C++ to the project's `main_ino`, flush dirty companion files, and point
  `ArduinoJobWorker` at the **project folder** so `arduino-cli` compiles the whole
  sketch (generated main + companion files). With no project open, behaviour is
  unchanged (writes to `build/sparkide_sketch/`). This requires `ArduinoJobWorker` to
  accept an optional sketch-directory override instead of always using
  `app_config.SKETCH_FILE`.

### `ui/workers.py` change

- `ArduinoJobWorker.__init__` gains an optional `sketch_dir: Path | None = None`. When
  provided, it writes the generated code to `<sketch_dir>/<stem>.ino` and runs
  compile/upload against `sketch_dir`; when `None`, it uses the existing
  `app_config.SKETCH_FILE` path exactly as today. No new signals.

## Data flow

```
Blocks change → bridge.on_code_update → EditorTabs.update_code (Generated tab, RO)

New/Open Project → project.open_project → MainWindow._project
   → bridge.load_workspace(<name>.blocks.json)
   → EditorTabs.open_file(each companion file)  → editable CodeEditor tabs
   → recent.add_recent(root)

Edit companion file → CodeEditor.modificationChanged → tab '●' + dirty_changed
   → autosave QTimer → autosave.files_to_autosave(dirty, disk) → write files
                     → bridge.get_workspace_json → write <name>.blocks.json

Compile/Upload (project open) → write generated code to <project>/<name>.ino
   → flush dirty companion files → ArduinoJobWorker(sketch_dir=<project>)
   → arduino-cli compiles whole folder → stats/log as today
```

## Error handling

- **Open non-sketch folder:** `open_project` raises; `MainWindow` shows a warning and
  leaves current state untouched.
- **Create over existing folder / bad name:** `create_project` raises a clear error;
  surfaced via the existing `_show_warning`.
- **Missing recent project (folder deleted):** `load_recent` drops non-existent paths;
  selecting a stale entry shows a warning and prunes it.
- **Unsaved edits on close:** close-tab / close-app prompts to save dirty buffers
  (Save / Discard / Cancel).
- **Autosave write failure (permissions, disk):** logged to the Output panel as a
  warning; autosave keeps running; no crash, no data loss in the in-memory buffer.
- **No project open:** every project-only path no-ops gracefully and the v1.1.0
  block-only workflow remains fully functional.

## Testing

Pure-logic tests (no Qt):
- `tests/test_project_model.py` — `create_project`/`open_project`/`is_sketch_folder`,
  `Project.files()`/`companion_files()` tagging (main ino = generated), workspace and
  main-ino path derivation, error cases (bad name, non-sketch folder), using `tmp_path`.
- `tests/test_recent_projects.py` — MRU dedupe/cap/prune-missing, round-trip via a
  monkeypatched config dir.
- `tests/test_autosave.py` — `files_to_autosave` returns only dirty buffers; identical
  buffers excluded; new-file (not on disk) included.

Qt smoke tests (offscreen, following `tests/test_main_window.py` /
`test_serial_panel.py`):
- `tests/test_code_editor.py` — construct `CodeEditor`, set/get text, read-only
  toggle, dirty flag.
- `tests/test_editor_tabs.py` — `update_code`/`current_code` on the generated tab;
  `open_file`/`new_file`/`close_file`; `dirty_buffers()` reflects edits.
- `tests/test_main_window.py` (extend) — open a temp project, assert tabs populate and
  `_project` is set; compile path uses the project dir.

`tests/test_arduino_cli.py` / worker tests extend to cover `ArduinoJobWorker`'s
`sketch_dir` override (writes to the given folder).

JS suite is untouched (no Blockly changes in Phase 3).

## Documentation & release

- Bump `APP_VERSION` to `1.2.0` via `make bump-version`.
- `CHANGELOG.md`: new "Phase 3 — Editor Depth & Dual-Mode" Added section.
- `CLAUDE.md`: document the `project/` package, the `ui/editor/` package (replacing
  `code_panel.py`), the project/autosave/recent model, the `ArduinoJobWorker`
  `sketch_dir` override, and the block-authoritative interaction rule.
- `requirements.txt`: add `PyQt6-QScintilla`.

## Done when

A user can create or open a multi-file Arduino project, edit C++ companion files in a
real code editor with tabs, see their work autosaved, reopen recent projects, and
compile/upload the whole project (block-generated main sketch + hand-written files) —
with the block-only v1.1.0 workflow still intact and `make lint`, `make test`, and
`make test-js` all green.
