"""
ui/workers.py — background QThread workers for board discovery and build jobs.

Kept off the UI thread so the window stays responsive while arduino-cli runs.
"""

from pathlib import Path

import serial
from PyQt6.QtCore import QMutex, QMutexLocker, QThread, pyqtSignal

from app_config import BUILD_DIR, SKETCH_FILE
from cli.arduino_cli import ArduinoCLI, ArduinoCLIError, parse_compile_stats
from cli.serial_io import LINE_ENDINGS


class BoardRefreshWorker(QThread):
    """Discover connected and installed boards plus their serial ports."""

    finished = pyqtSignal(list, list, str)

    def run(self):
        cli = ArduinoCLI()
        try:
            detected = cli.list_boards()
            installed = cli.list_installed_boards()
            ports = sorted({board.port for board in detected if board.port})
            self.finished.emit(detected + installed, ports, "")
        except ArduinoCLIError as exc:
            self.finished.emit([], [], str(exc))


class ArduinoJobWorker(QThread):
    """Write the current sketch and run a compile (and optionally upload)."""

    line = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)
    stats = pyqtSignal(object)

    def __init__(self, action: str, fqbn: str, port: str, code: str, parent=None, *, sketch_dir=None):
        super().__init__(parent)
        self._action = action
        self._fqbn = fqbn
        self._port = port
        self._code = code
        self._sketch_dir = Path(sketch_dir) if sketch_dir is not None else None

    def run(self):
        try:
            if self._sketch_dir is not None:
                build_dir = self._sketch_dir
                sketch_file = build_dir / f"{build_dir.name}.ino"
            else:
                build_dir = BUILD_DIR
                sketch_file = SKETCH_FILE
            build_dir.mkdir(parents=True, exist_ok=True)
            sketch_file.write_text(self._code, encoding="utf-8")
            self.line.emit(f"Sketch written to {sketch_file}", "dim")

            captured: list[str] = []

            def cb(line: str, level: str):
                captured.append(line)
                self.line.emit(line, level)

            cli = ArduinoCLI()
            if self._action == "compile":
                ok = cli.compile(self._fqbn, build_dir, cb)
                self.stats.emit(parse_compile_stats("\n".join(captured)))
                self.finished.emit(ok, "Compile complete." if ok else "Compile failed.")
            else:
                ok = cli.compile(self._fqbn, build_dir, cb)
                if ok:
                    ok = cli.upload(self._fqbn, self._port, build_dir, cb)
                self.stats.emit(parse_compile_stats("\n".join(captured)))
                self.finished.emit(ok, "Upload complete." if ok else "Upload failed.")
        except OSError as exc:
            self.line.emit(f"Could not write sketch: {exc}", "error")
            self.finished.emit(False, "Sketch write failed.")


class SerialReadWorker(QThread):
    """Reads lines from a serial port until stopped; thread-safe send()."""

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


class CoreJobWorker(QThread):
    """Runs a single core install/upgrade/uninstall, streaming output."""

    line = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, action: str, core_id: str, parent=None):
        super().__init__(parent)
        self._action = action
        self._core_id = core_id

    def run(self):
        cli = ArduinoCLI()
        fn = {
            "install": cli.core_install,
            "upgrade": cli.core_upgrade,
            "uninstall": cli.core_uninstall,
        }[self._action]
        ok = fn(self._core_id, self.line.emit)
        self.finished.emit(ok, f"{self._action} {'complete' if ok else 'failed'}: {self._core_id}")
