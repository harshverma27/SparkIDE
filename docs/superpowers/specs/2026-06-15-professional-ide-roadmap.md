# SparkIDE → Professional Community IDE: 8-Phase Roadmap

**Date:** 2026-06-15
**Status:** Approved
**Owner:** Harsh Verma

## Goal

Evolve SparkIDE from a strong, single-developer Linux v1.0 into a **community-grade,
professional visual IDE for Arduino development**. The roadmap advances three goals
**in balance**:

1. **Open-source maturity** — make the project safe and inviting to contribute to.
2. **Feature depth** — close the gap with Arduino IDE 2 / Thonny-class tooling.
3. **Education reach** — keep the Scratch-like, beginner-first experience central.

## Guiding decisions

These constraints shape every phase:

- **Cross-platform desktop** — expand beyond Linux to Windows and macOS with proper
  packaged installers. Broaden community reach.
- **Dual-mode** — preserve the block-first experience for beginners while adding a
  text/advanced mode and pro features so the IDE *grows with the user*.
- **Interleaved cadence** — alternate infrastructure-hardening phases with
  user-facing feature phases, so every release is both stable and exciting.

## Starting point (v1.0)

A ~3,300-LOC PyQt6 + Blockly app with a clean three-layer bridge
(`bridge/` ⇄ QWebChannel ⇄ `blockly/`), an `arduino-cli` wrapper (`cli/`), native
UI panels (`ui/`), 50+ blocks plus user-defined functions, live C++ generation,
workspace save/load, one-click compile/upload, and a small pytest + Node test suite.
Gaps: no CI, no linting/formatting, no release automation, read-only code panel,
Linux-only, hard-coded blocks, AVR-only.

---

## The 8 Phases

Each phase is a shippable release with its own version bump, CHANGELOG entry, and
tests. Phases are ordered for dependency and momentum; later phases assume the
infrastructure laid by earlier ones.

### Phase 1 — Foundation Hardening & Project Hygiene *(infra)*

Make the project safe for outside contributors.

- GitHub Actions CI: run pytest + the Node generator harness + linting on every PR.
- Adopt `ruff` + `black` (Python) and a JS linter, wired into a `pre-commit` config.
- Expand test coverage; add a JS unit-test runner for generators/blocks.
- Issue and PR templates, `CODE_OF_CONDUCT.md`, a `SECURITY.md`, and a labelled
  "good first issue" backlog.
- Release automation (tagged releases → changelog → artifacts).
- Refactor the 623-LOC `ui/main_window.py` into focused modules (toolbar, workers,
  telemetry/status, menu/actions) and introduce a central app-config module.

**Done when:** a contributor can open a PR and CI validates it end-to-end with no
manual setup.

### Phase 2 — Serial Monitor & Hardware UX *(features)*

Close the most-requested hardware gaps.

- Built-in serial console (pyserial) with baud-rate selection, send line, autoscroll.
- Serial plotter for numeric streams.
- Flash/RAM memory gauges parsed from `arduino-cli` compile output.
- In-app core/board management (install/update cores from the UI).

**Done when:** a user can compile, upload, watch serial output, and see memory usage
without leaving SparkIDE.

### Phase 3 — Editor Depth & Dual-Mode *(features)*

Let advanced users graduate beyond blocks.

- Editable text/code mode (QScintilla or embedded Monaco) alongside the block view.
- Multi-file projects with tabs, recent-files, and autosave.
- Clear block ↔ code interaction model (block-authoritative with a read/inspect code
  view first; explore safe round-trip later).

**Done when:** a user can manage a multi-file project and edit C++ directly.

### Phase 4 — Cross-Platform Packaging & Distribution *(infra)*

Ship to everyone, easily.

- Windows + macOS support (path handling, Qt/WebEngine quirks, signing).
- Bundle `arduino-cli` so users need no separate install.
- Installers: AppImage/Flatpak (Linux), MSI/exe (Windows), dmg (macOS).
- CI build matrix producing signed release artifacts.
- In-app auto-update or update notifications.

**Done when:** a non-technical user on any of the three OSes can download and run
SparkIDE in one step.

### Phase 5 — Extensibility / Plugin Architecture *(infra)*

Turn block contributions into a community activity, not a core-team chore.

- A plugin API for third-party **block packs** (block defs + generators + toolbox
  entries + theme colours) loaded without editing core files.
- Board/architecture plugins and theme plugins.
- Integration with the Arduino library manager.
- Re-express selected first-party blocks as the reference plugin pack.

**Done when:** someone can publish a block pack and a user can install it without
touching SparkIDE source.

### Phase 6 — Expanded Block & Board Ecosystem *(features)*

Grow capability on top of the plugin foundation.

- Library blocks: Servo, I2C (Wire), SPI, common sensors, NeoPixel/addressable LEDs.
- Multi-architecture: ESP32/ESP8266 and RP2040 support.
- Non-blocking timers, interrupts, and simple state-machine blocks.

**Done when:** users can build real multi-peripheral projects across major board
families.

### Phase 7 — Education & Community Platform *(features)*

Make SparkIDE a place to learn and share.

- In-app tutorials/lessons and a searchable example gallery.
- Shareable projects (export/import bundles; optional shareable links).
- Internationalisation / localisation (i18n) of UI and block text.
- First-run onboarding wizard.
- Optional simulator/preview for running without hardware (scoped, may be deferred).

**Done when:** a teacher can run a classroom session and students can share projects.

### Phase 8 — Polish, Stability & 2.0 Launch *(infra + release)*

Land the plane.

- Accessibility pass (keyboard nav, contrast, screen-reader labels).
- Performance profiling and optimisation (large workspaces, WebEngine startup).
- Opt-in crash/error reporting.
- A documentation site and refreshed marketing/landing page.
- Community channels (GitHub Discussions / Discord) and contributor recognition.
- **v2.0 release.**

**Done when:** SparkIDE ships a polished, documented, cross-platform v2.0 with an
active contributor community.

---

## Sequencing rationale

- **1 before everything** — contributions are unsafe without CI and a clean
  structure.
- **2 and 3** deliver immediate, visible user value while the foundation is fresh.
- **4 before 5/6** — packaging widens the audience that benefits from new blocks.
- **5 before 6** — build the plugin system, then grow the ecosystem through it.
- **7 and 8** capitalise on a mature, extensible, cross-platform base.

## Out of scope (for now)

- Cloud accounts / hosted backend (sharing stays file/link-based until demanded).
- Mobile/web ports.
- A full hardware simulator is a *stretch* item inside Phase 7, not a commitment.

## Success metrics

- CI green on every PR; contributor PRs merged from outside the core team.
- Installable in one step on Linux, Windows, and macOS.
- At least one community-published plugin.
- Documented v2.0 release with serial monitor, dual-mode editor, and multi-board
  support.
