<div align="center">
  <h1>⚡ SparkIDE</h1>
  <p><strong>A lightweight, visual, block-based IDE for Arduino development on Linux.</strong></p>

  <p>
    <a href="https://github.com/harshverma27/SparkIDE/releases/latest"><img alt="Release" src="https://img.shields.io/github/v/release/harshverma27/SparkIDE?label=release&color=4ade80"></a>
    <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-4ade80.svg"></a>
    <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-blue">
    <img alt="Platform: Linux" src="https://img.shields.io/badge/platform-Linux-informational">
  </p>
</div>

SparkIDE brings the ease of Scratch-like block programming to Arduino development on Linux desktop environments. By wrapping Google Blockly in a fast, native PyQt6 shell, SparkIDE lets beginners drag and drop code blocks while instantly generating real Arduino C++ in a live preview panel — then compile and flash it to a connected board with one click.

---

## ✨ Features

- **Native Linux App**: Fast desktop application built with Python 3 and PyQt6.
- **Hybrid Lab Console UI**: A terminal/maker-lab inspired theme with a phosphor-green accent, monospace telemetry, and a focused workspace layout.
- **Live C++ Generation**: Watch your C++ code write itself in real time as you snap blocks together on the left panel.
- **Blockly Integration**: Offline-ready implementation of Google Blockly loaded via QtWebEngine — no internet connection required.
- **Multi-File Projects**: Folder-based Arduino projects (matching the `arduino-cli` sketch layout) with **New Project**, **Open Project**, **New File**, and **Open Recent** — the whole project folder is compiled in one shot when a project is open.
- **Dual-Mode Editor**: A QScintilla-powered code editor with syntax highlighting, line numbers, code folding, brace matching, and autocomplete. A read-only **Generated** tab shows live C++ from the blocks; additional companion `.h`/`.cpp`/`.ino` tabs are freely editable.
- **Autosave**: A 30-second timer silently writes dirty editor buffers and the block workspace JSON to disk.
- **Board Discovery**: Refresh connected Arduino boards and serial ports through `arduino-cli`.
- **One-Click Compile & Upload**: Compile or flash the selected board/port directly from the toolbar. Live build logs stream into the docked Output panel with flash/RAM usage pills.
- **Serial Monitor & Plotter**: Built-in serial console with baud-rate/line-ending selection; a live multi-series plotter (pyqtgraph) graphs numeric/CSV/`label:value` streams.
- **Boards Manager**: In-app **Tools ▸ Boards Manager** to search, install, update, and uninstall `arduino-cli` cores.
- **Rich Block Library**: 50+ custom blocks covering the full standard Arduino API:
  - **Structure**: `setup()` and `loop()`.
  - **Digital I/O**: `pinMode()`, `digitalWrite()`, `digitalRead()`, pin toggling, button edge cases, and LED blink routines.
  - **Analog I/O**: `analogRead()`, `analogWrite()`, `map()`, and `constrain()`.
  - **Time**: `millis()`, `micros()`, `delay()`, and `delayMicroseconds()`.
  - **Serial**: `Serial.begin()`, print, println, `Serial.read()`, `Serial.available()`, and `Serial.flush()`.
  - **Variables**: Dynamic typing support for `int`, `float`, `String`, and `bool`, including reassignment and compound operators (`+=`, `*=`).
  - **Logic & Math**: `if/else`, comparisons (==, >, <), boolean logic (AND/OR/NOT), arithmetic, modulo, absolute value, exponents, rounding, and min/max boundaries.
  - **Loops**: `for`, `while`, `do...while`, `break`, and `continue`.
  - **Functions**: User-defined functions with parameters and return values; prototypes emitted above `setup()`/`loop()` via multi-pass generation.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- A Linux desktop environment (X11 or XWayland)
- System-level Qt/XCB libraries (most desktop distros already have these):

  ```bash
  # Debian / Ubuntu
  sudo apt install python3-pip python3-venv libxcb-cursor0

  # Arch Linux
  sudo pacman -S python python-pip libxcb
  ```

### Quick Start (recommended)

SparkIDE ships with a `Makefile` that automates the full setup: virtual environment, Python dependencies, `arduino-cli`, and the AVR core needed for boards like the Uno/Nano.

```bash
git clone https://github.com/harshverma27/SparkIDE.git
cd SparkIDE
make setup   # one-time: creates .venv, installs deps, installs arduino-cli + AVR core
make run     # launches SparkIDE
```

### Manual Setup

If you'd rather manage things yourself:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Hardware compile/upload requires [`arduino-cli`](https://arduino.github.io/arduino-cli/) on your `PATH` with the `arduino:avr` core installed:

```bash
arduino-cli core update-index
arduino-cli core install arduino:avr
```

### Other Makefile targets

| Command              | Description                                              |
|----------------------|-----------------------------------------------------------|
| `make run`           | Launch SparkIDE                                            |
| `make test`          | Run the Python unit test suite with `pytest`               |
| `make install-cli`   | Install `arduino-cli` only                                  |
| `make install-core`  | Install the Arduino AVR core (`arduino:avr`)                |
| `make clean`         | Remove `.venv` and build artefacts                          |
| `make help`          | Show all available targets                                  |

---

## 🖱️ Usage

1. Launch SparkIDE with `make run`.
2. Drag blocks from the category toolbox on the left into the workspace.
3. Watch the generated Arduino C++ appear live in the **Generated** tab of the editor on the right.
4. Optionally create a project with **File ▸ New Project** to get a full sketch folder with editable companion files (`.h`, `.cpp`).
5. Connect your Arduino board over USB, then hit **↻** to refresh the board/port dropdowns.
6. Click **Compile** to build the sketch (or full project folder) with `arduino-cli`, or **Upload** to compile and flash it to the board.
7. Open **Tools ▸ Serial Monitor** to read/write the serial port; switch to the plotter tab to graph sensor data live.
8. Save your workspace with `Ctrl+S` — or let autosave handle it in the background every 30 seconds.

Build and upload logs stream live into the **Output** dock at the bottom of the window.

---

## 🏗️ Project Architecture

```text
SparkIDE/
├── Makefile                # Automation commands (make setup, run, test, clean)
├── requirements.txt        # Python dependencies
├── app_config.py           # Central config: version string, key paths
├── main.py                 # Application entry point, theme injection
├── blockly/                # HTML/JS assets for Google Blockly
│   ├── index.html          # Host page loaded inside QWebEngineView
│   ├── blocks/             # Custom block shape + colour definitions
│   ├── generators/         # Block → C++ code generators
│   └── vendor/             # Bundled Blockly core (offline-ready)
├── bridge/                 # PyQt ↔ JavaScript comms
│   └── channel.py          # QWebChannel bridge (code_changed, block_count_changed)
├── cli/                    # arduino-cli wrappers (Qt-free, testable)
│   ├── arduino_cli.py      # Board discovery, compile, upload, core management
│   └── serial_io.py        # Serial port helpers and plotter line parser
├── project/                # Project layer (Qt-free, testable)
│   ├── model.py            # Project / ProjectFile dataclasses, sketch-folder helpers
│   ├── recent.py           # Recent-projects MRU (JSON, capped at 10)
│   └── autosave.py         # Pure autosave diff helper
├── ui/                     # PyQt6 window modules
│   ├── main_window.py      # App shell (ToolbarMixin + StatusBarMixin composition)
│   ├── toolbar.py          # Top toolbar
│   ├── status_bar.py       # Telemetry strip (board/port/blocks/memory pills)
│   ├── workers.py          # QThread workers: BoardRefresh, ArduinoJob, SerialRead, CoreJob
│   ├── theme.py            # Design tokens + widget factory helpers
│   ├── editor/             # Dual-mode code editor
│   │   ├── code_editor.py  # QsciScintilla C++ editor (themed, line numbers, folding)
│   │   └── editor_tabs.py  # Tabbed host: read-only Generated tab + editable companion tabs
│   ├── log_panel.py        # Colour-coded build/upload output dock
│   ├── serial_panel.py     # Serial monitor + plotter (stacked widget)
│   ├── serial_plotter.py   # Live pyqtgraph multi-series plotter
│   └── board_manager.py    # Tools ▸ Boards Manager dialog
└── tests/                  # Pytest unit tests + Node.js generator tests
```

---

## 🧪 Testing

```bash
make test       # Python pytest suite
make test-js    # Node.js generator tests (node --test)
make lint       # ruff lint + format + ESLint
```

The test suite covers the `arduino-cli` wrapper, Blockly/bridge foundation, log panel behaviour, project model, and autosave logic.

---

## 🛣️ Roadmap

SparkIDE is evolving from a strong single-developer v1.0 into a **community-grade,
professional, cross-platform IDE** — balancing open-source maturity, feature depth,
and education reach. The full plan lives in
[`docs/superpowers/specs/2026-06-15-professional-ide-roadmap.md`](docs/superpowers/specs/2026-06-15-professional-ide-roadmap.md).

### Shipped

- [x] **v0.1 — Foundation**: Native PyQt6 shell, offline Blockly integration, 50+ Arduino blocks, live C++ generation, workspace save/load.
- [x] **v0.2 — Hardware Execution**: `arduino-cli` integration, board/port discovery, one-click compile & upload, live build logs.
- [x] **v1.0 — Hybrid Lab Console**: Full visual redesign with a terminal/maker-lab aesthetic, consolidated Blockly category palette, and a status-bar telemetry strip.
- [x] **Advanced Blocks — User-defined functions**: Functions toolbox category with parameters and return values, multi-pass C++ generation (prototypes + definitions emitted above `setup()`/`loop()`).
- [x] **Phase 1 — Foundation Hardening**: GitHub Actions CI, `ruff`/ESLint + pre-commit, expanded tests, contributor docs, release automation, `main_window.py` split into focused modules (`ui/theme.py`, `ui/toolbar.py`, `ui/status_bar.py`, `ui/workers.py`), central `app_config.py`.
- [x] **Phase 2 — Serial Monitor & Hardware UX**: Built-in serial console, live serial plotter (pyqtgraph), flash/RAM memory pills in the status bar, in-app **Boards Manager** for core install/update/uninstall.
- [x] **Phase 3 — Editor Depth & Dual-Mode** *(v1.2.0)*: QScintilla-powered editable editor with syntax highlighting, folding, and autocomplete; folder-based multi-file projects with New/Open/Recent and 30-second autosave; block-authoritative block↔code model with a read-only Generated tab and freely editable companion files; compile/upload targeting the whole project folder.

### Up next

- [ ] **Phase 4 — Cross-Platform Packaging** *(infra)*: Windows + macOS support, bundled `arduino-cli`, AppImage/Flatpak/MSI/dmg installers, signed CI builds, auto-update.
- [ ] **Phase 5 — Plugin Architecture** *(infra)*: a plugin API for third-party block packs, boards, and themes; Arduino library-manager integration.
- [ ] **Phase 6 — Expanded Block & Board Ecosystem** *(features)*: Servo, I2C/SPI, sensors, NeoPixel, ESP32/RP2040, non-blocking timers, interrupts, state machines.
- [ ] **Phase 7 — Education & Community Platform** *(features)*: in-app tutorials, example gallery, shareable projects, i18n, onboarding wizard, optional simulator.
- [ ] **Phase 8 — Polish, Stability & 2.0 Launch** *(infra + release)*: accessibility, performance profiling, opt-in crash reporting, docs site, community channels, **v2.0**.

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on setting up a development environment, coding conventions, and how to submit a pull request.

---

## 📄 License

SparkIDE is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- [Google Blockly](https://developers.google.com/blockly) — the visual block editor at the core of SparkIDE.
- [arduino-cli](https://github.com/arduino/arduino-cli) — official Arduino command-line toolchain used for compiling and uploading sketches.
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) — the native desktop UI framework.
- [QScintilla](https://riverbankcomputing.com/software/qscintilla/) — the embedded code editor widget used for the dual-mode editor.
- [pyqtgraph](https://www.pyqtgraph.org/) — fast scientific graphics library powering the serial plotter.
