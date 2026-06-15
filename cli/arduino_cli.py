"""
cli/arduino_cli.py — Subprocess wrapper around the `arduino-cli` tool.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from threading import Thread

LogCallback = Callable[[str, str], None]


@dataclass(frozen=True)
class BoardOption:
    name: str
    fqbn: str
    port: str = ""
    detected: bool = False

    @property
    def label(self) -> str:
        suffix = " detected" if self.detected else " compile only"
        return f"{self.name} ({self.fqbn}) - {suffix}"


class ArduinoCLIError(RuntimeError):
    """Raised when arduino-cli is unavailable or returns malformed data."""


class ArduinoCLI:
    """Small synchronous wrapper. Run compile/upload from a worker thread."""

    def __init__(self, executable: str = "arduino-cli"):
        self.executable = executable

    def is_available(self) -> bool:
        return shutil.which(self.executable) is not None

    def list_boards(self) -> list[BoardOption]:
        """Return currently detected boards, including their serial ports."""
        data = self._run_json(["board", "list", "--format", "json"])
        ports = data.get("detected_ports", [])
        boards: list[BoardOption] = []

        for detected in ports:
            port = self._port_address(detected.get("port", {}))
            matching = detected.get("matching_boards") or []
            for match in matching:
                fqbn = match.get("fqbn", "")
                name = match.get("name", fqbn or "Unknown board")
                if fqbn:
                    boards.append(BoardOption(name=name, fqbn=fqbn, port=port, detected=True))

        return self._unique_boards(boards)

    def list_ports(self) -> list[str]:
        data = self._run_json(["board", "list", "--format", "json"])
        ports = []
        for detected in data.get("detected_ports", []):
            port = self._port_address(detected.get("port", {}))
            if port:
                ports.append(port)
        return sorted(set(ports))

    def list_installed_boards(self) -> list[BoardOption]:
        """Return boards supported by installed cores, useful before USB discovery."""
        data = self._run_json(["board", "listall", "--format", "json"])
        boards = [
            BoardOption(name=item.get("name", item.get("fqbn", "Unknown board")), fqbn=item["fqbn"])
            for item in data.get("boards", [])
            if item.get("fqbn")
        ]
        return self._prioritize_common_boards(self._unique_boards(boards))

    def compile(self, fqbn: str, sketch_path: str | Path, callback: LogCallback) -> bool:
        return self._run_streaming(
            ["compile", "--fqbn", fqbn, str(sketch_path)],
            callback,
        )

    def upload(self, fqbn: str, port: str, sketch_path: str | Path, callback: LogCallback) -> bool:
        return self._run_streaming(
            ["upload", "--fqbn", fqbn, "--port", port, str(sketch_path)],
            callback,
        )

    def _run_json(self, args: list[str]) -> dict:
        if not self.is_available():
            raise ArduinoCLIError("arduino-cli was not found in PATH.")

        completed = subprocess.run(
            [self.executable, *args],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise ArduinoCLIError(self._parse_error(completed.stderr or completed.stdout))
        try:
            return json.loads(completed.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise ArduinoCLIError("arduino-cli returned invalid JSON.") from exc

    def _run_streaming(self, args: list[str], callback: LogCallback) -> bool:
        if not self.is_available():
            callback("arduino-cli was not found in PATH.", "error")
            return False

        command = [self.executable, *args]
        callback("$ " + " ".join(command), "dim")

        process = subprocess.Popen(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
        )
        assert process.stdout is not None
        assert process.stderr is not None

        queue: Queue[tuple[str, str | None]] = Queue()

        def reader(stream, level: str) -> None:
            for line in iter(stream.readline, ""):
                queue.put((level, line.rstrip()))
            queue.put((level, None))

        Thread(target=reader, args=(process.stdout, "info"), daemon=True).start()
        Thread(target=reader, args=(process.stderr, "error"), daemon=True).start()

        closed = 0
        raw_errors: list[str] = []
        while closed < 2:
            level, line = queue.get()
            if line is None:
                closed += 1
                continue
            if line:
                if level == "error":
                    raw_errors.append(line)
                callback(line, level)

        return_code = process.wait()
        if return_code == 0:
            callback("Done.", "success")
            return True

        parsed = self._parse_error("\n".join(raw_errors))
        if parsed:
            callback(parsed, "error")
        return False

    def _parse_error(self, raw: str) -> str:
        text = raw.strip()
        if not text:
            return "arduino-cli failed without an error message."

        patterns = [
            (
                r"error:\s*'([^']+)'\s+was not declared in this scope",
                "Unknown name '{0}'. Check the block variable or function name.",
            ),
            (
                r"error:\s*expected\s+';'\s+before\s+'([^']+)'\s+token",
                "The generated code is missing a semicolon before '{0}'.",
            ),
            (r"Error during build:\s*(.+)", "Build failed: {0}"),
            (r"Compilation error:\s*(.+)", "Compilation failed: {0}"),
            (r"No such file or directory", "A required file or board package is missing."),
            (
                r"Permission denied",
                "Permission denied. Check serial port permissions or board access.",
            ),
        ]
        for regex, message in patterns:
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                return message.format(*match.groups())

        lines = [self._strip_path_noise(line) for line in text.splitlines() if line.strip()]
        return lines[-1] if lines else text

    @staticmethod
    def _port_address(port: dict) -> str:
        return port.get("address") or port.get("label") or port.get("protocol") or ""

    @staticmethod
    def _strip_path_noise(line: str) -> str:
        return re.sub(r"[/\w.\-]+\.ino:\d+:\d+:\s*", "", line).strip()

    @staticmethod
    def _unique_boards(boards: list[BoardOption]) -> list[BoardOption]:
        seen: set[tuple[str, str]] = set()
        unique: list[BoardOption] = []
        for board in boards:
            key = (board.fqbn, board.port)
            if key not in seen:
                seen.add(key)
                unique.append(board)
        return unique

    @staticmethod
    def _prioritize_common_boards(boards: list[BoardOption]) -> list[BoardOption]:
        preferred = {
            "arduino:avr:uno": 0,
            "arduino:avr:nano": 1,
            "arduino:avr:mega": 2,
            "arduino:avr:leonardo": 3,
        }
        return sorted(boards, key=lambda b: (preferred.get(b.fqbn, 99), b.name.lower()))
