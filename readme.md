# SparkIDE — Product Requirements Document

**Version:** 1.0  
**Author:** Harsh  
**Status:** Pre-development  
**Last Updated:** March 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Problem Statement](#2-problem-statement)
3. [Features](#3-features)
4. [Scope (v0.1)](#4-scope-v01)
5. [Technical Architecture](#5-technical-architecture)
6. [Development Timeline](#6-development-timeline)
7. [Risks & Mitigations](#7-risks--mitigations)
8. [Success Metrics](#8-success-metrics)
9. [Open Source Strategy](#9-open-source-strategy)

---

## 1. Overview

SparkIDE is a native Linux desktop app that lets you program Arduino boards by dragging and dropping visual blocks — similar to Scratch — and instantly see the generated C++ code on the right panel. You click upload and it flashes the board. No terminal, no toolchain confusion, no blank file staring at you.

| Field | Value |
|---|---|
| Timeline | 2 weeks (v0.1) |
| Stack | Python · PyQt6 · Google Blockly |
| Platform | Linux Desktop (primary: Arch Linux) |
| License | MIT (planned) |
| Hardware | Arduino Uno / Nano |

### Vision statement

> The only modern, actively maintained, native Linux desktop app for visual Arduino programming.

---

## 2. Problem Statement

### For beginners

Getting started with Arduino requires writing C++ immediately — there is no gradual on-ramp. New users copy-paste code they don't understand, get lost in compilation errors, and give up. A visual block system removes this barrier entirely.

### For the Linux community

Most beginner-friendly Arduino tools are Windows-first or web-only. Linux users get the Arduino IDE (clunky) or PlatformIO (overkill for beginners). A native PyQt6 desktop app on Linux is a genuine gap.

### For the open source ecosystem

Every block-based Arduino tool that existed is now abandoned. The last meaningful update to ArduBlock was in 2014. SparkIDE can own this space.

### Competitive landscape

| Tool | Status | Problem |
|---|---|---|
| Arduino IDE | Active | Text-only, no visual blocks |
| PlatformIO (VS Code) | Active | Powerful but not beginner-friendly |
| ArduBlock | Dead (2014) | Outdated, plugin for old Arduino IDE |
| S4A (Scratch for Arduino) | Dead | Web-only, limited hardware support |
| MicroBlocks | Active | Targets MicroPython, not Arduino C++ |

---

## 3. Features

### v0.1 Features (2-week target)

#### 🧱 Visual Block Editor
Drag-and-drop Scratch-style blocks powered by Google Blockly embedded in a PyQt6 `QWebEngineView`. Blocks map to real Arduino functions and are organized into logical categories.

#### ⚡ Live C++ Preview
As you place blocks, the right panel updates in real-time with the generated C++ code. Syntax highlighted, read-only, always in sync with the block workspace.

#### 📤 One-Click Upload
Compiles and uploads to connected Arduino via `arduino-cli`. Board and port are selectable via dropdowns. Build logs shown inline below the editor.

#### 🔍 Core Arduino Blocks
Covers the fundamental operations:
- `setup()` and `loop()` containers
- `pinMode(pin, mode)`
- `digitalWrite(pin, value)`
- `digitalRead(pin)`
- `delay(ms)`
- `if / else` logic
- Variables (int, bool)
- `Serial.begin(baud)` and `Serial.print(value)`

#### ⚠️ Compile Error Display
When compilation fails, errors from `arduino-cli` are parsed and shown in plain English below the code panel — not as raw compiler output.

#### 💾 Save / Load Workspace
Export the block workspace as JSON and reload it later. Supports `Ctrl+S` and `Ctrl+O` keyboard shortcuts.

---

### v0.2 Features (post-launch)

#### 🧩 Sensor & Advanced Blocks
Servo, I2C, `analogRead`, PWM, DHT11/22, ultrasonic distance sensor blocks.

#### 📊 Flash & RAM Usage Gauges
After compilation, display flash usage % and SRAM usage % as a simple gauge bar. Warn when approaching limits.

#### 🔌 Built-in Serial Monitor
Real-time `Serial.print` output from the board. Baud rate selector included.

#### 🛠️ Custom Block Creator
Let power users define new blocks with custom C++ snippets.

---

## 4. Scope (v0.1)

### In scope

- PyQt6 app shell with Blockly in `QWebEngineView`
- Core Arduino blocks (10–12 block types)
- Live C++ code generation panel
- Compile + upload via `arduino-cli`
- Compile error display (parsed, not raw)
- Board and port selector dropdowns
- Save / load block workspace as JSON

### Out of scope for v0.1

- Sensor-specific blocks (servo, DHT, I2C)
- Serial monitor
- Flash / RAM usage gauges
- Wiring safety warnings
- Custom block creator
- App installer / packaging (`.deb`, AUR, AppImage)
- Windows / macOS support

---

## 5. Technical Architecture

### Technology choices

| Layer | Technology | Reasoning |
|---|---|---|
| UI Framework | `PyQt6` | Native Linux desktop, Python bindings, mature |
| Block Editor | Google Blockly (via `QWebEngineView`) | Industry-standard drag-and-drop engine — don't reinvent it |
| Code Generation | Blockly JS generator → C++ output | Blockly has a built-in generator API; write custom Arduino rules on top |
| Compile + Upload | `arduino-cli` | Official CLI tool, board management, subprocess-friendly |
| PyQt ↔ Blockly bridge | `QWebChannel` | Bidirectional Python ↔ JavaScript communication |
| Syntax Highlighting | `QScintilla` or static HTML render | Read-only C++ preview, lightweight |
| Serial comms (v0.2) | `pyserial` | Standard Python serial library |

### Architecture overview

The app has three logical layers:

```
┌─────────────────────────────────────────┐
│           PyQt6 Desktop App             │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  Blockly     │  │  C++ Preview     │ │
│  │  (WebView)   │  │  Panel           │ │
│  └──────┬───────┘  └────────▲─────────┘ │
│         │  QWebChannel       │           │
│         ▼                    │           │
│  ┌─────────────────────────────────────┐ │
│  │      Python Bridge Layer            │ │
│  │  (receives block changes, emits     │ │
│  │   generated C++ string)             │ │
│  └────────────────┬────────────────────┘ │
│                   │                      │
│  ┌────────────────▼────────────────────┐ │
│  │      arduino-cli subprocess         │ │
│  │  compile → upload → log stream      │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Blockly layer** — lives in a `QWebEngineView` loading a local HTML page with Blockly's JS library. Handles all drag-and-drop UI.

**Python bridge layer** — uses `QWebChannel` to receive block-change events from JavaScript and pass back generated C++ strings.

**CLI layer** — Python subprocess wrapper around `arduino-cli compile` and `arduino-cli upload`, with stdout/stderr streamed into a log widget.

### Project folder structure

```
sparkide/
├── main.py                  # App entry point
├── ui/
│   ├── main_window.py       # PyQt6 main window
│   ├── code_panel.py        # C++ preview panel
│   └── log_panel.py         # Build log widget
├── blockly/
│   ├── index.html           # Local Blockly HTML page
│   ├── blocks/              # Custom Arduino block definitions (JS)
│   └── generators/          # C++ code generators (JS)
├── bridge/
│   └── channel.py           # QWebChannel Python side
├── cli/
│   └── arduino_cli.py       # arduino-cli subprocess wrapper
├── assets/
│   └── icons/
├── requirements.txt
└── README.md
```

---

## 6. Development Timeline

### Phase 1 — Foundation (Days 1–6)

**Day 1–2: Project scaffold + Blockly shell**
- Set up PyQt6 app window
- Embed `QWebEngineView` loading a local Blockly HTML page
- Confirm blocks render correctly
- Set up GitHub repo, README skeleton, folder structure

**Day 3–4: QWebChannel bridge**
- Establish bidirectional Python ↔ JavaScript communication
- When a block changes in Blockly, Python receives the generated code string
- Test with a single dummy block end-to-end

**Day 5–6: Core Arduino blocks**
- Define custom Blockly block definitions for all 10 core blocks
- Write C++ code generator for each block
- Verify generated output is valid C++ for a blink sketch

---

### Phase 2 — Core Features (Days 7–12)

**Day 7–8: Live C++ preview panel**
- Split main window: Blockly left, C++ panel right
- Code updates on every block change event
- Add syntax highlighting
- Make panel read-only

**Day 9–10: arduino-cli integration**
- Detect connected boards and ports
- Add board + port selector dropdowns
- Wire up Compile button (`arduino-cli compile`)
- Wire up Upload button (`arduino-cli upload`)
- Stream stdout/stderr into log panel

**Day 11–12: Error handling + save/load**
- Parse `arduino-cli` error output → show readable messages
- Implement workspace save (Blockly XML/JSON → file)
- Implement workspace load
- Add keyboard shortcuts (`Ctrl+S`, `Ctrl+O`)

---

### Phase 3 — Polish & Release (Days 13–14)

**Day 13–14: Polish + v0.1 release**
- UI polish: toolbar icons, status bar (board / port / connection status)
- End-to-end test on real Arduino Uno (blink LED → confirm it works)
- Write README with screenshots and demo GIF
- Tag `v0.1` on GitHub and write release notes

---

## 7. Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| `arduino-cli` toolchain issues (board not detected, wrong port, driver issues on Linux) | High | Test the full compile+upload flow on Day 9, before any UI polish |
| `QWebChannel` bridge complexity (PyQt6 ↔ Blockly JS can be fiddly) | Medium | Days 3–4 dedicated entirely to this; use AI to debug |
| Blockly customization learning curve (custom block defs and generators) | Medium | Use AI to scaffold block definitions; Blockly docs are solid |
| Scope creep (temptation to add sensors, serial monitor in v0.1) | Medium | Strict v0.1 scope list; everything else goes to backlog |
| `QWebEngineView` performance (Blockly in a WebView may feel laggy) | Low | Blockly is lightweight; should be fine on modern hardware |

---

## 8. Success Metrics

A v0.1 is considered successful when all of the following are true:

- **End-to-end demo works:** Place blink blocks → click upload → Arduino Uno blinks
- **Core block count:** ≥ 10 distinct Arduino block types functional
- **Code generation accuracy:** Generated C++ compiles without errors for all core blocks
- **Upload speed:** Compiles and uploads to Uno in under 30 seconds
- **GitHub release:** Tagged `v0.1` with README, screenshots, and demo GIF
- **Open source ready:** MIT license, `CONTRIBUTING.md`, clean commit history

---

## 9. Open Source Strategy

### Repository setup

- Host on GitHub under your personal account
- Clean `README.md` with a demo GIF at the top — non-negotiable for discoverability
- GitHub topics: `arduino`, `blockly`, `linux`, `pyqt6`, `visual-programming`, `embedded-systems`
- MIT license from day one

### Launch plan (after v0.1)

Post in the following communities with a working demo GIF:
- r/arduino
- r/learnprogramming
- r/linux
- Arduino Community Forum
- Hacker News (Show HN)

### Differentiation message

> *"SparkIDE is the only modern, actively maintained, native Linux desktop app for visual Arduino programming. Drag blocks, see real C++, click upload."*

### Community growth

Keep a public roadmap in the README. After launch, let the community vote on v0.2 priorities. This creates early contributors and makes the project feel alive from day one.

---

*SparkIDE PRD v1.0 · March 2026 · Subject to revision as development begins*
