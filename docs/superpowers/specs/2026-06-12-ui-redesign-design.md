# SparkIDE UI Redesign — Hybrid Lab Console

**Date:** 2026-06-12
**Status:** Approved
**Scope:** Visual + layout restyle of the existing PyQt6 shell and embedded Blockly workspace. No new features, no functional/behavioral changes — colors, typography, shape, and a few layout simplifications only.

## Goals

- Replace the current blue/navy "One Dark" look with a **terminal/CRT-inspired maker-lab aesthetic**: near-black graphite base, phosphor-green primary accent, amber secondary accent, subtle (not heavy) retro touches.
- Make the Blockly canvas feel like part of the same device as the surrounding shell, instead of a separate "rainbow" Blockly default theme.
- Simplify the Blockly panel's redundant chrome (it currently duplicates app-level toolbar/status info).

## Non-goals

- No new features, panels, or interactions.
- No changes to application logic, bridge, CLI wrapper, or code generation.
- No literal/heavy CRT effects (scanlines across every panel, blinking cursors, ASCII borders) — "subtle nods only".

---

## 1. Design tokens

### Palette

| Token | Old value | New value | Use |
|---|---|---|---|
| `BG_VOID` | `#0d1117` | `#0a0f0c` | Outermost window background (near-black, faint green tint) |
| `BG_DARK` | `#111827` | `#0d1310` | Menu bar, status bar, deep recesses |
| `BG_MID` | `#172033` | `#121a16` | Mid-tone background (window gradient) |
| `BG_PANEL` | `#0f1728` | `#101512` | Panel/card backgrounds (code panel, log panel, Blockly stage) |
| `BG_RAISED` | `#1f2a3d` | `#171f1b` | Inputs, secondary buttons, comboboxes |
| `BORDER` | `#263246` | `#22322a` | Default panel/divider borders |
| `BORDER_HI` | `#425474` | `#3c5347` | Hover/active borders |
| `ACCENT_PRIMARY` (phosphor green) | `#2f9e6f` / `#2b7fff` | `#4ade80` | Primary actions, "live"/active states, success, Upload button fill |
| `ACCENT_PRIMARY_HI` | `#277f5a` / `#2367d1` | `#3fc270` | Hover/pressed state for primary accent |
| `ACCENT_AMBER` | `#f4b942` | `#f0a93e` | Warnings, highlights — **not** used for button branding |
| `ACCENT_ERROR` | `#e06c75` | `#f0654a` | Errors |
| `TEXT_MAIN` | `#eef3ff` | `#e4f0e8` | Primary text (slight green-white tint) |
| `TEXT_MID` | `#b2bdd2` | `#93a89c` | Secondary text/labels |
| `TEXT_DIM` | `#7e8aa5` | `#5c7468` | Tertiary/dim text, timestamps |

`ACCENT_BLU` / `ACCENT_BLU_HI` (bright blue, currently used for the Upload button and Blockly bridge accents) are retired entirely.

### Typography

- **Monospace** (`JetBrains Mono`, fallback `Fira Code`, fallback system mono): brand wordmark, toolbar labels, buttons, telemetry strip, menu items, code panel, log panel.
- **Sans** (`Inter`, current default): tooltips, `QMessageBox` dialog body text — anything with longer prose.

### Shape & texture

- Corner radii reduced: outer frame / dock edges `8px` (was `18px`); buttons, pills, comboboxes `6px` (was `10px`).
- A faint repeating-gradient scanline texture on the outermost window background only (very low opacity).
- Soft `text-shadow` glow limited to: the status-bar "live" indicator dot and its label. Not applied anywhere else.

---

## 2. Layout & component changes

### Toolbar (`ui/main_window.py::_build_toolbar`)

- Brand "SparkIDE" → monospace bold, new `TEXT_MAIN`.
- Tagline → terminal-prompt style: `> visual arduino studio`, `TEXT_DIM`.
- Board/Port selector groups: keep current structure (uppercase mono label + combo + refresh button), restyle to new tokens.
- **New**: icon-button group for Center / Reset / Zoom-to-fit, added to the toolbar (these move here from the Blockly panel's removed header — see section 3).
- Compile button: outlined/ghost style using `ACCENT_PRIMARY`.
- Upload button: solid fill using `ACCENT_PRIMARY` / `ACCENT_PRIMARY_HI` (replaces the old `ACCENT_BLU`).
- Amber is not used on either button — reserved for warning/status meaning only.

### Status bar → "telemetry strip" (`ui/main_window.py::_build_status_bar`, `_status_pill`)

- Board/Port pills become LED-readout chips: small square indicator + monospace text, e.g. `BOARD: UNO`, `PORT: ttyACM0`. New tokens, `6px` radius.
- **New** block-count readout, e.g. `BLOCKS: 7`, populated via the bridge/JS the same way `blockCount` is currently tracked in `blockly/index.html`.
- Right-side status indicator (`● Idle` / `● Ready` / `● Working` / `● Failed`) keeps its colored dot + text but gets the subtle glow treatment and monospace type. Status colors map to the new palette (`#4e9a51`→`ACCENT_PRIMARY`, `#e5c07b`→`ACCENT_AMBER`, `#e06c75`→`ACCENT_ERROR`, unchanged semantics).

### Central workspace

- `blockly/index.html`: remove `.topbar` (title/subtitle/pills) and `.footer-bar` entirely. `.workspace-stage` (toolbox + canvas) fills the panel edge-to-edge inside the existing `.workspace-shell` frame (which gets the new `8px` radius / new tokens). The `.quick-actions` buttons (Center/Reset/Zoom-to-fit) are removed from the HTML — equivalent actions now live in the main toolbar (section above) and call the existing `workspace.scrollCenter()` / `clearWorkspace()` / `workspace.zoomToFit()` via the bridge or `runJavaScript`.
- `ui/code_panel.py`: header (title chip, "Live sync" dot, line count, Copy button) restyled to new tokens + monospace. Structure unchanged. `_window_stylesheet`/editor background → `BG_PANEL`.
- Splitter handle (`ui/main_window.py::_build_central`) restyled to new `BORDER`/`BORDER_HI`.

### Log/output dock (`ui/log_panel.py`)

- Structure unchanged (header with title + Clear button, scrollable colored log).
- Level color retune: `success`→`ACCENT_PRIMARY` (`#4ade80`), `warning`→`ACCENT_AMBER` (`#f0a93e`), `error`→`ACCENT_ERROR` (`#f0654a`), `info`→muted teal-gray (`#7fa89c`), `dim`→darker green-gray (`#3f4f48`).
- Header restyled to new tokens + monospace.

### Code panel syntax highlighting (`ui/code_panel.py::CppHighlighter`)

Retune the existing One Dark-derived highlight colors to sit on the new `BG_PANEL` background while keeping distinct hues for readability (keywords, builtins, strings, numbers, comments each stay visually distinct — exact hex values chosen during implementation to satisfy contrast against `#101512`).

---

## 3. Blockly canvas theme

### Category color remapping (`blockly/blocks/arduino_blocks.js`, `blockly/index.html` TOOLBOX + `WORKSPACE_THEME`)

Current blocks use 7 distinct Blockly hues (30, 120, 160, 210, 230, 270, 330) spread across 9 toolbox categories — a "rainbow" look disconnected from the new palette. These consolidate into 4 muted families, each tuned (via hue + the theme's saturation/brightness) to read as desaturated greens/teals/ambers/blue-grays against the graphite background rather than default vivid Blockly colors:

| Family | Categories | Current hue(s) |
|---|---|---|
| Phosphor green | Structure, Loops | 120 |
| Teal/cyan | Digital I/O, Analog I/O, Serial | 210, 160, 270 |
| Amber | Time, Math | 30, 230 |
| Muted blue-gray | Logic, Variables | 210, 330 |

Every `setColour(...)` call in `arduino_blocks.js` is updated to its new family's hue, and the `TOOLBOX` category `colour` values in `index.html` are updated to match so toolbox icons/headers agree with the blocks inside them.

### Workspace chrome (`blockly/index.html` `WORKSPACE_THEME` + CSS)

- `workspaceBackgroundColour`, `toolboxBackgroundColour`, `flyoutBackgroundColour` → `BG_VOID`/`BG_PANEL` tokens (currently `#0b1322`/`#0f1728`).
- Toolbox tree row hover/selected state → `ACCENT_PRIMARY` (currently blue `rgba(43,127,255,...)`).
- Grid line color → dark green-tinted graphite (currently `#22314b`).
- Scrollbar handles, flyout button background → new tokens.
- Insertion marker stays amber (`ACCENT_AMBER`) — good contrast against green/teal blocks, no change needed.
- `.workspace-shell` border-radius → `8px` (was `18px`), matching the new shape tokens.

---

## 4. Verification

- Run `make run` to launch the PyQt6 app and visually confirm: toolbar, telemetry strip, Blockly canvas (toolbox + category colors), code panel (incl. syntax highlighting contrast), and log dock all render with the new palette/typography and no leftover blue/navy artifacts.
- Confirm the four Blockly category color families remain visually distinguishable from each other.
- Confirm removing the Blockly topbar/footer doesn't break `generateAndSend`, `updateWorkspaceMeta`, or the bridge connection (block count now reported to the telemetry strip instead of the removed `#blockCount` pill).
- If the session environment is headless, fall back to code review + asking the user to manually confirm the visuals.

## Files affected

- `ui/main_window.py` — design tokens, toolbar, telemetry strip, splitter/frame styling
- `ui/code_panel.py` — header styling, syntax highlighter palette, editor background
- `ui/log_panel.py` — header styling, log level colors
- `blockly/index.html` — CSS variables, `WORKSPACE_THEME`, TOOLBOX category colours, removal of topbar/footer/quick-actions
- `blockly/blocks/arduino_blocks.js` — `setColour(...)` remapping per category family
