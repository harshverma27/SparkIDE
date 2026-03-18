"""
ui/main_window.py — PyQt6 Main Application Window.
"""

import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QToolBar, QStatusBar,
    QDockWidget, QSizePolicy, QMenu, QFileDialog, QMessageBox,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt, QSize, QUrl

from ui.code_panel import CodePanel
from ui.log_panel import LogPanel
from bridge.channel import Bridge


# ── Placeholder board / port data (real data from arduino-cli in next phase) ──
PLACEHOLDER_BOARDS = ["Arduino Uno", "Arduino Nano", "Arduino Mega"]
PLACEHOLDER_PORTS  = ["/dev/ttyUSB0", "/dev/ttyACM0", "/dev/ttyUSB1"]

# Absolute path to the Blockly host page
BLOCKLY_HTML = Path(__file__).parent.parent / "blockly" / "index.html"


class MainWindow(QMainWindow):
    """Top-level application window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SparkIDE")
        self.setMinimumSize(1024, 640)
        self.resize(1280, 760)

        # Build UI in order (central must be before dock so code_panel exists)
        self._build_menu_bar()
        self._build_toolbar()
        self._build_central()   # creates self._code_panel, self._web_view, self._bridge
        self._build_log_dock()
        self._build_status_bar()

    # ── Menu bar ──────────────────────────────────────────────────────────────

    def _build_menu_bar(self):
        mb = self.menuBar()

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

        clear_act = QAction("&New / Clear Workspace", self)
        clear_act.setShortcut(QKeySequence("Ctrl+N"))
        clear_act.triggered.connect(self._on_clear)
        file_menu.addAction(clear_act)

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
        tb.setStyleSheet(
            "QToolBar {"
            "  background: #1e1e1e;"
            "  border-bottom: 1px solid #3a3a3a;"
            "  padding: 4px 8px;"
            "  spacing: 6px;"
            "}"
        )
        self.addToolBar(tb)

        tb.addWidget(self._small_label("Board:"))
        self._board_combo = QComboBox()
        self._board_combo.addItems(PLACEHOLDER_BOARDS)
        self._board_combo.setFixedWidth(140)
        self._board_combo.setStyleSheet(self._combo_style())
        self._board_combo.currentTextChanged.connect(self._update_status)
        tb.addWidget(self._board_combo)

        tb.addSeparator()

        tb.addWidget(self._small_label("Port:"))
        self._port_combo = QComboBox()
        self._port_combo.addItems(PLACEHOLDER_PORTS)
        self._port_combo.setFixedWidth(140)
        self._port_combo.setStyleSheet(self._combo_style())
        self._port_combo.currentTextChanged.connect(self._update_status)
        tb.addWidget(self._port_combo)

        refresh_btn = QPushButton("↺  Refresh")
        refresh_btn.setFixedHeight(28)
        refresh_btn.setStyleSheet(self._secondary_btn_style())
        refresh_btn.clicked.connect(self._on_refresh_ports)
        tb.addWidget(refresh_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        compile_btn = QPushButton("⚡  Compile")
        compile_btn.setFixedHeight(30)
        compile_btn.setStyleSheet(self._primary_btn_style("#2d8a4e", "#236e3d"))
        compile_btn.setStatusTip("Compile sketch with arduino-cli")
        compile_btn.clicked.connect(self._on_compile)
        tb.addWidget(compile_btn)

        upload_btn = QPushButton("⬆  Upload")
        upload_btn.setFixedHeight(30)
        upload_btn.setStyleSheet(self._primary_btn_style("#1a6fb5", "#155c99"))
        upload_btn.setStatusTip("Upload sketch to connected Arduino")
        upload_btn.clicked.connect(self._on_upload)
        tb.addWidget(upload_btn)

    # ── Central widget ────────────────────────────────────────────────────────

    def _build_central(self):
        # 1. Code panel (right side)
        self._code_panel = CodePanel()

        # 2. Blockly WebView (left side)
        self._web_view = QWebEngineView()

        # Allow local file:// page to load remote CDN scripts (Blockly from unpkg)
        self._web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )

        # 3. Wire up QWebChannel bridge BEFORE loading the URL
        self._setup_web_channel()

        # 4. Load the Blockly HTML page
        self._web_view.setUrl(QUrl.fromLocalFile(str(BLOCKLY_HTML)))

        # 5. Splitter layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #3a3a3a; }")
        splitter.addWidget(self._web_view)
        splitter.addWidget(self._code_panel)
        splitter.setSizes([640, 440])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        self.setCentralWidget(splitter)

    def _setup_web_channel(self):
        """Create QWebChannel, register Bridge, connect signals."""
        self._channel = QWebChannel()
        self._bridge  = Bridge()

        # Register bridge so JS can access it as channel.objects.bridge
        self._channel.registerObject("bridge", self._bridge)
        self._web_view.page().setWebChannel(self._channel)

        # Store page ref on bridge so it can call runJavaScript
        self._bridge.set_page(self._web_view.page())

        # Every time Blockly changes → update the code panel
        self._bridge.code_changed.connect(self._code_panel.update_code)

    # ── Log dock ──────────────────────────────────────────────────────────────

    def _build_log_dock(self):
        self._log_panel = LogPanel()

        dock = QDockWidget("Output", self)
        dock.setWidget(self._log_panel)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable  |
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
            "QStatusBar { background:#1a1a1a; color:#666; font-size:11px;"
            " border-top:1px solid #3a3a3a; }"
        )
        self.setStatusBar(sb)
        self._status_label = QLabel(self._status_text())
        self._status_label.setStyleSheet("color:#666; padding: 0 8px;")
        sb.addPermanentWidget(self._status_label)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_compile(self):
        # Phase 3: wire up to ArduinoCLI.compile()
        self._log_panel.append_line("[ Coming soon ] Compile — arduino-cli integration in next phase.", "warning")

    def _on_upload(self):
        # Phase 3: wire up to ArduinoCLI.upload()
        self._log_panel.append_line("[ Coming soon ] Upload — arduino-cli integration in next phase.", "warning")

    def _on_refresh_ports(self):
        # Phase 3: call ArduinoCLI.list_boards() and repopulate combos
        self._log_panel.append_line("[ Coming soon ] Refresh ports — arduino-cli integration in next phase.", "warning")

    def _on_save(self):
        """Save the Blockly workspace JSON to a file (Ctrl+S)."""
        def _write(json_str: str):
            if not json_str:
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Save Workspace", "workspace.json", "JSON Files (*.json)"
            )
            if path:
                Path(path).write_text(json_str)
                self._log_panel.append_line(f"Workspace saved → {path}", "success")

        self._bridge.get_workspace_json(_write)

    def _on_open(self):
        """Load a Blockly workspace JSON from a file (Ctrl+O)."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Workspace", "", "JSON Files (*.json)"
        )
        if path:
            json_str = Path(path).read_text()
            self._bridge.load_workspace(json_str)
            self._log_panel.append_line(f"Workspace loaded ← {path}", "success")

    def _on_clear(self):
        """Reset the workspace to an empty setup/loop block."""
        self._web_view.page().runJavaScript("window.clearWorkspace();")
        self._log_panel.append_line("Workspace cleared.", "info")

    def _on_about(self):
        QMessageBox.about(
            self,
            "About SparkIDE",
            "<b>SparkIDE v0.1</b><br>"
            "Visual Arduino programming for Linux.<br><br>"
            "Drag blocks → see C++ → click upload.<br><br>"
            "<a href='https://github.com/harshverma27/SparkIDE'>"
            "github.com/harshverma27/SparkIDE</a>",
        )

    # ── Status helpers ────────────────────────────────────────────────────────

    def _status_text(self) -> str:
        b = getattr(self, "_board_combo", None)
        p = getattr(self, "_port_combo",  None)
        board = b.currentText() if b else "—"
        port  = p.currentText() if p else "—"
        return f"Board: {board}   |   Port: {port}   |   Status: Idle"

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
            "QComboBox { background:#2a2a2a; color:#ccc; border:1px solid #444;"
            " border-radius:4px; padding:2px 8px; font-size:12px; }"
            "QComboBox:hover { border:1px solid #666; }"
            "QComboBox QAbstractItemView { background:#2a2a2a; color:#ccc;"
            " selection-background-color:#3e4451; }"
        )

    @staticmethod
    def _secondary_btn_style() -> str:
        return (
            "QPushButton { background:#2a2a2a; color:#aaa; border:1px solid #444;"
            " border-radius:4px; padding:2px 12px; font-size:12px; }"
            "QPushButton:hover { background:#333; color:#ccc; border-color:#666; }"
            "QPushButton:pressed { background:#222; }"
        )

    @staticmethod
    def _primary_btn_style(bg: str, hover_bg: str) -> str:
        return (
            f"QPushButton {{ background:{bg}; color:#fff; border:none;"
            f" border-radius:4px; padding:2px 16px; font-size:12px; font-weight:600; }}"
            f"QPushButton:hover {{ background:{hover_bg}; }}"
            f"QPushButton:pressed {{ background:{hover_bg}; }}"
        )
