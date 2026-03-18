"""
ui/main_window.py — PyQt6 Main Application Window.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QToolBar, QStatusBar,
    QDockWidget, QSizePolicy, QMenuBar, QMenu, QFileDialog,
    QMessageBox,
)
from PyQt6.QtGui import QAction, QIcon, QFont, QKeySequence
from PyQt6.QtCore import Qt, QSize

from ui.code_panel import CodePanel
from ui.log_panel import LogPanel


# ── Placeholder board / port data (real data from arduino-cli in Phase 2) ─────
PLACEHOLDER_BOARDS = ["Arduino Uno", "Arduino Nano", "Arduino Mega"]
PLACEHOLDER_PORTS  = ["/dev/ttyUSB0", "/dev/ttyACM0", "/dev/ttyUSB1"]


class BlocklyPlaceholder(QWidget):
    """Temporary placeholder for the Blockly QWebEngineView."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #252526;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel("🧱")
        icon_label.setFont(QFont("Segoe UI Emoji", 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("color: #444; background: transparent;")

        text_label = QLabel("Blockly editor loads here")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("color: #555; font-size: 14px; background: transparent;")

        sub_label = QLabel("(Phase 2: QWebEngineView + Google Blockly)")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet("color: #3a3a3a; font-size: 11px; background: transparent;")

        layout.addWidget(icon_label)
        layout.addSpacing(8)
        layout.addWidget(text_label)
        layout.addSpacing(4)
        layout.addWidget(sub_label)


class MainWindow(QMainWindow):
    """Top-level application window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SparkIDE")
        self.setMinimumSize(1024, 640)
        self.resize(1280, 760)

        self._build_menu_bar()
        self._build_toolbar()
        self._build_central()
        self._build_log_dock()
        self._build_status_bar()

    # ── Menu bar ──────────────────────────────────────────────────────────────

    def _build_menu_bar(self):
        mb = self.menuBar()

        # File menu
        file_menu: QMenu = mb.addMenu("&File")

        save_act = QAction("&Save Workspace", self)
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.setStatusTip("Save current block workspace to a JSON file")
        save_act.triggered.connect(self._on_save)
        file_menu.addAction(save_act)

        open_act = QAction("&Open Workspace", self)
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.setStatusTip("Load a saved block workspace from a JSON file")
        open_act.triggered.connect(self._on_open)
        file_menu.addAction(open_act)

        file_menu.addSeparator()

        quit_act = QAction("&Quit", self)
        quit_act.setShortcut(QKeySequence("Ctrl+Q"))
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        # Help menu
        help_menu: QMenu = mb.addMenu("&Help")

        about_act = QAction("&About SparkIDE", self)
        about_act.triggered.connect(self._on_about)
        help_menu.addAction(about_act)

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self):
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        tb.setStyleSheet(
            "QToolBar {"
            "  background: #1e1e1e;"
            "  border-bottom: 1px solid #3a3a3a;"
            "  padding: 4px 8px;"
            "  spacing: 6px;"
            "}"
        )
        self.addToolBar(tb)

        # ── Board selector ─────────────────────────────────────────────────
        tb.addWidget(self._small_label("Board:"))
        self._board_combo = QComboBox()
        self._board_combo.addItems(PLACEHOLDER_BOARDS)
        self._board_combo.setFixedWidth(140)
        self._board_combo.setStyleSheet(self._combo_style())
        self._board_combo.currentTextChanged.connect(self._on_board_changed)
        tb.addWidget(self._board_combo)

        tb.addSeparator()

        # ── Port selector ──────────────────────────────────────────────────
        tb.addWidget(self._small_label("Port:"))
        self._port_combo = QComboBox()
        self._port_combo.addItems(PLACEHOLDER_PORTS)
        self._port_combo.setFixedWidth(140)
        self._port_combo.setStyleSheet(self._combo_style())
        self._port_combo.currentTextChanged.connect(self._on_port_changed)
        tb.addWidget(self._port_combo)

        # ── Refresh ports button ───────────────────────────────────────────
        refresh_btn = QPushButton("↺  Refresh")
        refresh_btn.setFixedHeight(28)
        refresh_btn.setStyleSheet(self._secondary_btn_style())
        refresh_btn.clicked.connect(self._on_refresh_ports)
        tb.addWidget(refresh_btn)

        # Spacer to push Compile / Upload to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        # ── Compile button ─────────────────────────────────────────────────
        compile_btn = QPushButton("⚡  Compile")
        compile_btn.setFixedHeight(30)
        compile_btn.setStyleSheet(self._primary_btn_style("#2d8a4e", "#236e3d"))
        compile_btn.setStatusTip("Compile sketch with arduino-cli")
        compile_btn.clicked.connect(self._on_compile)
        tb.addWidget(compile_btn)

        # ── Upload button ──────────────────────────────────────────────────
        upload_btn = QPushButton("⬆  Upload")
        upload_btn.setFixedHeight(30)
        upload_btn.setStyleSheet(self._primary_btn_style("#1a6fb5", "#155c99"))
        upload_btn.setStatusTip("Upload sketch to connected Arduino")
        upload_btn.clicked.connect(self._on_upload)
        tb.addWidget(upload_btn)

    # ── Central widget ────────────────────────────────────────────────────────

    def _build_central(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #3a3a3a; }")

        # Left: Blockly placeholder
        self._blockly_placeholder = BlocklyPlaceholder()
        splitter.addWidget(self._blockly_placeholder)

        # Right: C++ preview
        self._code_panel = CodePanel()
        splitter.addWidget(self._code_panel)

        # Give Blockly 60%, code panel 40%
        splitter.setSizes([640, 440])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self.setCentralWidget(splitter)

    # ── Log dock ──────────────────────────────────────────────────────────────

    def _build_log_dock(self):
        self._log_panel = LogPanel()

        dock = QDockWidget("Output", self)
        dock.setWidget(self._log_panel)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        dock.setMinimumHeight(120)
        dock.setStyleSheet(
            "QDockWidget { color: #ccc; font-size:12px; }"
            "QDockWidget::title { background:#1a1a1a; padding-left:8px; }"
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_status_bar(self):
        sb = QStatusBar()
        sb.setStyleSheet(
            "QStatusBar { background:#1a1a1a; color:#666; font-size:11px; border-top:1px solid #3a3a3a; }"
        )
        self.setStatusBar(sb)
        self._status_label = QLabel(self._status_text())
        self._status_label.setStyleSheet("color:#666; padding: 0 8px;")
        sb.addPermanentWidget(self._status_label)

    # ── Stub actions ──────────────────────────────────────────────────────────

    def _on_compile(self):
        # Phase 2: call ArduinoCLI.compile()
        self._log_panel.append_line("[ Stub ] Compile pressed — wiring up in Phase 2.", "warning")

    def _on_upload(self):
        # Phase 2: call ArduinoCLI.upload()
        self._log_panel.append_line("[ Stub ] Upload pressed — wiring up in Phase 2.", "warning")

    def _on_refresh_ports(self):
        # Phase 2: call ArduinoCLI.list_boards() and repopulate combo
        self._log_panel.append_line("[ Stub ] Refresh ports — wiring up in Phase 2.", "warning")

    def _on_save(self):
        # Phase 2: call JS getWorkspaceJson() then write to file
        self._log_panel.append_line("[ Stub ] Save workspace — wiring up in Phase 2.", "warning")

    def _on_open(self):
        # Phase 2: open file dialog, read JSON, call JS loadWorkspace()
        self._log_panel.append_line("[ Stub ] Open workspace — wiring up in Phase 2.", "warning")

    def _on_board_changed(self, board: str):
        self._update_status()

    def _on_port_changed(self, port: str):
        self._update_status()

    def _on_about(self):
        QMessageBox.about(
            self,
            "About SparkIDE",
            "<b>SparkIDE v0.1</b><br>"
            "Visual Arduino programming for Linux.<br><br>"
            "Drag blocks → see C++ → click upload.<br>"
            "<a href='https://github.com/harshverma27/SparkIDE'>github.com/harshverma27/SparkIDE</a>",
        )

    # ── Status helpers ────────────────────────────────────────────────────────

    def _status_text(self) -> str:
        board = getattr(self, "_board_combo", None)
        port  = getattr(self, "_port_combo", None)
        b = board.currentText() if board else "—"
        p = port.currentText()  if port  else "—"
        return f"Board: {b}   |   Port: {p}   |   Status: Idle"

    def _update_status(self):
        self._status_label.setText(self._status_text())

    # ── Style helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _small_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("color:#888; font-size:11px; margin-left:4px;")
        return lbl

    @staticmethod
    def _combo_style() -> str:
        return (
            "QComboBox {"
            "  background:#2a2a2a; color:#ccc; border:1px solid #444;"
            "  border-radius:4px; padding:2px 8px; font-size:12px;"
            "}"
            "QComboBox:hover { border:1px solid #666; }"
            "QComboBox QAbstractItemView {"
            "  background:#2a2a2a; color:#ccc; selection-background-color:#3e4451;"
            "}"
        )

    @staticmethod
    def _secondary_btn_style() -> str:
        return (
            "QPushButton {"
            "  background:#2a2a2a; color:#aaa; border:1px solid #444;"
            "  border-radius:4px; padding:2px 12px; font-size:12px;"
            "}"
            "QPushButton:hover { background:#333; color:#ccc; border-color:#666; }"
            "QPushButton:pressed { background:#222; }"
        )

    @staticmethod
    def _primary_btn_style(bg: str, hover_bg: str) -> str:
        return (
            f"QPushButton {{"
            f"  background:{bg}; color:#fff; border:none;"
            f"  border-radius:4px; padding:2px 16px; font-size:12px; font-weight:600;"
            f"}}"
            f"QPushButton:hover {{ background:{hover_bg}; }}"
            f"QPushButton:pressed {{ background:{hover_bg}; opacity:0.8; }}"
        )
