"""
ui/log_panel.py — Build log / output panel (docked at the bottom of the window).
"""

from datetime import datetime

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QLabel
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PyQt6.QtCore import Qt


WELCOME_TEXT = "SparkIDE v0.1 — Ready.  Connect an Arduino board and click Compile."

# Colour palette — One Dark tones
_COLOURS = {
    "info":    "#abb2bf",  # soft white
    "warning": "#e5c07b",  # amber
    "error":   "#e06c75",  # soft red
    "success": "#98c379",  # soft green
    "dim":     "#4b5263",  # muted / timestamps
}

BG_PANEL  = "#111111"
BG_HEADER = "#141414"
BORDER    = "#2e2e2e"


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
        header.setFixedHeight(30)
        header.setStyleSheet(
            f"background: {BG_HEADER}; border-bottom: 1px solid {BORDER};"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 0, 8, 0)

        title = QLabel("⬛  Output")
        title.setStyleSheet(
            "color: #888; font-size: 11px; font-weight: 600; letter-spacing: 0.4px;"
        )
        hl.addWidget(title)
        hl.addStretch()

        # Timestamps toggle label (cosmetic for now)
        ts_label = QLabel("timestamps on")
        ts_label.setStyleSheet("color: #3a3a3a; font-size: 10px; margin-right: 10px;")
        hl.addWidget(ts_label)

        clear_btn = QPushButton("✕ Clear")
        clear_btn.setFixedSize(60, 20)
        clear_btn.setStyleSheet(
            "QPushButton { background: #1e1e1e; color: #666; border: 1px solid #2a2a2a;"
            " border-radius: 4px; font-size: 10px; }"
            "QPushButton:hover { background: #2a2a2a; color: #e06c75; border-color: #e06c75; }"
            "QPushButton:pressed { background: #1a1a1a; }"
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
            f"  color: #abb2bf;"
            f"  border: none;"
            f"  padding: 6px 12px;"
            f"}}"
            f"QScrollBar:vertical {{"
            f"  background: {BG_PANEL}; width: 6px; border: none;"
            f"}}"
            f"QScrollBar::handle:vertical {{"
            f"  background: #2a2a2a; border-radius: 3px;"
            f"}}"
            f"QScrollBar::handle:vertical:hover {{ background: #444; }}"
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
