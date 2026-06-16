# Changelog

All notable changes to SparkIDE are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- User-defined function blocks: new "Functions" toolbox category (Blockly procedure blocks) supporting `int` parameters, return values, and early return. Function prototypes and definitions are emitted above `setup()`/`loop()` via multi-pass generation.
- Headless Node test harness (`tests/generate_code.js`) so pytest can assert real generated C++.
- **Phase 1 — Foundation Hardening:** GitHub Actions CI (lint, JS tests, pytest on Python 3.10–3.12) and tag-triggered release automation. `ruff` lint+format and ESLint via a `pre-commit` config. A `node:test` runner for the Blockly generators. Issue/PR templates, `SECURITY.md`, and a good-first-issues backlog. Expanded Python test coverage (cli, bridge, code panel, main-window smoke test).
- **Phase 2 — Serial Monitor & Hardware UX:** built-in serial monitor (pyserial) with baud-rate and line-ending selection, send-line input, and autoscroll; a live serial plotter (pyqtgraph) that graphs numeric/CSV/`label:value` streams; flash & RAM usage pills in the status bar parsed from `arduino-cli compile` output; and an in-app **Tools ▸ Boards Manager** to search, install, update, and uninstall Arduino cores. The serial monitor automatically releases the port during upload and reconnects afterward.
  - New runtime dependencies: `pyserial` and `pyqtgraph` (see `requirements.txt`).
- **Phase 3 — Editor Depth & Dual-Mode:** a QScintilla-based editable code mode (line numbers, code folding, brace matching, autocomplete) themed to the Hybrid Lab Console palette; folder-based multi-file Arduino projects with **New Project**, **Open Project**, **New File**, **Open Recent**, and timer-based autosave of edited files and the block workspace; a block-authoritative block↔code model where blocks own the read-only generated sketch while companion `.h`/`.cpp`/`.ino` files are freely editable; and compile/upload that builds the whole project folder when a project is open.
  - New runtime dependency: `PyQt6-QScintilla` (see `requirements.txt`).

### Changed
- **Phase 3:** replaced the read-only `CodePanel` with a tabbed `EditorTabs` editor (read-only **Generated** tab + editable companion-file tabs).
- **Phase 1 refactor:** split `ui/main_window.py` into focused modules — `ui/theme.py` (design tokens + widget factories, ending the previous triplication), `ui/toolbar.py`, `ui/status_bar.py`, `ui/workers.py` — and introduced a central `app_config.py` that is the single source of truth for the version string and key paths.

### Fixed
- Statement chains now generate code for every block: previously only the first block connected under `setup()`, `loop()`, or any statement input was emitted (the generator never followed next-block connections).

## [1.0.0] — 2026-06-12

### Added
- "Hybrid Lab Console" UI redesign: terminal/maker-lab aesthetic with a phosphor-green primary accent, amber warnings, and monospace typography for brand, code, and telemetry.
- Status-bar telemetry strip showing the selected board, port, and live Blockly workspace block count.
- Center / Zoom-to-fit / Reset workspace controls, moved from the Blockly page into the main toolbar.
- `CONTRIBUTING.md` and this `CHANGELOG.md`.

### Changed
- Consolidated Blockly's 8-category colour palette into 4 cohesive families (phosphor green, teal, amber, blue-gray).
- Removed Blockly's redundant in-page header/footer/quick-actions chrome in favour of the main application toolbar and status bar.
- Refreshed syntax highlighting, log panel, and code preview colours to match the new palette.

### Fixed
- Toolbox category hover/selection highlight no longer renders offset above the visible label.

## [0.2.0] — Hardware Execution

### Added
- `arduino-cli` integration (`cli/arduino_cli.py`) for board discovery, compiling, and uploading.
- Board and serial port discovery with a refresh control in the toolbar.
- One-click Compile and Upload, with live build/upload logs streamed to the Output dock.

## [0.1.0] — Foundation

### Added
- Native PyQt6 application shell with a dark theme.
- Offline Google Blockly integration via QtWebEngine and a QWebChannel bridge.
- 50+ custom Arduino blocks across 8 categories (Structure, Digital I/O, Analog I/O, Time, Serial, Variables, Logic & Math, Loops).
- Live C++ code generation and preview panel with syntax highlighting.
- Workspace save/load to `.json` (`Ctrl+S` / `Ctrl+O`).
