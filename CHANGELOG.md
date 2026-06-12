# Changelog

All notable changes to SparkIDE are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
