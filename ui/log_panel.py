"""
ui/log_panel.py — Build log / output panel (docked at the bottom of the window).

What to do here:
  1. Subclass QWidget.
  2. Use a QPlainTextEdit (read-only, monospace font, dark background preferred).
  3. Expose these public methods:
       def append_line(self, text: str, level: str = "info") -> None:
           # Appends a line to the log.
           # level can be "info", "warning", "error".
           # Colour the line accordingly:
           #   info    → default text colour (white / light grey)
           #   warning → yellow / amber
           #   error   → red
       def clear(self) -> None:
           # Clears all log output.
  4. Auto-scroll to the bottom after every append_line call.
  5. Optional: add a small "Clear" button in the top-right corner of the panel.

Usage:
  ArduinoCLI.compile() and .upload() stream stdout / stderr here line by line.
  Parsed error messages from arduino_cli.py are also shown here with level="error".
"""

# TODO: from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton
# TODO: from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
# TODO: from PyQt6.QtCore import Qt


class LogPanel:
    # TODO: subclass QWidget
    # TODO: set up layout with QPlainTextEdit
    # TODO: implement append_line(self, text: str, level: str = "info")
    # TODO: implement clear(self)
    pass
