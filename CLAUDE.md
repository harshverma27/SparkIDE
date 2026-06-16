# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

SparkIDE is a native Linux desktop app (Python 3 + PyQt6) that wraps Google Blockly in a `QWebEngineView` to provide Scratch-like visual Arduino programming. Blocks generate real Arduino C++ live, which can be compiled/uploaded to a board via `arduino-cli`.

## Commands

```bash
make setup   # one-time: creates .venv, installs requirements.txt, installs arduino-cli + arduino:avr core
make run     # .venv/bin/python main.py
make test    # .venv/bin/python -m pytest tests/ -v
make clean   # removes .venv, __pycache__, .pytest_cache, build/
```

Run a single test: `.venv/bin/python -m pytest tests/test_arduino_cli.py::test_list_boards_parses_detected_ports -v`

There is no separate lint/format command configured.

## Architecture

### Three-layer bridge: PyQt ⇄ QWebChannel ⇄ Blockly (JS)

- `main.py` — entry point, applies the dark Fusion palette, launches `MainWindow`.
- `ui/main_window.py` — the app shell (toolbar, splitter, dock, status bar). Loads `blockly/index.html` into a `QWebEngineView` and wires up a `QWebChannel`.
- `bridge/channel.py` — `Bridge(QObject)`, registered as `bridge` on the web channel.
  - JS → Python: `bridge.on_code_update(cppString)` emits `code_changed` (→ `CodePanel.update_code`); `bridge.on_block_count_update(int)` emits `block_count_changed` (→ status bar telemetry).
  - Python → JS: `bridge.load_workspace(json)` and `bridge.get_workspace_json(callback)` call `window.loadWorkspace()` / `window.getWorkspaceJson()` via `page.runJavaScript()`.
- `blockly/index.html` — hosts the Blockly workspace. Defines `TOOLBOX` (category list + colours), `WORKSPACE_THEME`, injects the workspace, and exposes globals the Python side calls via `runJavaScript`: `window.loadWorkspace`, `window.getWorkspaceJson`, `window.clearWorkspace`, `window.centerWorkspace`, `window.zoomToFitWorkspace`. On every non-UI workspace change it regenerates code and calls `bridge.on_code_update` / `bridge.on_block_count_update`.
- `blockly/blocks/arduino_blocks.js` — custom block definitions (50+ blocks, `setColour(...)` per category family).
- `blockly/generators/arduino_generator.js` — `ArduinoGenerator` (a `Blockly.CodeGenerator`), one `forBlock['<type>']` function per block, returning either a statement string or `[expression, ORDER_*]` tuple. Defines C++ operator-precedence constants (`ORDER_ATOMIC`, `ORDER_ADDITION`, etc.) used when wrapping expressions in parens.
- `blockly/vendor/` — bundled Blockly core/blocks/locale so the app works fully offline (`index.html` must never load from `unpkg.com` or any CDN — enforced by `tests/test_blockly_foundation.py`).

When adding a new block: define it in `arduino_blocks.js`, add a matching `forBlock` generator in `arduino_generator.js`, and register it under a category in the `TOOLBOX` object in `blockly/index.html` using one of the existing category colours (140 green / 185 teal / 42 amber / 222 blue-gray — see `WORKSPACE_THEME.blockStyles`). `tests/test_blockly_foundation.py` asserts every block type has a generator.

### Compile/upload flow

- `cli/arduino_cli.py` — `ArduinoCLI` is a synchronous subprocess wrapper around `arduino-cli` (`board list`, `compile`, `upload`), returning `BoardOption` dataclasses and streaming output lines via a `LogCallback`. It also parses compile output for flash/RAM usage (`parse_compile_stats` → `CompileStats`) and manages cores (`core_list`/`core_search`/`core_install`/`core_upgrade`/`core_uninstall` → `CoreInfo`) for the Boards Manager.
- `cli/serial_io.py` — Qt-free serial helpers: `parse_plot_values` (parses numeric/CSV/`label:value` lines for the plotter), `list_serial_ports`, `BAUD_RATES`, and `LINE_ENDINGS`.
- These `QThread` subclasses live in `ui/workers.py` and are driven by `ui/main_window.py`:
  - `BoardRefreshWorker` — populates board/port dropdowns.
  - `ArduinoJobWorker` — writes the current generated C++ to a sketch `.ino`, then runs `compile` (and `upload` if requested), emitting `line` (log output), `stats` (`CompileStats`, consumed by the status-bar memory pills), and `finished` signals consumed by `LogPanel` and the status bar. With no project open it targets `build/sparkide_sketch/sparkide_sketch.ino`; when a project is open `MainWindow` passes `sketch_dir=<project root>` so the whole folder (generated sketch + companion files) is compiled in place.
  - `SerialReadWorker` — reads a serial port on a background thread and exposes a thread-safe `send()` for writing back to the port.
  - `CoreJobWorker` — runs `arduino-cli core install`/`upgrade`/`uninstall` jobs for the Boards Manager.

### App shell modules

`ui/main_window.py` is composition-only: `MainWindow(ToolbarMixin, StatusBarMixin, QMainWindow)`. The pieces it composes:
- `ui/toolbar.py` (`ToolbarMixin`) — builds the top toolbar.
- `ui/status_bar.py` (`StatusBarMixin`) — builds the telemetry status strip and its update helpers.
- `ui/workers.py` — the background `QThread` workers (above).
- `app_config.py` (repo root) — central config: app name/version, repo URL, key paths (`BLOCKLY_HTML`, `BUILD_DIR`, `SKETCH_FILE`, `USER_CONFIG_DIR`), window sizes. No Qt imports, safe for tests.

### Projects & editor (Phase 3)

- `project/` — Qt-free project layer (testable without a running Qt app, like `cli/`):
  - `project/model.py` — `Project`/`ProjectFile` frozen dataclasses for **sketch-folder projects** (a folder whose main `.ino` matches the folder name, Arduino-style). `create_project`/`open_project`/`is_sketch_folder`; `companion_files()` returns the editable `.h`/`.cpp`/extra-`.ino` files; `workspace_path` is the saved Blockly JSON. Project names are validated `^[A-Za-z0-9_]+$`.
  - `project/recent.py` — recent-projects MRU stored as JSON under `USER_CONFIG_DIR` (`load_recent`/`add_recent`/`clear_recent`; dedupes, caps at 10, prunes missing folders).
  - `project/autosave.py` — pure `files_to_autosave(buffers, on_disk)` returning only the buffers whose text differs from disk.
- `ui/editor/` — the dual-mode editor (replaces the old `ui/code_panel.py`):
  - `ui/editor/code_editor.py` (`CodeEditor`) — themed `QsciScintilla` C++ editor (QsciLexerCPP, line numbers, brace matching, folding, autocomplete).
  - `ui/editor/editor_tabs.py` (`EditorTabs`) — tabbed host with a **read-only "Generated" tab** (driven live by `bridge.code_changed` → `update_code`; `current_code()` feeds compile/upload) plus **editable companion-file tabs** (`open_file`/`new_file`/`close_file`/`dirty_buffers`/`mark_saved`, dirty `●` markers, `dirty_changed` signal).
- **Block-authoritative block↔code model:** blocks own the generated sketch, which is shown read-only — there is no code→block round-trip. Companion `.h`/`.cpp`/`.ino` files are freely editable. `MainWindow` opens/creates projects (`_on_new_project`/`_on_open_project`/`_on_open_recent`/`_on_new_file`), populates `EditorTabs`, and runs a 30s `QTimer` autosave (`_on_autosave`) that writes dirty buffers (via `files_to_autosave`) and the workspace JSON to disk.

### UI panels & design tokens

- `ui/editor/` — the tabbed code editor (see *Projects & editor* above); replaces the former read-only `ui/code_panel.py`.
- `ui/log_panel.py` — colour-coded build/upload log (`_COLOURS` dict keyed by level: info/warning/error/success/dim).
- `ui/serial_panel.py` (`SerialPanel`) — serial monitor + plotter in a `QStackedWidget`, with baud-rate/line-ending selectors, a send-line input, and autoscroll; backed by `SerialReadWorker`.
- `ui/serial_plotter.py` (`SerialPlotter`) — live multi-series plot (pyqtgraph) driven by `cli/serial_io.parse_plot_values`.
- `ui/board_manager.py` (`BoardManagerDialog`) — Tools ▸ Boards Manager… dialog to search, install, update, and uninstall `arduino-cli` cores via `CoreJobWorker`.
- Visual theme is the **"Hybrid Lab Console"** design (terminal/maker-lab aesthetic, phosphor-green primary accent `#4ade80`, amber warning `#f0a93e`, monospace `FONT_MONO` for brand/code/telemetry). The colour/font tokens and the widget-factory helpers live in **`ui/theme.py`**; `main_window.py`, the `ui/editor/` modules, and `log_panel.py` import from it (some panels alias tokens to local names, e.g. `BG_DEEP as BG_PANEL`). Retune the palette in one place. The same palette is mirrored in `blockly/index.html`'s CSS `:root` vars and `WORKSPACE_THEME`/`TOOLBOX` colours. The design rationale lives in `docs/superpowers/specs/2026-06-12-ui-redesign-design.md`.
- Status bar acts as a telemetry strip (board/port/block-count pills, flash/RAM usage pills via `_update_memory`, + a glowing status indicator via `QGraphicsDropShadowEffect`).

### Serial port handoff

Only one owner of the serial port at a time: `MainWindow` disconnects the serial monitor (`SerialReadWorker`) before starting an upload and reconnects it after `_on_job_finished`, so `arduino-cli upload` can claim the port without contention.

## Versioning

`APP_VERSION` in `app_config.py` is the single source of truth; it flows to the QApplication version, the About dialog, and the log `WELCOME_TEXT`. Bump it with `make bump-version VERSION=X.Y.Z`, then update `CHANGELOG.md` and tag `vX.Y.Z` (see `docs/RELEASING.md`, automated by `.github/workflows/release.yml`). See `CHANGELOG.md` for release history and `CONTRIBUTING.md` for contribution conventions (commit prefixes: `feat:`, `fix:`, `docs:`, `ui:`, `refactor:`, `test:`).

## Quality gates

`make lint` (ruff lint+format + ESLint), `make test` (pytest), and `make test-js` (`node --test`) all run in CI (`.github/workflows/ci.yml`) on every PR. Run them locally before pushing; `make dev-setup` installs the pre-commit hooks.
