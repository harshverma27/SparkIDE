<div align="center">
  <h1>⚡ SparkIDE</h1>
  <p><strong>A lightweight, visual, block-based IDE for Arduino development on Linux.</strong></p>
</div>

SparkIDE is designed to bring the ease of Scratch-like block programming to Arduino development on Linux desktop environments. By wrapping Google Blockly in a fast PyQt6 native shell, SparkIDE lets beginners drag and drop code blocks while instantly generating Arduino C++ in a live preview panel.

---

## ✨ Features (v0.1 — Foundation)

- **Native Linux App**: Fast desktop application built with Python 3 and PyQt6.
- **Deep Dark Theme**: Custom `One Dark` inspired UI for distraction-free coding, complete with custom styled docks, panels, and scrollbars.
- **Live C++ Generation**: Watch your C++ code write itself in real-time as you snap blocks together on the left panel.
- **Blockly Integration**: Offline-ready implementation of Google Blockly loaded via QtWebEngine.
- **State Saving**: Save and load Blockly workspaces to `.json` files (`Ctrl+S`, `Ctrl+O`).
- **Rich Block Library**: Includes **50+ custom blocks** covering the entire standard Arduino library:
  - **Structure**: `setup()` and `loop()`.
  - **Digital I/O**: `pinMode()`, `digitalWrite()`, `digitalRead()`, pin toggling, button edge cases, and LED blink routines.
  - **Analog I/O**: `analogRead()`, `analogWrite()`, `map()`, and `constrain()`.
  - **Time**: `millis()`, `micros()`, `delay()`, and `delayMicroseconds()`.
  - **Serial**: `Serial.begin()`, print, println, `Serial.read()`, `Serial.available()`, and `Serial.flush()`.
  - **Variables**: Dynamic typing support for `int`, `float`, `String`, and `bool`, including reassignment and compound operators (`+=`, `*=`).
  - **Logic & Math**: `if/else`, comparisons (==, >, <), boolean logic (AND/OR/NOT), arithmetic, modulo, absolute value, exponents, rounding, logic, and min/max boundaries.
  - **Loops**: `for`, `while`, `do...while`, `break`, and `continue`.

---

## 🚀 Installation & Setup

SparkIDE requires Python 3.10+ and uses a `Makefile` to handle dependencies automatically. You do **not** need to manually create virtual environments.

### 1. Requirements

Ensure you have system-level Qt/XCB requirements installed (most Linux distros have these included with desktop environments):
```bash
sudo apt install python3-pip python3-venv libxcb-cursor0
```

### 2. Run the App

Simply use the provided Makefile in the root directory:
```bash
make run
```
_This will automatically create a `.venv`, install all PyQt6 packages from `requirements.txt`, and launch the SparkIDE window._

---

## 🏗️ Project Architecture

```text
SparkIDE/
├── Makefile                # Automation commands (make run, make clean)
├── requirements.txt        # Python dependencies (PyQt6, PyQt6-WebEngine)
├── main.py                 # Application entry point, theme injection
├── blockly/                # HTML/JS assets for Google Blockly
│   ├── index.html          # Host page loaded inside QWebEngineView
│   ├── blocks/             # Definitions for block shapes + colours
│   └── generators/         # Translators from Blocks to C++ syntax
├── bridge/                 # PyQt <-> JavaScript comms
│   └── channel.py          # QWebChannel implementation
└── ui/                     # Native PyQt6 Window layout
    ├── main_window.py      # App shell, toolbar, menus
    ├── code_panel.py       # Live C++ editor with syntax highlighting
    └── log_panel.py        # Terminal-style output dock
```

---

## 🛣️ Roadmap (v0.2 — Execution Phase)

The GUI and Block definitions are complete. The next phase will connect the generated code to physical hardware.

- [ ] **Arduino-CLI Integration**: Wrapping the `arduino-cli` binary within Python (`cli/arduino_cli.py`).
- [ ] **Board Discovery**: Dynamic dropdown population of connected USB boards and serial ports.
- [ ] **One-Click Compiling**: Send the generated C++ to `arduino-cli compile` and stream compiler logs to the Output dock.
- [ ] **Seamless Uploading**: Flash the compiled binary directly to the Arduino via the IDE.
- [ ] **Advanced Blocks**: Add support for User-Defined Functions (requires multi-pass C++ generation), Servo motor libraries (`#include <Servo.h>`), and non-blocking timers.
