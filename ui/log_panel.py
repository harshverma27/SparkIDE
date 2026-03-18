"""
ui/log_panel.py — Build log / output panel (docked at the bottom of the window).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QLabel
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PyQt6.QtCore import Qt


WELCOME_TEXT = "SparkIDE v0.1 — Ready.\nConnect an Arduino board and click Compile."

# Colour palette
_COLOURS = {
    "info":    "#d4d4d4",  # light grey
    "warning": "#e5c07b",  # amber
    "error":   "#e06c75",  # soft red
    "success": "#98c379",  # soft green
}


class LogPanel(QWidget):
    """Read-only, colour-coded build log widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.append_line(WELCOME_TEXT, level="info")

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header bar
        header = QWidget()
        header.setFixedHeight(28)
        header.setStyleSheet("background:#1a1a1a; border-bottom: 1px solid #3a3a3a;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(8, 0, 8, 0)

        title = QLabel("Output")
        title.setStyleSheet("color:#888; font-size:11px; font-weight:600; letter-spacing:1px;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedSize(52, 20)
        clear_btn.setStyleSheet(
            "QPushButton { background:#2a2a2a; color:#888; border:1px solid #3a3a3a;"
            " border-radius:3px; font-size:10px; }"
            "QPushButton:hover { background:#333; color:#ccc; }"
        )
        clear_btn.clicked.connect(self.clear)
        h_layout.addWidget(clear_btn)

        root.addWidget(header)

        # Text area
        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setFont(QFont("Monospace", 10))
        self._editor.setStyleSheet(
            "QPlainTextEdit {"
            "  background: #111;"
            "  color: #d4d4d4;"
            "  border: none;"
            "  padding: 6px 10px;"
            "}"
        )
        # Limit scrollback to 500 lines for performance
        self._editor.setMaximumBlockCount(500)
        root.addWidget(self._editor)

    # ── Public API ────────────────────────────────────────────────────────────

    def append_line(self, text: str, level: str = "info") -> None:
        """Append a line to the log in the appropriate colour."""
        colour = _COLOURS.get(level, _COLOURS["info"])

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(colour))

        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Insert a newline before new content if the log isn't empty
        if not self._editor.toPlainText() == "":
            cursor.insertText("\n")

        cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self._editor.setTextCursor(cursor)

        # Auto-scroll to bottom
        self._editor.verticalScrollBar().setValue(
            self._editor.verticalScrollBar().maximum()
        )

    def clear(self) -> None:
        """Clear all log output."""
        self._editor.clear()
