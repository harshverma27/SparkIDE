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
- **State Saving**: Save and load Blockly workspaces to `.json` files (`Ctrl+S`, `Ctrl+O`).
- **Board Discovery**: Refresh connected Arduino boards and serial ports through `arduino-cli`.
- **One-Click Compile**: Write the generated C++ to a valid sketch folder and compile it through `arduino-cli`.
- **One-Click Upload**: Compile and flash the selected board/port directly from the SparkIDE toolbar.
- **Live Build Logs**: Stream compiler and uploader output into the docked Output panel.
- **Rich Block Library**: Includes **50+ custom blocks** covering the entire standard Arduino library:
  - **Structure**: `setup()` and `loop()`.
  - **Digital I/O**: `pinMode()`, `digitalWrite()`, `digitalRead()`, pin toggling, button edge cases, and LED blink routines.
  - **Analog I/O**: `analogRead()`, `analogWrite()`, `map()`, and `constrain()`.
  - **Time**: `millis()`, `micros()`, `delay()`, and `delayMicroseconds()`.
  - **Serial**: `Serial.begin()`, print, println, `Serial.read()`, `Serial.available()`, and `Serial.flush()`.
  - **Variables**: Dynamic typing support for `int`, `float`, `String`, and `bool`, including reassignment and compound operators (`+=`, `*=`).
  - **Logic & Math**: `if/else`, comparisons (==, >, <), boolean logic (AND/OR/NOT), arithmetic, modulo, absolute value, exponents, rounding, and min/max boundaries.
  - **Loops**: `for`, `while`, `do...while`, `break`, and `continue`.

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
3. Watch the generated Arduino C++ appear live in the **Generated Sketch** panel on the right.
4. Connect your Arduino board over USB, then hit **↻** to refresh the board/port dropdowns.
5. Click **Compile** to build the sketch with `arduino-cli`, or **Upload** to compile and flash it to the board.
6. Save your workspace with `Ctrl+S` and reopen it later with `Ctrl+O`.

Build and upload logs stream live into the **Output** dock at the bottom of the window.

---

## 🏗️ Project Architecture

```text
SparkIDE/
├── Makefile                # Automation commands (make setup, run, test, clean)
├── requirements.txt        # Python dependencies (PyQt6, PyQt6-WebEngine, pytest)
├── main.py                 # Application entry point, theme injection
├── blockly/                # HTML/JS assets for Google Blockly
│   ├── index.html          # Host page loaded inside QWebEngineView
│   ├── blocks/              # Definitions for block shapes + colours
│   ├── generators/          # Translators from Blocks to C++ syntax
│   └── vendor/               # Bundled Blockly core (offline-ready)
├── bridge/                  # PyQt <-> JavaScript comms
│   └── channel.py            # QWebChannel implementation
├── cli/                     # arduino-cli wrapper
│   └── arduino_cli.py         # Board discovery, compile, upload
├── ui/                      # Native PyQt6 window layout
│   ├── main_window.py        # App shell, toolbar, menus, telemetry strip
│   ├── code_panel.py          # Live C++ editor with syntax highlighting
│   └── log_panel.py           # Terminal-style output dock
└── tests/                   # Pytest unit tests
```

---

## 🧪 Testing

```bash
make test
```

This runs the full `pytest` suite covering the `arduino-cli` wrapper, Blockly/bridge foundation, and log panel behaviour.

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

### The road to 2.0 — 8 phases

Each phase is a shippable release. Infrastructure and feature phases are interleaved
so every release is both stable and exciting.

- [ ] **Phase 1 — Foundation Hardening** *(infra)*: GitHub Actions CI, `ruff`/`black` + pre-commit, expanded tests, contributor docs and templates, release automation, and a refactor of `main_window.py` into focused modules.
- [ ] **Phase 2 — Serial Monitor & Hardware UX** *(features)*: built-in serial console with baud selection, serial plotter, flash/RAM memory gauges, in-app core/board management.
- [ ] **Phase 3 — Editor Depth & Dual-Mode** *(features)*: editable text/code mode alongside blocks, multi-file projects with tabs, recent-files, autosave.
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
