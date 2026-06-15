# Phase 2 — Serial Monitor & Hardware UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a serial monitor, serial plotter, flash/RAM memory gauges, and in-app core/board management so a user can compile, upload, watch serial, and manage cores without leaving SparkIDE.

**Architecture:** Backend parsing/IO stays Qt-free and unit-tested in `cli/`; long-running work runs in `QThread` workers in `ui/workers.py`; UI panels follow `ui/log_panel.py` and pull tokens from `ui/theme.py`. The serial monitor lives in a bottom dock tabified with "Output"; `MainWindow` owns the single `SerialReadWorker` and hands the port off around uploads.

**Tech Stack:** Python 3.10+, PyQt6, pyserial, pyqtgraph, pytest (offscreen Qt), arduino-cli.

**Spec:** `docs/superpowers/specs/2026-06-16-phase-2-serial-hardware-ux-design.md`

---

## File Structure

- Create `cli/serial_io.py` — Qt-free serial helpers: `parse_plot_values`, `list_serial_ports`, `BAUD_RATES`, `LINE_ENDINGS`.
- Modify `cli/arduino_cli.py` — add `CompileStats` + `parse_compile_stats`; `CoreInfo` + `core_list/core_search/core_install/core_upgrade/core_uninstall`.
- Modify `ui/workers.py` — add `SerialReadWorker`, `CoreJobWorker`; extend `ArduinoJobWorker` with a `stats` signal.
- Create `ui/serial_plotter.py` — `SerialPlotter(QWidget)` over pyqtgraph.
- Create `ui/serial_panel.py` — `SerialPanel(QWidget)` (monitor + plotter stack + send box).
- Create `ui/board_manager.py` — `BoardManagerDialog(QDialog)`.
- Modify `ui/main_window.py` — serial dock, port handoff, memory pills, Tools menu.
- Modify `ui/status_bar.py` — Flash/RAM pills + `_update_memory`.
- Modify `requirements.txt`, `app_config.py` (version), `CHANGELOG.md`, `CLAUDE.md`.
- Tests: `tests/test_serial_io.py`, `tests/test_serial_panel.py`, `tests/test_board_manager.py`; extend `tests/test_arduino_cli.py`.

Each numbered Task below is a self-contained unit suitable for one subagent. Tasks are ordered by dependency; run them in order.

---

## Task 1: Dependencies + serial backend (`cli/serial_io.py`)

**Files:**
- Modify: `requirements.txt`
- Create: `cli/serial_io.py`
- Test: `tests/test_serial_io.py`

- [ ] **Step 1: Add dependencies.** In `requirements.txt`, replace the `# pyserial ...` placeholder block with active deps:

```
# Serial monitor: read Serial.print() output from the board
pyserial

# Realtime serial plotter widget
pyqtgraph
```

Then `.venv/bin/pip install -r requirements.txt`.

- [ ] **Step 2: Write failing tests** in `tests/test_serial_io.py`:

```python
import pytest
from cli.serial_io import parse_plot_values, list_serial_ports, BAUD_RATES


def test_parse_plot_values_csv_positional():
    assert parse_plot_values("12,3.5,-7") == {"ch0": 12.0, "ch1": 3.5, "ch2": -7.0}


def test_parse_plot_values_whitespace():
    assert parse_plot_values("12 3.5 -7") == {"ch0": 12.0, "ch1": 3.5, "ch2": -7.0}


def test_parse_plot_values_labelled():
    assert parse_plot_values("temp:21.5 hum=40") == {"temp": 21.5, "hum": 40.0}


def test_parse_plot_values_mixed_skips_non_numeric():
    assert parse_plot_values("temp:21.5 status:ok") == {"temp": 21.5}


def test_parse_plot_values_non_numeric_returns_empty():
    assert parse_plot_values("hello world") == {}
    assert parse_plot_values("") == {}


def test_baud_rates_include_common():
    assert 9600 in BAUD_RATES and 115200 in BAUD_RATES


def test_list_serial_ports_uses_pyserial(monkeypatch):
    class FakePort:
        def __init__(self, device): self.device = device
    monkeypatch.setattr(
        "cli.serial_io.comports", lambda: [FakePort("/dev/ttyUSB0"), FakePort("/dev/ttyACM0")]
    )
    assert list_serial_ports() == ["/dev/ttyACM0", "/dev/ttyUSB0"]
```

- [ ] **Step 3: Run, expect fail.** `.venv/bin/python -m pytest tests/test_serial_io.py -v` → ImportError.

- [ ] **Step 4: Implement `cli/serial_io.py`:**

```python
"""cli/serial_io.py — Qt-free serial helpers (ports, line parsing)."""
from __future__ import annotations

import re

from serial.tools.list_ports import comports

BAUD_RATES = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 74880, 115200, 230400, 250000]
# label -> bytes appended to outgoing lines
LINE_ENDINGS = {"No line ending": b"", "Newline": b"\n", "Carriage return": b"\r", "Both NL & CR": b"\r\n"}

_LABELLED = re.compile(r"([A-Za-z_]\w*)\s*[:=]\s*(-?\d+(?:\.\d+)?)")
_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")


def list_serial_ports() -> list[str]:
    """Sorted list of serial device paths discovered by pyserial."""
    return sorted(p.device for p in comports())


def parse_plot_values(line: str) -> dict[str, float]:
    """Extract {series: value} from one serial line. {} if no numbers found.

    Supports `label:value`/`label=value`, and positional CSV/whitespace numbers
    (named ch0, ch1, ...). Labelled pairs take priority; if any exist, only they
    are returned.
    """
    line = line.strip()
    if not line:
        return {}
    labelled = {m.group(1): float(m.group(2)) for m in _LABELLED.finditer(line)}
    if labelled:
        return labelled
    tokens = re.split(r"[,\s]+", line)
    values: dict[str, float] = {}
    for i, tok in enumerate(tokens):
        if _NUMBER.match(tok):
            values[f"ch{i}"] = float(tok)
    return values
```

- [ ] **Step 5: Run, expect pass.** `.venv/bin/python -m pytest tests/test_serial_io.py -v`

- [ ] **Step 6: Lint + commit.** `make lint` then:
```bash
git add requirements.txt cli/serial_io.py tests/test_serial_io.py
git commit -m "feat: add Qt-free serial helpers (ports + plot parsing)"
```

---

## Task 2: Compile-stats parsing (`cli/arduino_cli.py`)

**Files:**
- Modify: `cli/arduino_cli.py`
- Test: `tests/test_arduino_cli.py`

- [ ] **Step 1: Write failing tests** appended to `tests/test_arduino_cli.py`:

```python
from cli.arduino_cli import parse_compile_stats

_SAMPLE = """Sketch uses 2408 bytes (7%) of program storage space. Maximum is 32256 bytes.
Global variables use 184 bytes (8%) of dynamic memory, leaving 1864 bytes for local variables. Maximum is 2048 bytes."""


def test_parse_compile_stats_full():
    stats = parse_compile_stats(_SAMPLE)
    assert stats.flash_used == 2408 and stats.flash_max == 32256
    assert stats.ram_used == 184 and stats.ram_max == 2048
    assert stats.flash_pct == 7  # 2408/32256 rounded


def test_parse_compile_stats_none_when_absent():
    assert parse_compile_stats("nothing useful here") is None
```

- [ ] **Step 2: Run, expect fail.** `.venv/bin/python -m pytest tests/test_arduino_cli.py -k compile_stats -v`

- [ ] **Step 3: Implement** in `cli/arduino_cli.py` — add the dataclass and a module-level function (also expose as needed):

```python
@dataclass(frozen=True)
class CompileStats:
    flash_used: int
    flash_max: int
    ram_used: int
    ram_max: int

    @property
    def flash_pct(self) -> int:
        return round(100 * self.flash_used / self.flash_max) if self.flash_max else 0

    @property
    def ram_pct(self) -> int:
        return round(100 * self.ram_used / self.ram_max) if self.ram_max else 0


_FLASH_RE = re.compile(r"Sketch uses (\d+) bytes.*?Maximum is (\d+) bytes", re.DOTALL)
_RAM_RE = re.compile(r"Global variables use (\d+) bytes.*?Maximum is (\d+) bytes", re.DOTALL)


def parse_compile_stats(text: str) -> "CompileStats | None":
    flash = _FLASH_RE.search(text)
    ram = _RAM_RE.search(text)
    if not flash or not ram:
        return None
    return CompileStats(
        flash_used=int(flash.group(1)), flash_max=int(flash.group(2)),
        ram_used=int(ram.group(1)), ram_max=int(ram.group(2)),
    )
```

Note: the RAM line also contains "Maximum is N bytes", and the flash line precedes it. Because `_FLASH_RE` anchors on "Sketch uses" and `_RAM_RE` on "Global variables use", each non-greedily matches its own trailing "Maximum is". Verify on the sample.

- [ ] **Step 4: Run, expect pass.** `.venv/bin/python -m pytest tests/test_arduino_cli.py -k compile_stats -v`

- [ ] **Step 5: Lint + commit.**
```bash
git add cli/arduino_cli.py tests/test_arduino_cli.py
git commit -m "feat: parse flash/RAM usage from arduino-cli compile output"
```

---

## Task 3: Core management backend (`cli/arduino_cli.py`)

**Files:**
- Modify: `cli/arduino_cli.py`
- Test: `tests/test_arduino_cli.py`

- [ ] **Step 1: Write failing tests.** Follow the existing subprocess-mocking style already used in `tests/test_arduino_cli.py` (inspect it first to match the fixture/monkeypatch approach). Cover:
  - `core_list()` parses `arduino-cli core list --format json` output into `CoreInfo(id, name, installed, latest)`.
  - `core_search("esp32")` parses `core search --format json`.
  Sample JSON for `core list`:

```python
_CORE_LIST_JSON = '{"platforms":[{"id":"arduino:avr","installed_version":"1.8.6","latest_version":"1.8.6","releases":{"1.8.6":{"name":"Arduino AVR Boards"}}}]}'
```

(arduino-cli JSON shape varies by version; the parser must read `id`, `installed_version`, `latest_version`, and a human name, tolerating missing keys. Write the test against the shape above and code defensively.)

- [ ] **Step 2: Run, expect fail.**

- [ ] **Step 3: Implement** in `cli/arduino_cli.py`:

```python
@dataclass(frozen=True)
class CoreInfo:
    id: str
    name: str
    installed: str = ""
    latest: str = ""

    @property
    def upgradable(self) -> bool:
        return bool(self.installed) and bool(self.latest) and self.installed != self.latest
```

Add methods on `ArduinoCLI`:

```python
def core_list(self) -> list[CoreInfo]:
    data = self._run_json(["core", "list", "--format", "json"])
    return self._parse_cores(data.get("platforms", data) if isinstance(data, dict) else data)

def core_search(self, query: str) -> list[CoreInfo]:
    data = self._run_json(["core", "search", query, "--format", "json"])
    return self._parse_cores(data.get("platforms", data) if isinstance(data, dict) else data)

def core_install(self, core_id: str, callback: LogCallback) -> bool:
    return self._run_streaming(["core", "install", core_id], callback)

def core_upgrade(self, core_id: str, callback: LogCallback) -> bool:
    return self._run_streaming(["core", "upgrade", core_id], callback)

def core_uninstall(self, core_id: str, callback: LogCallback) -> bool:
    return self._run_streaming(["core", "uninstall", core_id], callback)

@staticmethod
def _parse_cores(platforms) -> list["CoreInfo"]:
    cores = []
    for p in platforms or []:
        pid = p.get("id", "")
        if not pid:
            continue
        installed = p.get("installed_version", "") or p.get("installed", "")
        latest = p.get("latest_version", "") or p.get("latest", "")
        releases = p.get("releases", {})
        name = p.get("name") or next(
            (r.get("name") for r in releases.values() if isinstance(r, dict) and r.get("name")), pid
        )
        cores.append(CoreInfo(id=pid, name=name, installed=installed, latest=latest))
    return sorted(cores, key=lambda c: c.id)
```

- [ ] **Step 4: Run, expect pass.**

- [ ] **Step 5: Lint + commit.**
```bash
git add cli/arduino_cli.py tests/test_arduino_cli.py
git commit -m "feat: add arduino-cli core list/search/install/upgrade/uninstall"
```

---

## Task 4: Workers — SerialReadWorker, CoreJobWorker, stats signal

**Files:**
- Modify: `ui/workers.py`
- Test: `tests/test_workers.py` (create; pure-signal tests where feasible)

- [ ] **Step 1: Extend `ArduinoJobWorker`** to emit compile stats. Add `stats = pyqtSignal(object)`. The current `ArduinoCLI.compile` streams lines but doesn't return text; collect compile stdout in the worker by wrapping the callback:

```python
from cli.arduino_cli import ArduinoCLI, ArduinoCLIError, parse_compile_stats
...
def run(self):
    ...
    captured: list[str] = []
    def cb(line: str, level: str):
        captured.append(line)
        self.line.emit(line, level)
    cli = ArduinoCLI()
    if self._action == "compile":
        ok = cli.compile(self._fqbn, BUILD_DIR, cb)
    else:
        ok = cli.compile(self._fqbn, BUILD_DIR, cb)
        if ok:
            ok = cli.upload(self._fqbn, self._port, BUILD_DIR, cb)
    self.stats.emit(parse_compile_stats("\n".join(captured)))
    self.finished.emit(ok, ...)
```

- [ ] **Step 2: Add `SerialReadWorker(QThread)`:**

```python
from PyQt6.QtCore import QMutex, QMutexLocker
import serial
from cli.serial_io import LINE_ENDINGS


class SerialReadWorker(QThread):
    line_received = pyqtSignal(str)
    connection_error = pyqtSignal(str)

    def __init__(self, port: str, baud: int, parent=None):
        super().__init__(parent)
        self._port_name = port
        self._baud = baud
        self._serial = None
        self._mutex = QMutex()
        self._running = True

    def run(self):
        try:
            self._serial = serial.Serial(self._port_name, self._baud, timeout=0.2)
        except (serial.SerialException, OSError) as exc:
            self.connection_error.emit(str(exc))
            return
        while self._running:
            try:
                raw = self._serial.readline()
            except (serial.SerialException, OSError) as exc:
                if self._running:
                    self.connection_error.emit(str(exc))
                break
            if raw:
                self.line_received.emit(raw.decode("utf-8", errors="replace").rstrip("\r\n"))
        with QMutexLocker(self._mutex):
            if self._serial and self._serial.is_open:
                self._serial.close()

    def send(self, text: str, ending_label: str = "Newline") -> None:
        with QMutexLocker(self._mutex):
            if self._serial and self._serial.is_open:
                self._serial.write(text.encode("utf-8") + LINE_ENDINGS.get(ending_label, b"\n"))

    def stop(self) -> None:
        self._running = False
        self.wait(1000)
```

- [ ] **Step 3: Add `CoreJobWorker(QThread)`** mirroring `ArduinoJobWorker`'s signal shape:

```python
class CoreJobWorker(QThread):
    line = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, action: str, core_id: str, parent=None):
        super().__init__(parent)
        self._action = action
        self._core_id = core_id

    def run(self):
        cli = ArduinoCLI()
        fn = {"install": cli.core_install, "upgrade": cli.core_upgrade,
              "uninstall": cli.core_uninstall}[self._action]
        ok = fn(self._core_id, self.line.emit)
        self.finished.emit(ok, f"{self._action} {'complete' if ok else 'failed'}: {self._core_id}")
```

- [ ] **Step 4: Test** in `tests/test_workers.py` — verify `parse_compile_stats` wiring by unit-testing the capture logic is non-trivial under a real QThread; instead assert the signals exist and `SerialReadWorker.send` is a no-op when `_serial is None` (no exception). Keep tests offscreen-safe:

```python
import os; os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from ui.workers import SerialReadWorker, CoreJobWorker, ArduinoJobWorker

def test_serial_worker_send_no_port_is_safe():
    w = SerialReadWorker("/dev/null", 9600)
    w.send("hi")  # _serial is None → no raise

def test_workers_have_expected_signals():
    assert hasattr(ArduinoJobWorker, "stats")
    assert hasattr(SerialReadWorker, "line_received")
    assert hasattr(CoreJobWorker, "finished")
```

- [ ] **Step 5: Run + lint + commit.** `.venv/bin/python -m pytest tests/test_workers.py -v`
```bash
git add ui/workers.py tests/test_workers.py
git commit -m "feat: add serial read + core job workers, compile stats signal"
```

---

## Task 5: Serial plotter widget (`ui/serial_plotter.py`)

**Files:**
- Create: `ui/serial_plotter.py`
- Test: `tests/test_serial_plotter.py`

- [ ] **Step 1: Implement** `SerialPlotter(QWidget)`:

```python
"""ui/serial_plotter.py — live multi-series plot of numeric serial values."""
from collections import defaultdict, deque

import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from cli.serial_io import parse_plot_values
from ui import theme

_CURVE_COLOURS = [theme.ACCENT_GRN, theme.ACCENT_AMBER, "#5aa9e6", theme.ACCENT_ERROR, "#b07fff"]


class SerialPlotter(QWidget):
    def __init__(self, max_points: int = 500, parent=None):
        super().__init__(parent)
        self._max_points = max_points
        self._buffers: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self._curves: dict[str, pg.PlotDataItem] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        pg.setConfigOptions(antialias=True)
        self._plot = pg.PlotWidget(background=theme.BG_PANEL)
        self._plot.showGrid(x=True, y=True, alpha=0.15)
        self._plot.addLegend()
        layout.addWidget(self._plot)

    def feed(self, line: str) -> None:
        values = parse_plot_values(line)
        if not values:
            return
        for name, value in values.items():
            self._buffers[name].append(value)
            if name not in self._curves:
                colour = _CURVE_COLOURS[len(self._curves) % len(_CURVE_COLOURS)]
                self._curves[name] = self._plot.plot(name=name, pen=pg.mkPen(colour, width=2))
            self._curves[name].setData(list(self._buffers[name]))

    def clear(self) -> None:
        self._buffers.clear()
        for curve in self._curves.values():
            self._plot.removeItem(curve)
        self._curves.clear()
```

- [ ] **Step 2: Write smoke test** `tests/test_serial_plotter.py`:

```python
import os; os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest

@pytest.fixture(scope="module")
def app():
    from PyQt6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])

def test_plotter_feed_creates_series(app):
    from ui.serial_plotter import SerialPlotter
    p = SerialPlotter()
    p.feed("1,2,3")
    p.feed("4,5,6")
    assert set(p._curves) == {"ch0", "ch1", "ch2"}
    p.feed("not numbers")  # ignored
    assert set(p._curves) == {"ch0", "ch1", "ch2"}
    p.clear()
    assert p._curves == {}
```

- [ ] **Step 3: Run, expect pass.** `.venv/bin/python -m pytest tests/test_serial_plotter.py -v`

- [ ] **Step 4: Lint + commit.**
```bash
git add ui/serial_plotter.py tests/test_serial_plotter.py
git commit -m "feat: add live serial plotter widget (pyqtgraph)"
```

---

## Task 6: Serial monitor panel (`ui/serial_panel.py`)

**Files:**
- Create: `ui/serial_panel.py`
- Test: `tests/test_serial_panel.py`

- [ ] **Step 1: Implement** `SerialPanel(QWidget)` following `ui/log_panel.py` styling and `ui/theme.py` factories. Structure:
  - Header `QHBoxLayout`: Connect/Disconnect `QPushButton` (`theme.make_btn`), baud `QComboBox` (`theme.make_combo` populated from `cli.serial_io.BAUD_RATES`, default 9600), line-ending combo (`LINE_ENDINGS` keys), a "Plotter" toggle `QPushButton` (checkable), autoscroll checkable button, Clear button.
  - Body: `QStackedWidget` with index 0 = read-only `QPlainTextEdit` (styled like LogPanel's editor, `setMaximumBlockCount(5000)`), index 1 = `SerialPlotter`.
  - Footer `QHBoxLayout`: `QLineEdit` (send box, `returnPressed`) + Send button.
  - Signals: `connect_requested = pyqtSignal(int)` (baud), `disconnect_requested = pyqtSignal()`, `send_requested = pyqtSignal(str, str)` (text, ending_label).
  - Public slots/methods: `append_output(line: str)` → append to text view AND `self._plotter.feed(line)`; respect autoscroll. `set_connected(bool)` → toggle button label ("Connect"/"Disconnect"), enable/disable send box, baud combo. `current_baud() -> int`, `current_ending() -> str`. `clear()` clears both views.
  - The Connect button click decides emit based on connected state; Plotter toggle switches the stacked widget.

  Keep all colours/fonts from `theme`. Do not open a serial port here — emit signals only.

- [ ] **Step 2: Write smoke test** `tests/test_serial_panel.py`:

```python
import os; os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest

@pytest.fixture(scope="module")
def app():
    from PyQt6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])

def test_serial_panel_connect_toggle(app):
    from ui.serial_panel import SerialPanel
    panel = SerialPanel()
    seen = []
    panel.connect_requested.connect(lambda baud: seen.append(("connect", baud)))
    panel.disconnect_requested.connect(lambda: seen.append(("disconnect",)))
    panel._connect_btn.click()
    assert seen[0][0] == "connect"
    panel.set_connected(True)
    panel._connect_btn.click()
    assert seen[-1] == ("disconnect",)

def test_serial_panel_append_and_clear(app):
    from ui.serial_panel import SerialPanel
    panel = SerialPanel()
    panel.append_output("hello 1 2 3")
    assert "hello" in panel._output.toPlainText()
    panel.clear()
    assert panel._output.toPlainText() == ""

def test_serial_panel_send(app):
    from ui.serial_panel import SerialPanel
    panel = SerialPanel()
    sent = []
    panel.send_requested.connect(lambda text, ending: sent.append((text, ending)))
    panel.set_connected(True)
    panel._send_box.setText("ping")
    panel._send_btn.click()
    assert sent and sent[0][0] == "ping"
```

(Adjust private attribute names in the test to match your implementation: `_connect_btn`, `_output`, `_send_box`, `_send_btn`.)

- [ ] **Step 3: Run, expect pass.** `.venv/bin/python -m pytest tests/test_serial_panel.py -v`

- [ ] **Step 4: Lint + commit.**
```bash
git add ui/serial_panel.py tests/test_serial_panel.py
git commit -m "feat: add serial monitor panel (text + plotter views)"
```

---

## Task 7: Board manager dialog (`ui/board_manager.py`)

**Files:**
- Create: `ui/board_manager.py`
- Test: `tests/test_board_manager.py`

- [ ] **Step 1: Implement** `BoardManagerDialog(QDialog)`:
  - Constructor takes an optional `cli` (defaults to `ArduinoCLI()`) for testability.
  - Search `QLineEdit` + Search button (calls `cli.core_search`); on empty query, show `cli.core_list`.
  - `QTableWidget` columns: Core ID, Name, Installed, Latest. Populate from `list[CoreInfo]`.
  - Buttons: Install / Update / Uninstall act on the selected row via a `CoreJobWorker`; disable buttons while a job runs; append worker `line` output to an embedded read-only `QPlainTextEdit`; on `finished`, refresh the list.
  - Style with `theme` tokens; size ~720x520.
  - Guard every CLI call with try/except `ArduinoCLIError`, showing the message in the embedded log (do not crash if arduino-cli is missing).

- [ ] **Step 2: Write smoke test** `tests/test_board_manager.py` with a stub CLI:

```python
import os; os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from cli.arduino_cli import CoreInfo

@pytest.fixture(scope="module")
def app():
    from PyQt6.QtWidgets import QApplication
    return QApplication.instance() or QApplication([])

class StubCLI:
    def core_list(self):
        return [CoreInfo(id="arduino:avr", name="Arduino AVR Boards", installed="1.8.6", latest="1.8.6")]
    def core_search(self, q):
        return [CoreInfo(id="esp32:esp32", name="ESP32", installed="", latest="2.0.0")]

def test_board_manager_lists_installed(app):
    from ui.board_manager import BoardManagerDialog
    dlg = BoardManagerDialog(cli=StubCLI())
    assert dlg._table.rowCount() == 1
    assert dlg._table.item(0, 0).text() == "arduino:avr"

def test_board_manager_search(app):
    from ui.board_manager import BoardManagerDialog
    dlg = BoardManagerDialog(cli=StubCLI())
    dlg._search_box.setText("esp32")
    dlg._search_btn.click()
    assert dlg._table.item(0, 0).text() == "esp32:esp32"
```

(Match private names `_table`, `_search_box`, `_search_btn` to your implementation.)

- [ ] **Step 3: Run, expect pass.** `.venv/bin/python -m pytest tests/test_board_manager.py -v`

- [ ] **Step 4: Lint + commit.**
```bash
git add ui/board_manager.py tests/test_board_manager.py
git commit -m "feat: add Boards Manager dialog (install/update/uninstall cores)"
```

---

## Task 8: Status-bar memory pills (`ui/status_bar.py`)

**Files:**
- Modify: `ui/status_bar.py`
- Test: covered by `tests/test_main_window.py` smoke (Task 9) — no new test file required.

- [ ] **Step 1: Add Flash/RAM pills.** In `_build_status_bar`, after `self._sb_blocks`, add:

```python
self._sb_flash = theme.status_pill()
sb.addWidget(self._sb_flash)
self._sb_ram = theme.status_pill()
sb.addWidget(self._sb_ram)
...
self._update_memory(None)
```

- [ ] **Step 2: Add `_update_memory`:**

```python
def _update_memory(self, stats):
    def fmt(used, mx, pct):
        accent = theme.ACCENT_GRN if pct < 60 else theme.ACCENT_AMBER if pct < 85 else theme.ACCENT_ERROR
        return accent, f"{used:,}/{mx:,} ({pct}%)"
    if stats is None:
        self._sb_flash.setText(theme.pill_html("FLASH:", "—", theme.TEXT_DIM))
        self._sb_ram.setText(theme.pill_html("RAM:", "—", theme.TEXT_DIM))
        return
    fa, ft = fmt(stats.flash_used, stats.flash_max, stats.flash_pct)
    ra, rt = fmt(stats.ram_used, stats.ram_max, stats.ram_pct)
    self._sb_flash.setText(theme.pill_html("FLASH:", ft, fa))
    self._sb_ram.setText(theme.pill_html("RAM:", rt, ra))
```

- [ ] **Step 3: Lint + commit.**
```bash
git add ui/status_bar.py
git commit -m "feat: show flash/RAM usage pills in the status bar"
```

---

## Task 9: Wire everything into MainWindow (`ui/main_window.py`)

**Files:**
- Modify: `ui/main_window.py`
- Test: `tests/test_main_window.py` (extend smoke test)

- [ ] **Step 1: Build the serial dock.** Add `_build_serial_dock()` called from `__init__` after `_build_log_dock()`:

```python
def _build_serial_dock(self):
    self._serial_panel = SerialPanel()
    self._serial_worker = None
    self._reconnect_after_job = None  # remembers (baud) to reconnect after upload
    dock = QDockWidget("Serial", self)
    dock.setWidget(self._serial_panel)
    dock.setFeatures(... same flags as log dock ...)
    dock.setMinimumHeight(160)
    dock.setStyleSheet(... same as log dock ...)
    self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
    self.tabifyDockWidget(self._log_dock, dock)  # store self._log_dock in _build_log_dock
    self._serial_panel.connect_requested.connect(self._on_serial_connect)
    self._serial_panel.disconnect_requested.connect(self._on_serial_disconnect)
    self._serial_panel.send_requested.connect(self._on_serial_send)
```

(Refactor `_build_log_dock` to keep `self._log_dock = dock`.)

- [ ] **Step 2: Serial slots:**

```python
def _on_serial_connect(self, baud: int):
    port = self._selected_port()
    if not port:
        self._show_warning("Select a serial port before connecting.")
        self._serial_panel.set_connected(False)
        return
    self._serial_worker = SerialReadWorker(port, baud, self)
    self._serial_worker.line_received.connect(self._serial_panel.append_output)
    self._serial_worker.connection_error.connect(self._on_serial_error)
    self._serial_worker.start()
    self._serial_panel.set_connected(True)
    self._log_panel.append_line(f"Serial connected: {port} @ {baud}", "success")

def _on_serial_disconnect(self):
    if self._serial_worker:
        self._serial_worker.stop()
        self._serial_worker = None
    self._serial_panel.set_connected(False)
    self._log_panel.append_line("Serial disconnected.", "info")

def _on_serial_send(self, text: str, ending: str):
    if self._serial_worker:
        self._serial_worker.send(text, ending)

def _on_serial_error(self, message: str):
    self._log_panel.append_line(f"Serial error: {message}", "error")
    self._serial_worker = None
    self._serial_panel.set_connected(False)
```

- [ ] **Step 3: Port handoff around uploads.** In `_start_job`, before starting an upload, if a serial worker is connected, record the baud and disconnect:

```python
self._reconnect_after_job = None
if self._serial_worker and action == "upload":
    self._reconnect_after_job = self._serial_panel.current_baud()
    self._on_serial_disconnect()
    self._log_panel.append_line("Released serial port for upload.", "dim")
```

In `_on_job_finished`, after status update, reconnect if needed:

```python
if self._reconnect_after_job is not None:
    baud = self._reconnect_after_job
    self._reconnect_after_job = None
    self._serial_panel._baud_combo.setCurrentText(str(baud))  # or a setter
    self._on_serial_connect(baud)
```

- [ ] **Step 4: Memory pills.** In `_start_job`, connect the worker stats signal: `self._job_worker.stats.connect(self._update_memory)`.

- [ ] **Step 5: Tools menu + Boards Manager.** In `_build_menu_bar`, add:

```python
tools_menu = mb.addMenu("&Tools")
bm_act = QAction("&Boards Manager…", self)
bm_act.triggered.connect(self._on_boards_manager)
tools_menu.addAction(bm_act)
```

And the slot:

```python
def _on_boards_manager(self):
    from ui.board_manager import BoardManagerDialog
    dlg = BoardManagerDialog(parent=self)
    dlg.exec()
    self._on_refresh_ports()  # cores may have changed available boards
```

- [ ] **Step 6: Imports.** Add `from ui.serial_panel import SerialPanel` and `from ui.workers import ... SerialReadWorker`.

- [ ] **Step 7: Extend smoke test** `tests/test_main_window.py` — assert the window builds with the serial dock and Tools menu present, and `_update_memory(None)` runs without error. Follow the existing offscreen QApplication fixture in that file.

- [ ] **Step 8: Run full suite + lint.**
```bash
.venv/bin/python -m pytest tests/ -v
make lint
```

- [ ] **Step 9: Commit.**
```bash
git add ui/main_window.py tests/test_main_window.py
git commit -m "feat: wire serial monitor, plotter, memory pills, boards manager into the window"
```

---

## Task 10: Version bump, docs, changelog

**Files:**
- Modify: `app_config.py` (via make), `CHANGELOG.md`, `CLAUDE.md`

- [ ] **Step 1: Bump version.** `make bump-version VERSION=1.1.0`.

- [ ] **Step 2: CHANGELOG.** Under `## [Unreleased]` → `### Added`, add the Phase 2 entry summarising serial monitor, plotter, flash/RAM pills, and Boards Manager.

- [ ] **Step 3: CLAUDE.md.** Document `cli/serial_io.py`, the new workers (`SerialReadWorker`, `CoreJobWorker`, `ArduinoJobWorker.stats`), `ui/serial_panel.py`, `ui/serial_plotter.py`, `ui/board_manager.py`, and the serial-port-handoff rule (monitor releases the port during upload, reconnects after).

- [ ] **Step 4: Final verification.**
```bash
make lint && make test && make test-js
```
Expected: all green.

- [ ] **Step 5: Commit.**
```bash
git add app_config.py CHANGELOG.md CLAUDE.md
git commit -m "docs: document Phase 2 features and bump version to 1.1.0"
```

---

## Self-Review notes

- **Spec coverage:** serial console (T1,4,6,9), plotter (T1,5,6), memory gauges (T2,8,9), core management (T3,7,9), deps (T1), tests (each task), docs/version (T10). All four spec features mapped.
- **Type consistency:** `CompileStats`/`CoreInfo` defined in T2/T3 and consumed in T8/T7/T9; `SerialReadWorker.send(text, ending_label)` matches `SerialPanel.send_requested(text, ending)` and `_on_serial_send`. `parse_plot_values` shared by T1/T5.
- **Open implementation detail for the worker (T9 Step 3):** prefer adding a `SerialPanel.set_baud(int)` setter rather than poking `_baud_combo` directly; the subagent should add it when implementing T6.
