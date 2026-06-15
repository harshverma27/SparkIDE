# Phase 2 — Serial Monitor & Hardware UX: Design

**Date:** 2026-06-16
**Status:** Approved
**Owner:** Harsh Verma
**Roadmap:** `docs/superpowers/specs/2026-06-15-professional-ide-roadmap.md` (Phase 2)
**Target version:** 1.1.0

## Goal

Let a user compile, upload, watch live serial output, plot numeric streams, see
flash/RAM usage, and install/update Arduino cores — all without leaving SparkIDE.
This closes the most-requested hardware gaps and is the first user-facing feature
release on top of the Phase 1 foundation.

## Scope (four features, one sequenced release)

1. **Serial console** — pyserial-backed live monitor: connect/disconnect, baud-rate
   select, line-ending select, send-line input, autoscroll, clear.
2. **Serial plotter** — live line chart of numeric values parsed from the same
   stream (CSV / whitespace / `label:value`), rolling window, multi-series.
3. **Flash/RAM memory gauges** — parsed from `arduino-cli compile` output, shown in
   the status bar after each compile.
4. **In-app core/board management** — a dialog to list, search, install, update, and
   uninstall `arduino-cli` cores.

Out of scope for Phase 2: editable code mode, multi-file projects (Phase 3), and any
non-AVR board enablement beyond what core management exposes.

## Guiding constraints

- **Reuse existing patterns.** Backend work goes through `cli/` (synchronous,
  testable wrappers); long-running work goes through `QThread` subclasses in
  `ui/workers.py`; UI panels follow `ui/log_panel.py` and pull tokens from
  `ui/theme.py`; paths/identity live in `app_config.py`.
- **Keep `cli/` Qt-free and unit-testable.** Parsing logic (compile stats, serial
  numeric extraction, core JSON) lives in pure functions covered by pytest without a
  running Qt app or real hardware.
- **One serial port owner at a time.** The monitor and an upload cannot hold the
  port simultaneously; `MainWindow` coordinates a disconnect-before-upload /
  reconnect-after handoff.

## Architecture

### New dependencies (`requirements.txt`)

- `pyserial` — serial I/O.
- `pyqtgraph` — fast realtime plotting widget for the plotter.

### Backend (`cli/`)

**`cli/serial_io.py`** (new) — thin, Qt-free helpers:
- `list_serial_ports()` — wrap `serial.tools.list_ports` (used as a fallback /
  enrichment for the existing arduino-cli port discovery).
- `parse_plot_values(line: str) -> dict[str, float]` — pure function: extract a
  `{series_name: value}` mapping from one line. Supports `a,b,c` (positional →
  `ch0,ch1,...`), whitespace-separated, and `label:value`/`label=value` pairs.
  Non-numeric lines return `{}`.
- `BAUD_RATES`, `LINE_ENDINGS` constants.

**`cli/arduino_cli.py`** (extend):
- `@dataclass CompileStats` with `flash_used, flash_max, ram_used, ram_max` (ints,
  bytes) and `flash_pct` / `ram_pct` properties.
- `parse_compile_stats(text: str) -> CompileStats | None` — pure static method/
  function matching arduino-cli's "Sketch uses X bytes (Y%) of program storage …
  Maximum is Z bytes." and "Global variables use X bytes (Y%) of dynamic memory …"
  lines.
- Core management methods (each Qt-free, JSON or streaming):
  `core_list() -> list[CoreInfo]`, `core_search(query) -> list[CoreInfo]`,
  `core_install(id, callback)`, `core_upgrade(id, callback)`,
  `core_uninstall(id, callback)` — `core_*` install/upgrade/uninstall reuse the
  existing `_run_streaming` machinery; list/search reuse `_run_json`.
- `@dataclass CoreInfo` with `id, installed, latest, name`.

### Workers (`ui/workers.py`)

- **`SerialReadWorker(QThread)`** — owns a `serial.Serial`; loops reading lines and
  emits `line_received(str)`; emits `connection_error(str)` on failure and
  `connection_closed()` on stop. Owns a `QMutex`-guarded `send(text, line_ending)`
  for writes and a cooperative `stop()`.
- **`CoreJobWorker(QThread)`** — runs a single core install/upgrade/uninstall,
  emitting `line(str, str)` and `finished(bool, str)` (mirrors `ArduinoJobWorker`).
- **`ArduinoJobWorker`** (extend) — capture compile stdout, run
  `parse_compile_stats`, and emit a new `stats(object)` signal (CompileStats or
  None) alongside the existing `finished`.

### UI panels

- **`ui/serial_panel.py`** (new) — `SerialPanel(QWidget)`:
  - Header: Connect/Disconnect button, baud combo, line-ending combo, autoscroll
    toggle, Clear, and a Monitor/Plotter view toggle.
  - Body: a `QStackedWidget` holding the text monitor (read-only `QPlainTextEdit`,
    styled like `LogPanel`) and the plotter.
  - Footer: `QLineEdit` + Send (enabled only while connected).
  - Exposes signals `connect_requested(port, baud)`, `disconnect_requested()`,
    `send_requested(text)`; slots `append_output(line)`, `set_connected(bool)`.
  - Holds no `serial.Serial` itself — MainWindow wires it to a `SerialReadWorker`.
- **`ui/serial_plotter.py`** (new) — `SerialPlotter(QWidget)` wrapping a
  `pyqtgraph.PlotWidget`; `feed(line)` calls `parse_plot_values` and appends to
  per-series rolling deques (configurable max points), drawing one curve per series
  with theme colours. `clear()` resets.
- **`ui/board_manager.py`** (new) — `BoardManagerDialog(QDialog)`: search field,
  table of cores (id / name / installed / latest), Install/Update/Uninstall buttons
  driving a `CoreJobWorker`, and a small embedded log area. Opened from a new
  **Tools ▸ Boards Manager…** menu action.

### Wiring (`ui/main_window.py`)

- `_build_serial_dock()` — add `SerialPanel` in a `QDockWidget` ("Serial"),
  tabified with the existing "Output" dock (`tabifyDockWidget`).
- Connect SerialPanel signals to create/stop a `SerialReadWorker`; feed
  `line_received` to both the monitor text view and the plotter.
- **Port handoff:** in `_start_job` for uploads, if the serial worker is connected
  on the target port, stop it first, run the job, then reconnect after
  `_on_job_finished` (remember prior connection state).
- Status bar: add Flash/RAM pills (reuse `theme.status_pill` / `pill_html`); a new
  `_update_memory(stats)` slot connected to `ArduinoJobWorker.stats` formats
  `used/max (pct%)` or `—` when unknown.
- Menu: add a **Tools** menu with **Boards Manager…**.

### Status-bar gauges

Phase 2 keeps the gauges as text pills (`FLASH: 2,408/32,256 (7%)`,
`RAM: 184/2,048 (9%)`) with the accent colour shifting green→amber→red by
percentage. No new custom-painted widget — consistent with the existing pill
telemetry and cheap to test.

## Data flow

```
Board → USB → SerialReadWorker.readline ─emit line_received→ MainWindow
   → SerialPanel.append_output (text view)
   → SerialPlotter.feed → parse_plot_values → rolling buffers → curves

SerialPanel send box ─send_requested→ MainWindow → SerialReadWorker.send → Board

arduino-cli compile stdout → ArduinoJobWorker → parse_compile_stats
   ─emit stats→ MainWindow._update_memory → status-bar pills

Boards Manager dialog → CoreJobWorker → arduino-cli core install/upgrade/uninstall
   ─emit line→ dialog log;  on finish → refresh core list (+ board dropdown)
```

## Error handling

- **Port busy / disappeared:** `SerialReadWorker` emits `connection_error`; panel
  returns to disconnected state and the log shows the reason.
- **Upload while connected:** automatic disconnect/reconnect; if reconnect fails,
  surface a warning and leave the panel disconnected (no crash).
- **arduino-cli missing:** already handled by `ArduinoCLI.is_available()`; core
  methods and the dialog show the same "not found in PATH" message.
- **Malformed serial data:** `parse_plot_values` returns `{}` for non-numeric lines;
  the plotter ignores them while the text monitor still shows them raw.
- **No compile stats in output:** `parse_compile_stats` returns `None`; pills show
  `—`.

## Testing

Pure-logic tests (no Qt, no hardware):
- `tests/test_serial_io.py` — `parse_plot_values` across CSV / whitespace /
  `label:value` / non-numeric; `list_serial_ports` with a monkeypatched
  `list_ports`.
- `tests/test_arduino_cli.py` (extend) — `parse_compile_stats` on real arduino-cli
  output samples (with and without stats); `core_list`/`core_search` JSON parsing
  with sample fixtures via the existing subprocess-mocking style.

Qt smoke tests (offscreen, following `tests/test_main_window.py` /
`test_log_panel.py`):
- `tests/test_serial_panel.py` — construct `SerialPanel`, toggle connected state,
  emit `send_requested`, switch Monitor/Plotter.
- `tests/test_board_manager.py` — construct `BoardManagerDialog` with a stub CLI.

JS suite is untouched (no Blockly changes in Phase 2).

## Documentation & release

- Bump `APP_VERSION` to `1.1.0` via `make bump-version`.
- `CHANGELOG.md`: new "Phase 2 — Serial Monitor & Hardware UX" Added section.
- `CLAUDE.md`: document `cli/serial_io.py`, the new panels/workers, and the serial
  port-handoff rule.
- `requirements.txt`: move `pyserial` out of the "not needed yet" comment and add
  `pyqtgraph`.

## Done when

A user can connect to a board's serial port, watch and send lines, plot numeric
output live, see flash/RAM usage after each compile, and install/update a core from
a dialog — with `make lint`, `make test`, and `make test-js` all green.
