"""
ui/log_panel.py — Build log / output panel (docked at the bottom of the window).
"""

from datetime import datetime

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QLabel
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PyQt6.QtCore import Qt


WELCOME_TEXT = "SparkIDE v0.1 — Ready.  Connect an Arduino board and click Compile."

# Colour palette — Hybrid Lab Console (terminal/maker-lab)
_COLOURS = {
    "info":    "#7fa89c",  # muted teal-gray
    "warning": "#f0a93e",  # amber
    "error":   "#f0654a",  # warm red
    "success": "#4ade80",  # phosphor green
    "dim":     "#3f4f48",  # muted / timestamps
}

BG_PANEL  = "#0a0f0c"
BG_HEADER = "#0d1310"
BORDER    = "#22322a"
FONT_MONO = '"JetBrains Mono", "Fira Code", "DejaVu Sans Mono", monospace'


class LogPanel(QWidget):
    """Read-only, colour-coded build log widget."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.append_line(WELCOME_TEXT, level="success")

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(38)
        header.setStyleSheet(
            f"background: {BG_HEADER}; border-bottom: 1px solid {BORDER};"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(14, 0, 10, 0)

        title = QLabel("Build Output")
        title.setStyleSheet(
            f"color: #93a89c; font-family: {FONT_MONO}; font-size: 11px; font-weight: 700; letter-spacing: 0.4px;"
        )
        hl.addWidget(title)
        hl.addStretch()

        ts_label = QLabel("timestamps on")
        ts_label.setStyleSheet(
            f"color: #5c7468; font-family: {FONT_MONO}; font-size: 10px; margin-right: 10px;"
        )
        hl.addWidget(ts_label)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedSize(62, 24)
        clear_btn.setStyleSheet(
            f"QPushButton {{ background: #16201b; color: #93a89c; font-family: {FONT_MONO};"
            " border: 1px solid #22322a;"
            " border-radius: 6px; font-size: 10px; font-weight: 600; }"
            "QPushButton:hover { background: #1c2620; color: #e4f0e8; border-color: #3c5347; }"
            "QPushButton:pressed { background: #0d1310; }"
        )
        clear_btn.clicked.connect(self.clear)
        hl.addWidget(clear_btn)

        root.addWidget(header)

        # ── Text area ────────────────────────────────────────────────────────
        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)

        # Font: try nice monospace, fall back gracefully
        font = QFont("Fira Code", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        if not font.exactMatch():
            font = QFont("JetBrains Mono", 10)
            font.setStyleHint(QFont.StyleHint.Monospace)
        self._editor.setFont(font)

        self._editor.setStyleSheet(
            f"QPlainTextEdit {{"
            f"  background: {BG_PANEL};"
            f"  color: #e4f0e8;"
            f"  border: none;"
            f"  padding: 10px 14px;"
            f"}}"
            f"QScrollBar:vertical {{"
            f"  background: {BG_PANEL}; width: 8px; border: none;"
            f"}}"
            f"QScrollBar::handle:vertical {{"
            f"  background: #2a3a32; border-radius: 4px;"
            f"}}"
            f"QScrollBar::handle:vertical:hover {{ background: #3c5347; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
        )
        self._editor.setMaximumBlockCount(1000)
        root.addWidget(self._editor)

    # ── Public API ────────────────────────────────────────────────────────────

    def append_line(self, text: str, level: str = "info") -> None:
        """Append a timestamped, colour-coded line to the log."""
        colour = _COLOURS.get(level, _COLOURS["info"])
        ts = datetime.now().strftime("%H:%M:%S")

        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Newline separator (skip on first line)
        if self._editor.toPlainText():
            cursor.insertText("\n")

        # Timestamp in dim colour
        ts_fmt = QTextCharFormat()
        ts_fmt.setForeground(QColor(_COLOURS["dim"]))
        cursor.setCharFormat(ts_fmt)
        cursor.insertText(f"[{ts}]  ")

        # Message in level colour
        msg_fmt = QTextCharFormat()
        msg_fmt.setForeground(QColor(colour))
        cursor.setCharFormat(msg_fmt)
        cursor.insertText(text)

        self._editor.setTextCursor(cursor)
        self._editor.verticalScrollBar().setValue(
            self._editor.verticalScrollBar().maximum()
        )

    def clear(self) -> None:
        """Clear all log output."""
        self._editor.clear()
