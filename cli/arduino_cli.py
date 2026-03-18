"""
cli/arduino_cli.py — Subprocess wrapper around the `arduino-cli` command-line tool.

What to do here:
  1. Define an ArduinoCLI class with the following methods:

  ── list_boards(self) -> list[dict]
       Runs:  arduino-cli board list --format json
       Parses the JSON output and returns a list of dicts, each with keys:
         { "fqbn": "arduino:avr:uno", "port": "/dev/ttyUSB0", "name": "Arduino Uno" }
       If no boards found, return [].

  ── compile(self, fqbn: str, sketch_path: str, callback) -> bool
       Runs:  arduino-cli compile --fqbn <fqbn> <sketch_path>
       Streams stdout and stderr line-by-line to callback(line, level).
         level = "info" for stdout, "error" for stderr.
       Returns True if process exits with code 0, False otherwise.
       On failure: parse error text → call callback(readable_message, "error").

  ── upload(self, fqbn: str, port: str, sketch_path: str, callback) -> bool
       Runs:  arduino-cli upload --fqbn <fqbn> --port <port> <sketch_path>
       Same streaming + return semantics as compile().

  2. All long-running operations (compile, upload) MUST run in a QThread worker,
     NOT on the main thread — otherwise the UI will freeze.
     Pattern: create a Worker(QRunnable or QThread) that calls compile()/upload()
     and emits signals for each output line. MainWindow connects those signals
     to LogPanel.append_line().

  3. Error parsing helper:
     def _parse_error(self, raw: str) -> str:
         # Takes raw arduino-cli stderr and returns a human-readable string.
         # Common patterns to handle:
         #   - "error: 'xxx' was not declared in this scope"
         #   - "error: expected ';' before '}' token"
         # Strip file paths, line numbers, and compiler jargon where possible.

Notes:
  - arduino-cli must be installed and in PATH. Check with: which arduino-cli
  - Boards must be installed: arduino-cli core install arduino:avr
    (Can add a helper check method here and show a dialog if missing.)
"""

import subprocess
import json

# TODO: from PyQt6.QtCore import QObject, QThread, pyqtSignal


class ArduinoCLI:
    # TODO: implement list_boards(self) -> list[dict]
    # TODO: implement compile(self, fqbn, sketch_path, callback) -> bool
    # TODO: implement upload(self, fqbn, port, sketch_path, callback) -> bool
    # TODO: implement _parse_error(self, raw: str) -> str
    pass
