"""
ui/workers.py — background QThread workers for board discovery and build jobs.

Kept off the UI thread so the window stays responsive while arduino-cli runs.
"""

from PyQt6.QtCore import QThread, pyqtSignal

from app_config import BUILD_DIR, SKETCH_FILE
from cli.arduino_cli import ArduinoCLI, ArduinoCLIError


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

    def __init__(self, action: str, fqbn: str, port: str, code: str, parent=None):
        super().__init__(parent)
        self._action = action
        self._fqbn = fqbn
        self._port = port
        self._code = code

    def run(self):
        try:
            BUILD_DIR.mkdir(parents=True, exist_ok=True)
            SKETCH_FILE.write_text(self._code, encoding="utf-8")
            self.line.emit(f"Sketch written to {SKETCH_FILE}", "dim")

            cli = ArduinoCLI()
            if self._action == "compile":
                ok = cli.compile(self._fqbn, BUILD_DIR, self.line.emit)
                self.finished.emit(ok, "Compile complete." if ok else "Compile failed.")
            else:
                ok = cli.compile(self._fqbn, BUILD_DIR, self.line.emit)
                if ok:
                    ok = cli.upload(self._fqbn, self._port, BUILD_DIR, self.line.emit)
                self.finished.emit(ok, "Upload complete." if ok else "Upload failed.")
        except OSError as exc:
            self.line.emit(f"Could not write sketch: {exc}", "error")
            self.finished.emit(False, "Sketch write failed.")
