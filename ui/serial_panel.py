"""
ui/serial_panel.py — Serial monitor panel (text output + live plotter view).

This panel holds NO serial port itself — it only emits signals
(`connect_requested`, `disconnect_requested`, `send_requested`). A later
wiring step (MainWindow + serial worker) listens to these signals and calls
back into `set_connected()` / `append_output()`.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from cli.serial_io import BAUD_RATES, LINE_ENDINGS
from ui import theme
from ui.serial_plotter import SerialPlotter
from ui.theme import BG_DARK as BG_HEADER
from ui.theme import BG_DEEP as BG_PANEL
from ui.theme import BORDER, FONT_MONO, TEXT_MAIN


class SerialPanel(QWidget):
    """Serial monitor: connect/disconnect, baud/EOL selection, output view, send box."""

    connect_requested = pyqtSignal(int)
    disconnect_requested = pyqtSignal()
    send_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._connected = False
        self._build_ui()
        self._wire_signals()
        self.set_connected(False)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(38)
        header.setStyleSheet(f"background: {BG_HEADER}; border-bottom: 1px solid {BORDER};")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 0, 10, 0)

        self._connect_btn = theme.make_btn(
            "Connect", theme.ACCENT_GRN, theme.ACCENT_GRN_HI, tooltip="Open/close the serial port"
        )
        self._connect_btn.setFixedWidth(96)
        hl.addWidget(self._connect_btn)

        hl.addWidget(theme.tb_label("Baud"))
        self._baud_combo = theme.make_combo([str(b) for b in BAUD_RATES], 90)
        self._baud_combo.setCurrentText("9600")
        hl.addWidget(self._baud_combo)

        hl.addWidget(theme.tb_label("EOL"))
        self._ending_combo = theme.make_combo(list(LINE_ENDINGS), 130)
        self._ending_combo.setCurrentText("Newline")
        hl.addWidget(self._ending_combo)

        hl.addStretch()

        self._plotter_btn = theme.make_btn(
            "Plotter", secondary=True, tooltip="Switch to plotter view"
        )
        self._plotter_btn.setCheckable(True)
        self._plotter_btn.setFixedWidth(90)
        hl.addWidget(self._plotter_btn)

        self._autoscroll_btn = theme.make_btn(
            "Autoscroll", secondary=True, tooltip="Automatically scroll to the latest output"
        )
        self._autoscroll_btn.setCheckable(True)
        self._autoscroll_btn.setChecked(True)
        self._autoscroll_btn.setFixedWidth(96)
        hl.addWidget(self._autoscroll_btn)

        self._clear_btn = theme.make_btn("Clear", secondary=True, tooltip="Clear the output")
        self._clear_btn.setFixedWidth(70)
        hl.addWidget(self._clear_btn)

        root.addWidget(header)

        # ── Stack: text output / plotter ────────────────────────────────────
        self._stack = QStackedWidget()

        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)

        font = QFont("Fira Code", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        if not font.exactMatch():
            font = QFont("JetBrains Mono", 10)
            font.setStyleHint(QFont.StyleHint.Monospace)
        self._output.setFont(font)

        self._output.setStyleSheet(
            f"QPlainTextEdit {{"
            f"  background: {BG_PANEL};"
            f"  color: {TEXT_MAIN};"
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
        self._output.setMaximumBlockCount(5000)
        self._stack.addWidget(self._output)

        self._plotter = SerialPlotter()
        self._stack.addWidget(self._plotter)

        root.addWidget(self._stack)

        # ── Footer: send box ─────────────────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(44)
        footer.setStyleSheet(f"background: {BG_HEADER}; border-top: 1px solid {BORDER};")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(10, 0, 10, 0)

        self._send_box = QLineEdit()
        self._send_box.setPlaceholderText("Type a line to send…")
        self._send_box.setFixedHeight(34)
        self._send_box.setStyleSheet(
            f"QLineEdit {{ background: {theme.BG_RAISED}; color: {TEXT_MAIN};"
            f" font-family: {FONT_MONO}; border: 1px solid {BORDER};"
            f" border-radius: 6px; padding: 0 10px; font-size: 12px; }}"
            f"QLineEdit:focus {{ border-color: {theme.BORDER_HI}; }}"
            f"QLineEdit:disabled {{ color: {theme.TEXT_DIM}; }}"
        )
        fl.addWidget(self._send_box)

        self._send_btn = theme.make_btn("Send", theme.ACCENT_GRN, theme.ACCENT_GRN_HI)
        self._send_btn.setFixedWidth(90)
        fl.addWidget(self._send_btn)

        root.addWidget(footer)

    # ── Signal wiring ────────────────────────────────────────────────────────

    def _wire_signals(self):
        self._connect_btn.clicked.connect(self._on_connect_clicked)
        self._plotter_btn.toggled.connect(self._on_plotter_toggled)
        self._clear_btn.clicked.connect(self.clear)
        self._send_btn.clicked.connect(self._on_send)
        self._send_box.returnPressed.connect(self._on_send)

    def _on_connect_clicked(self):
        if self._connected:
            self.disconnect_requested.emit()
        else:
            self.connect_requested.emit(self.current_baud())

    def _on_plotter_toggled(self, checked: bool):
        self._stack.setCurrentIndex(1 if checked else 0)
        self._plotter_btn.setText("Monitor" if checked else "Plotter")

    def _on_send(self):
        text = self._send_box.text()
        if not text:
            return
        self.send_requested.emit(text, self.current_ending())
        self._send_box.clear()

    # ── Public API ────────────────────────────────────────────────────────────

    def current_baud(self) -> int:
        return int(self._baud_combo.currentText())

    def current_ending(self) -> str:
        return self._ending_combo.currentText()

    def set_baud(self, baud: int) -> None:
        text = str(baud)
        idx = self._baud_combo.findText(text)
        if idx >= 0:
            self._baud_combo.setCurrentIndex(idx)

    def set_connected(self, connected: bool) -> None:
        self._connected = connected
        self._connect_btn.setText("Disconnect" if connected else "Connect")
        self._send_box.setEnabled(connected)
        self._send_btn.setEnabled(connected)
        self._baud_combo.setEnabled(not connected)

    def append_output(self, line: str) -> None:
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if self._output.toPlainText():
            cursor.insertText("\n")
        cursor.insertText(line)
        self._output.setTextCursor(cursor)

        self._plotter.feed(line)

        if self._autoscroll_btn.isChecked():
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self._output.setTextCursor(cursor)
            self._output.verticalScrollBar().setValue(self._output.verticalScrollBar().maximum())

    def clear(self) -> None:
        self._output.clear()
        self._plotter.clear()
