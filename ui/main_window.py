"""
ui/main_window.py — PyQt6 Main Application Window.
"""

import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QToolBar, QStatusBar,
    QDockWidget, QSizePolicy, QMenu, QFileDialog, QMessageBox,
    QFrame,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtGui import QAction, QKeySequence, QColor
from PyQt6.QtCore import Qt, QSize, QUrl

from ui.code_panel import CodePanel
from ui.log_panel import LogPanel
from bridge.channel import Bridge


# ── Placeholder board / port data (real data from arduino-cli in next phase) ──
PLACEHOLDER_BOARDS = ["Arduino Uno", "Arduino Nano", "Arduino Mega", "Arduino Leonardo"]
PLACEHOLDER_PORTS  = ["/dev/ttyUSB0", "/dev/ttyACM0", "/dev/ttyUSB1"]

# Absolute path to the Blockly host page
BLOCKLY_HTML = Path(__file__).parent.parent / "blockly" / "index.html"

# ── Design tokens ────────────────────────────────────────────────────────────
BG_DEEP    = "#141414"   # deepest background (title-bar-like areas)
BG_DARK    = "#1a1a1a"   # dark surfaces
BG_MID     = "#1e1e1e"   # mid surface (main background)
BG_RAISED  = "#252525"   # slightly raised elements
BORDER     = "#2e2e2e"   # subtle borders
BORDER_HI  = "#4a4a4a"   # hover borders
ACCENT_GRN = "#2d8a4e"   # compile green
ACCENT_GRN_HI = "#23703e"
ACCENT_BLU = "#1a6fb5"   # upload blue
ACCENT_BLU_HI = "#155c99"
TEXT_DIM   = "#606060"   # muted text
TEXT_MID   = "#888888"   # secondary text
TEXT_MAIN  = "#cccccc"   # primary text


class MainWindow(QMainWindow):
    """Top-level application window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SparkIDE")
        self.setMinimumSize(1100, 680)
        self.resize(1360, 800)

        # Global window background
        self.setStyleSheet(f"QMainWindow {{ background: {BG_MID}; }}")

        self._build_menu_bar()
        self._build_toolbar()
        self._build_central()
        self._build_log_dock()
        self._build_status_bar()

    # ── Menu bar ──────────────────────────────────────────────────────────────

    def _build_menu_bar(self):
        mb = self.menuBar()
        mb.setStyleSheet(
            f"QMenuBar {{ background: {BG_DEEP}; color: {TEXT_MID}; border-bottom: 1px solid {BORDER}; }}"
            f"QMenuBar::item:selected {{ background: {BG_RAISED}; color: {TEXT_MAIN}; }}"
            f"QMenu {{ background: {BG_DARK}; color: {TEXT_MAIN}; border: 1px solid {BORDER_HI}; }}"
            f"QMenu::item:selected {{ background: #264f78; }}"
        )

        file_menu: QMenu = mb.addMenu("&File")
        for label, shortcut, slot, tip in [
            ("&Save Workspace",     "Ctrl+S", self._on_save,  "Save blocks to JSON"),
            ("&Open Workspace",     "Ctrl+O", self._on_open,  "Load blocks from JSON"),
            ("&New / Clear",        "Ctrl+N", self._on_clear, "Reset workspace"),
        ]:
            act = QAction(label, self)
            act.setShortcut(QKeySequence(shortcut))
            act.setStatusTip(tip)
            act.triggered.connect(slot)
            file_menu.addAction(act)
        file_menu.addSeparator()
        quit_act = QAction("&Quit", self)
        quit_act.setShortcut(QKeySequence("Ctrl+Q"))
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        help_menu: QMenu = mb.addMenu("&Help")
        about_act = QAction("&About SparkIDE", self)
        about_act.triggered.connect(self._on_about)
        help_menu.addAction(about_act)

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self):
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        tb.setFixedHeight(46)
        tb.setStyleSheet(
            f"QToolBar {{"
            f"  background: {BG_DEEP};"
            f"  border-bottom: 1px solid {BORDER};"
            f"  padding: 0 12px;"
            f"  spacing: 4px;"
            f"}}"
            f"QToolBar::separator {{"
            f"  background: {BORDER_HI};"
            f"  width: 1px;"
            f"  margin: 8px 6px;"
            f"}}"
        )
        self.addToolBar(tb)

        # ── Brand mark ──────────────────────────────────────────────────────
        brand = QLabel("⚡ SparkIDE")
        brand.setStyleSheet(
            "color: #e8e8e8; font-size: 14px; font-weight: 700;"
            "padding-right: 14px; letter-spacing: 0.5px;"
        )
        tb.addWidget(brand)
        tb.addSeparator()

        # ── Board selector ──────────────────────────────────────────────────
        tb.addWidget(self._tb_label("Board"))
        self._board_combo = self._make_combo(PLACEHOLDER_BOARDS, 145)
        self._board_combo.currentTextChanged.connect(self._update_status)
        tb.addWidget(self._board_combo)

        tb.addSeparator()

        # ── Port selector ───────────────────────────────────────────────────
        tb.addWidget(self._tb_label("Port"))
        self._port_combo = self._make_combo(PLACEHOLDER_PORTS, 145)
        self._port_combo.currentTextChanged.connect(self._update_status)
        tb.addWidget(self._port_combo)

        refresh_btn = self._make_btn("↺", secondary=True, tooltip="Refresh boards and ports")
        refresh_btn.setFixedWidth(32)
        refresh_btn.clicked.connect(self._on_refresh_ports)
        tb.addWidget(refresh_btn)

        # ── Spacer ──────────────────────────────────────────────────────────
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        # ── Action buttons ──────────────────────────────────────────────────
        compile_btn = self._make_btn("⚡  Compile", color=ACCENT_GRN, hover=ACCENT_GRN_HI,
                                     tooltip="Compile sketch (arduino-cli)")
        compile_btn.clicked.connect(self._on_compile)
        tb.addWidget(compile_btn)

        upload_btn = self._make_btn("⬆  Upload", color=ACCENT_BLU, hover=ACCENT_BLU_HI,
                                    tooltip="Compile & upload to board")
        upload_btn.clicked.connect(self._on_upload)
        tb.addWidget(upload_btn)

    # ── Central widget ────────────────────────────────────────────────────────

    def _build_central(self):
        self._code_panel = CodePanel()
        self._web_view = QWebEngineView()
        self._web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self._setup_web_channel()
        self._web_view.setUrl(QUrl.fromLocalFile(str(BLOCKLY_HTML)))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {BORDER}; }}"
            f"QSplitter::handle:hover {{ background: {BORDER_HI}; }}"
        )
        splitter.addWidget(self._web_view)
        splitter.addWidget(self._code_panel)
        splitter.setSizes([700, 460])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self.setCentralWidget(splitter)

    def _setup_web_channel(self):
        self._channel = QWebChannel()
        self._bridge  = Bridge()
        self._channel.registerObject("bridge", self._bridge)
        self._web_view.page().setWebChannel(self._channel)
        self._bridge.set_page(self._web_view.page())
        self._bridge.code_changed.connect(self._code_panel.update_code)

    # ── Log dock ──────────────────────────────────────────────────────────────

    def _build_log_dock(self):
        self._log_panel = LogPanel()

        dock = QDockWidget("Output", self)
        dock.setWidget(self._log_panel)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable  |
            QDockWidget.DockWidgetFeature.DockWidgetMovable   |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        dock.setMinimumHeight(130)
        dock.setStyleSheet(
            f"QDockWidget {{ color: {TEXT_MID}; font-size: 11px; }}"
            f"QDockWidget::title {{"
            f"  background: {BG_DEEP};"
            f"  padding: 5px 8px;"
            f"  border-bottom: 1px solid {BORDER};"
            f"}}"
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_status_bar(self):
        sb = QStatusBar()
        sb.setFixedHeight(26)
        sb.setStyleSheet(
            f"QStatusBar {{ background: {BG_DEEP}; border-top: 1px solid {BORDER}; }}"
            f"QStatusBar::item {{ border: none; }}"
        )
        self.setStatusBar(sb)

        # Board pill
        self._sb_board = self._status_pill("💻", "Board", "#264f78")
        sb.addWidget(self._sb_board)

        # Port pill
        self._sb_port = self._status_pill("🔌", "Port", "#2d5a27")
        sb.addWidget(self._sb_port)

        # Status indicator (right side)
        self._sb_status = QLabel("● Idle")
        self._sb_status.setStyleSheet(f"color: #4e9a51; font-size: 11px; padding: 0 10px;")
        sb.addPermanentWidget(self._sb_status)

        self._update_status()

    @staticmethod
    def _status_pill(icon: str, label: str, bg: str) -> QLabel:
        lbl = QLabel(f"  {icon}  {label}  ")
        lbl.setStyleSheet(
            f"QLabel {{ background: {bg}18; color: {TEXT_MID}; font-size: 11px;"
            f" padding: 2px 8px; border-radius: 3px; margin: 3px 4px; }}"
        )
        return lbl

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_compile(self):
        self._log_panel.append_line("[ Coming soon ]  Compile — arduino-cli integration in next phase.", "warning")

    def _on_upload(self):
        self._log_panel.append_line("[ Coming soon ]  Upload — arduino-cli integration in next phase.", "warning")

    def _on_refresh_ports(self):
        self._log_panel.append_line("[ Coming soon ]  Refresh ports — arduino-cli integration in next phase.", "warning")

    def _on_save(self):
        def _write(json_str: str):
            if not json_str:
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Workspace", "workspace.json", "JSON Files (*.json)"
            )
            if path:
                Path(path).write_text(json_str)
                self._log_panel.append_line(f"✔  Workspace saved → {path}", "success")
        self._bridge.get_workspace_json(_write)

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Workspace", "", "JSON Files (*.json)"
        )
        if path:
            self._bridge.load_workspace(Path(path).read_text())
            self._log_panel.append_line(f"✔  Workspace loaded ← {path}", "success")

    def _on_clear(self):
        self._web_view.page().runJavaScript("window.clearWorkspace();")
        self._log_panel.append_line("Workspace cleared.", "info")

    def _on_about(self):
        QMessageBox.about(
            self,
            "About SparkIDE",
            "<b>SparkIDE v0.1</b><br>"
            "Visual Arduino programming for Linux.<br><br>"
            "Drag blocks → see generated C++ → compile & upload.<br><br>"
            "<a href='https://github.com/harshverma27/SparkIDE'>"
            "github.com/harshverma27/SparkIDE</a>",
        )

    # ── Status helpers ────────────────────────────────────────────────────────

    def _update_status(self):
        b = getattr(self, "_board_combo", None)
        p = getattr(self, "_port_combo",  None)
        board = b.currentText() if b else "—"
        port  = p.currentText() if p else "—"

        if hasattr(self, "_sb_board"):
            self._sb_board.setText(f"  💻  {board}  ")
        if hasattr(self, "_sb_port"):
            self._sb_port.setText(f"  🔌  {port}  ")

    # ── Widget factory helpers ────────────────────────────────────────────────

    @staticmethod
    def _tb_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 10px; font-weight: 600;"
            f" letter-spacing: 0.5px; margin-left: 6px; margin-right: 2px;"
        )
        return lbl

    @staticmethod
    def _make_combo(items: list, width: int) -> QComboBox:
        cb = QComboBox()
        cb.addItems(items)
        cb.setFixedWidth(width)
        cb.setFixedHeight(28)
        cb.setStyleSheet(
            f"QComboBox {{ background: {BG_RAISED}; color: {TEXT_MAIN};"
            f" border: 1px solid {BORDER}; border-radius: 5px; padding: 2px 10px;"
            f" font-size: 12px; }}"
            f"QComboBox:hover {{ border: 1px solid {BORDER_HI}; }}"
            f"QComboBox::drop-down {{ border: none; width: 20px; }}"
            f"QComboBox QAbstractItemView {{ background: {BG_DARK}; color: {TEXT_MAIN};"
            f" border: 1px solid {BORDER_HI}; selection-background-color: #264f78; }}"
        )
        return cb

    @staticmethod
    def _make_btn(label: str, color: str = "", hover: str = "",
                  secondary: bool = False, tooltip: str = "") -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(30)
        if tooltip:
            btn.setToolTip(tooltip)
        if secondary:
            btn.setStyleSheet(
                f"QPushButton {{ background: {BG_RAISED}; color: {TEXT_MID};"
                f" border: 1px solid {BORDER}; border-radius: 5px;"
                f" padding: 0 10px; font-size: 12px; }}"
                f"QPushButton:hover {{ background: #303030; color: {TEXT_MAIN};"
                f" border-color: {BORDER_HI}; }}"
                f"QPushButton:pressed {{ background: {BG_DARK}; }}"
            )
        else:
            btn.setFixedWidth(110)
            btn.setStyleSheet(
                f"QPushButton {{ background: {color}; color: #ffffff;"
                f" border: none; border-radius: 5px;"
                f" padding: 0 14px; font-size: 12px; font-weight: 600; }}"
                f"QPushButton:hover {{ background: {hover}; }}"
                f"QPushButton:pressed {{ background: {hover}; }}"
            )
        return btn
