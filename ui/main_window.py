"""
ui/main_window.py — PyQt6 main application window (shell + actions).

Composition only: the toolbar and status bar are built by ToolbarMixin /
StatusBarMixin, design tokens live in ui/theme.py, background jobs in
ui/workers.py, and identity/paths in app_config. What remains here is the window
shell (menu, central web view, log dock) and the action slots.
"""

from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app_config import (
    APP_NAME,
    APP_TAGLINE,
    APP_VERSION,
    BLOCKLY_HTML,
    REPO_URL,
    WINDOW_DEFAULT_SIZE,
    WINDOW_MIN_SIZE,
)
from bridge.channel import Bridge
from cli.arduino_cli import BoardOption
from project import recent
from project.autosave import files_to_autosave
from project.model import Project, create_project, open_project
from ui import theme
from ui.board_manager import BoardManagerDialog
from ui.editor.editor_tabs import EditorTabs
from ui.log_panel import LogPanel
from ui.serial_panel import SerialPanel
from ui.status_bar import StatusBarMixin
from ui.toolbar import ToolbarMixin
from ui.workers import ArduinoJobWorker, BoardRefreshWorker, SerialReadWorker


class MainWindow(ToolbarMixin, StatusBarMixin, QMainWindow):
    """Top-level application window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.resize(*WINDOW_DEFAULT_SIZE)
        self._refresh_worker = None
        self._job_worker = None
        self._project: Project | None = None
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(30_000)
        self._autosave_timer.timeout.connect(self._on_autosave)

        self.setStyleSheet(theme.window_stylesheet())

        self._build_menu_bar()
        self._build_toolbar()
        self._build_central()
        self._build_log_dock()
        self._build_serial_dock()
        self._build_status_bar()
        self._on_refresh_ports()

    # ── Menu bar ──────────────────────────────────────────────────────────────

    def _build_menu_bar(self):
        mb = self.menuBar()
        mb.setStyleSheet(
            f"QMenuBar {{ background: {theme.BG_DEEP}; color: {theme.TEXT_MID};"
            f" border-bottom: 1px solid {theme.BORDER}; }}"
            f"QMenuBar::item:selected {{ background: {theme.BG_RAISED}; color: {theme.TEXT_MAIN}; }}"
            f"QMenu {{ background: {theme.BG_DARK}; color: {theme.TEXT_MAIN};"
            f" border: 1px solid {theme.BORDER_HI}; }}"
            f"QMenu::item:selected {{ background: #1d3a2c; }}"
        )

        file_menu: QMenu = mb.addMenu("&File")
        for label, shortcut, slot, tip in [
            ("&Save Workspace", "Ctrl+S", self._on_save, "Save blocks to JSON"),
            ("&Open Workspace", "Ctrl+O", self._on_open, "Load blocks from JSON"),
            ("&New / Clear", "Ctrl+N", self._on_clear, "Reset workspace"),
        ]:
            act = QAction(label, self)
            act.setShortcut(QKeySequence(shortcut))
            act.setStatusTip(tip)
            act.triggered.connect(slot)
            file_menu.addAction(act)
        file_menu.addSeparator()
        for label, shortcut, slot, tip in [
            (
                "New &Project…",
                "Ctrl+Shift+N",
                self._on_new_project,
                "Create a sketch-folder project",
            ),
            (
                "Open Pro&ject…",
                "Ctrl+Shift+O",
                self._on_open_project,
                "Open an existing sketch folder",
            ),
            ("Ne&w File…", "", self._on_new_file, "Add a file to the current project"),
        ]:
            act = QAction(label, self)
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            act.setStatusTip(tip)
            act.triggered.connect(slot)
            file_menu.addAction(act)
        self._recent_menu = file_menu.addMenu("Open &Recent")
        self._recent_menu.aboutToShow.connect(self._rebuild_recent_menu)
        file_menu.addSeparator()
        quit_act = QAction("&Quit", self)
        quit_act.setShortcut(QKeySequence("Ctrl+Q"))
        quit_act.triggered.connect(self.close)
        file_menu.addAction(quit_act)

        tools_menu = mb.addMenu("&Tools")
        bm_act = QAction("&Boards Manager…", self)
        bm_act.setStatusTip("Install, update, or remove Arduino cores")
        bm_act.triggered.connect(self._on_boards_manager)
        tools_menu.addAction(bm_act)

        help_menu: QMenu = mb.addMenu("&Help")
        about_act = QAction("&About SparkIDE", self)
        about_act.triggered.connect(self._on_about)
        help_menu.addAction(about_act)

    # ── Central widget ────────────────────────────────────────────────────────

    def _build_central(self):
        self._editor = EditorTabs()
        self._web_view = QWebEngineView()
        self._web_view.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True
        )
        self._setup_web_channel()
        self._web_view.setUrl(QUrl.fromLocalFile(str(BLOCKLY_HTML)))

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {theme.BORDER}; }}"
            f"QSplitter::handle:hover {{ background: {theme.BORDER_HI}; }}"
        )
        splitter.addWidget(self._web_view)
        splitter.addWidget(self._editor)
        splitter.setSizes([700, 460])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        shell = QWidget()
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(16, 16, 16, 12)
        shell_layout.setSpacing(0)

        frame = QWidget()
        frame.setStyleSheet(
            f"background: {theme.BG_PANEL};border: 1px solid {theme.BORDER};border-radius: 8px;"
        )
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(splitter)

        shell_layout.addWidget(frame)
        self.setCentralWidget(shell)

    def _setup_web_channel(self):
        self._channel = QWebChannel()
        self._bridge = Bridge()
        self._channel.registerObject("bridge", self._bridge)
        self._web_view.page().setWebChannel(self._channel)
        self._bridge.set_page(self._web_view.page())
        self._bridge.code_changed.connect(self._editor.update_code)
        self._bridge.block_count_changed.connect(self._update_block_count)

    # ── Log dock ──────────────────────────────────────────────────────────────

    def _build_log_dock(self):
        self._log_panel = LogPanel()

        dock = QDockWidget("Output", self)
        dock.setWidget(self._log_panel)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        dock.setMinimumHeight(130)
        dock.setStyleSheet(
            f"QDockWidget {{ color: {theme.TEXT_MID}; font-family: {theme.FONT_MONO};"
            f" font-size: 11px; }}"
            f"QDockWidget::title {{"
            f"  background: {theme.BG_DEEP};"
            f"  padding: 5px 8px;"
            f"  border-bottom: 1px solid {theme.BORDER};"
            f"}}"
        )
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        self._log_dock = dock

    # ── Serial dock ─────────────────────────────────────────────────────────────

    def _build_serial_dock(self):
        self._serial_panel = SerialPanel()
        self._serial_worker = None
        self._reconnect_after_job = None
        dock = QDockWidget("Serial", self)
        dock.setWidget(self._serial_panel)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        dock.setMinimumHeight(160)
        dock.setStyleSheet(self._log_dock.styleSheet())
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        self._serial_dock = dock
        self.tabifyDockWidget(self._log_dock, dock)
        self._log_dock.raise_()
        self._serial_panel.connect_requested.connect(self._on_serial_connect)
        self._serial_panel.disconnect_requested.connect(self._on_serial_disconnect)
        self._serial_panel.send_requested.connect(self._on_serial_send)

    def _on_serial_connect(self, baud: int):
        port = self._selected_port()
        if not port:
            self._show_warning("Select a serial port before connecting.")
            self._serial_panel.set_connected(False)
            return
        self._serial_worker = SerialReadWorker(port, baud, self)
        self._serial_worker.line_received.connect(self._serial_panel.append_output)
        self._serial_worker.connection_error.connect(self._on_serial_error)
        self._serial_worker.start()
        self._serial_panel.set_connected(True)
        self._log_panel.append_line(f"Serial connected: {port} @ {baud} baud", "success")

    def _on_serial_disconnect(self):
        if self._serial_worker:
            self._serial_worker.stop()
            self._serial_worker = None
        self._serial_panel.set_connected(False)
        self._log_panel.append_line("Serial disconnected.", "info")

    def _on_serial_send(self, text: str, ending: str):
        if self._serial_worker:
            self._serial_worker.send(text, ending)

    def _on_serial_error(self, message: str):
        self._log_panel.append_line(f"Serial error: {message}", "error")
        self._serial_worker = None
        self._serial_panel.set_connected(False)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_compile(self):
        board = self._selected_board()
        if not board:
            self._show_warning("Select a board before compiling.")
            return
        self._start_job("compile", board.fqbn, "")

    def _on_upload(self):
        board = self._selected_board()
        port = self._selected_port() or (board.port if board else "")
        if not board:
            self._show_warning("Select a board before uploading.")
            return
        if not port:
            self._show_warning("Connect a board and select a serial port before uploading.")
            return
        self._start_job("upload", board.fqbn, port)

    def _on_refresh_ports(self):
        if self._refresh_worker and self._refresh_worker.isRunning():
            return
        if hasattr(self, "_refresh_btn"):
            self._refresh_btn.setEnabled(False)
        self._set_status("● Scanning", "#e5c07b")
        if hasattr(self, "_log_panel"):
            self._log_panel.append_line("Scanning boards and ports...", "info")
        self._refresh_worker = BoardRefreshWorker(self)
        self._refresh_worker.finished.connect(self._on_boards_loaded)
        self._refresh_worker.start()

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
        path, _ = QFileDialog.getOpenFileName(self, "Open Workspace", "", "JSON Files (*.json)")
        if path:
            self._bridge.load_workspace(Path(path).read_text())
            self._log_panel.append_line(f"✔  Workspace loaded ← {path}", "success")

    def _on_clear(self):
        self._web_view.page().runJavaScript("window.clearWorkspace();")
        self._log_panel.append_line("Workspace cleared.", "info")

    # ── Project lifecycle ───────────────────────────────────────────────────────

    def _on_new_project(self):
        parent = QFileDialog.getExistingDirectory(self, "Choose parent folder for new project")
        if not parent:
            return
        name, ok = QInputDialog.getText(self, "New Project", "Project name (letters, digits, _):")
        if not ok or not name:
            return
        try:
            proj = create_project(Path(parent), name)
        except (ValueError, FileExistsError, OSError) as exc:
            self._show_warning(f"Could not create project: {exc}")
            return
        self._load_project(proj)

    def _on_open_project(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Project (sketch folder)")
        if not folder:
            return
        try:
            proj = open_project(Path(folder))
        except ValueError as exc:
            self._show_warning(str(exc))
            return
        self._load_project(proj)

    def _on_open_recent(self, path: Path):
        try:
            proj = open_project(path)
        except ValueError:
            # load_recent() prunes missing folders on its next read, so nothing to do here.
            self._show_warning(f"Project no longer found: {path}")
            return
        self._load_project(proj)

    def _load_project(self, proj: Project):
        self._project = proj
        recent.add_recent(proj.root)
        ws = proj.workspace_path.read_text(encoding="utf-8") if proj.workspace_path.exists() else ""
        if ws.strip():
            self._bridge.load_workspace(ws)
        for f in proj.companion_files():
            self._editor.open_file(f.path)
        self.setWindowTitle(f"{APP_NAME} — {proj.name}")
        self._autosave_timer.start()
        self._log_panel.append_line(f"Project opened: {proj.root}", "success")

    def _on_new_file(self):
        if self._project is None:
            self._show_warning("Open or create a project first.")
            return
        name, ok = QInputDialog.getText(self, "New File", "File name (e.g. helpers.h):")
        if not ok or not name:
            return
        path = self._project.root / name
        if path.exists():
            self._show_warning(f"File already exists: {name}")
            return
        self._editor.new_file(path)
        self._log_panel.append_line(f"Created {name}", "success")

    def _rebuild_recent_menu(self):
        self._recent_menu.clear()
        items = recent.load_recent()
        if not items:
            act = QAction("(no recent projects)", self)
            act.setEnabled(False)
            self._recent_menu.addAction(act)
            return
        for path in items:
            act = QAction(path.name, self)
            act.setStatusTip(str(path))
            act.triggered.connect(lambda _checked=False, p=path: self._on_open_recent(p))
            self._recent_menu.addAction(act)

    def _on_autosave(self):
        if self._project is None:
            return
        buffers = self._editor.dirty_buffers()
        on_disk = {}
        for path in buffers:
            try:
                on_disk[path] = path.read_text(encoding="utf-8")
            except OSError:
                on_disk[path] = None
        for path, text in files_to_autosave(buffers, on_disk).items():
            try:
                path.write_text(text, encoding="utf-8")
                self._editor.mark_saved(path)
            except OSError as exc:
                self._log_panel.append_line(f"Autosave failed for {path.name}: {exc}", "warning")

        def _save_ws(json_str: str):
            if json_str:
                try:
                    self._project.workspace_path.write_text(json_str, encoding="utf-8")
                except OSError:
                    pass

        self._bridge.get_workspace_json(_save_ws)

    def _on_about(self):
        QMessageBox.about(
            self,
            f"About {APP_NAME}",
            f"<b>{APP_NAME} v{APP_VERSION}</b><br>"
            f"{APP_TAGLINE}<br><br>"
            "Drag blocks → see generated C++ → compile & upload.<br><br>"
            f"<a href='{REPO_URL}'>{REPO_URL.replace('https://', '')}</a>",
        )

    def _on_center_workspace(self):
        self._web_view.page().runJavaScript("window.centerWorkspace();")

    def _on_zoom_to_fit(self):
        self._web_view.page().runJavaScript("window.zoomToFitWorkspace();")

    # ── Job + board helpers ────────────────────────────────────────────────────

    def _on_boards_loaded(self, boards: list, ports: list, error: str):
        if hasattr(self, "_refresh_btn"):
            self._refresh_btn.setEnabled(True)

        self._board_combo.blockSignals(True)
        self._board_combo.clear()
        seen_fqbn = set()
        for board in boards:
            if board.fqbn in seen_fqbn and not board.detected:
                continue
            seen_fqbn.add(board.fqbn)
            self._board_combo.addItem(board.label, board)
        if self._board_combo.count() == 0:
            self._board_combo.addItem("No boards available", None)
        self._board_combo.blockSignals(False)

        self._port_combo.blockSignals(True)
        self._port_combo.clear()
        if ports:
            for port in ports:
                self._port_combo.addItem(port, port)
        else:
            self._port_combo.addItem("No port detected", "")
        self._port_combo.blockSignals(False)

        if error:
            self._log_panel.append_line(error, "error")
            self._set_status("● CLI error", theme.ACCENT_ERROR)
        elif ports:
            self._log_panel.append_line(f"Found {len(ports)} port(s).", "success")
            self._set_status("● Ready", theme.ACCENT_GRN)
        else:
            self._log_panel.append_line(
                "No serial ports detected. Compile is available; upload needs a connected board.",
                "warning",
            )
            self._set_status("● No port", theme.ACCENT_AMBER)

        self._update_status()

    def _start_job(self, action: str, fqbn: str, port: str):
        if self._job_worker and self._job_worker.isRunning():
            return
        code = self._editor.current_code().strip()
        if not code or "void setup()" not in code or "void loop()" not in code:
            self._show_warning("The generated sketch must include setup() and loop().")
            return

        self._reconnect_after_job = None
        if getattr(self, "_serial_worker", None) is not None and action == "upload":
            self._reconnect_after_job = self._serial_panel.current_baud()
            self._on_serial_disconnect()
            self._log_panel.append_line("Released serial port for upload.", "dim")

        self._set_busy(True)
        self._set_status("● Working", theme.ACCENT_AMBER)
        self._log_panel.append_line(f"Starting {action} for {fqbn}...", "info")
        sketch_dir = self._project.root if self._project is not None else None
        if sketch_dir is not None:
            # keep companion files current before compiling the whole folder
            for path, text in self._editor.dirty_buffers().items():
                try:
                    path.write_text(text, encoding="utf-8")
                    self._editor.mark_saved(path)
                except OSError as exc:
                    self._log_panel.append_line(f"Could not save {path.name}: {exc}", "warning")
        self._job_worker = ArduinoJobWorker(action, fqbn, port, code, self, sketch_dir=sketch_dir)
        self._job_worker.line.connect(self._log_panel.append_line)
        self._job_worker.stats.connect(self._update_memory)
        self._job_worker.finished.connect(self._on_job_finished)
        self._job_worker.start()

    def _on_job_finished(self, ok: bool, message: str):
        self._log_panel.append_line(message, "success" if ok else "error")
        self._set_busy(False)
        self._set_status(
            "● Ready" if ok else "● Failed", theme.ACCENT_GRN if ok else theme.ACCENT_ERROR
        )
        if getattr(self, "_reconnect_after_job", None) is not None:
            baud = self._reconnect_after_job
            self._reconnect_after_job = None
            self._serial_panel.set_baud(baud)
            self._on_serial_connect(baud)

    def _on_boards_manager(self):
        dlg = BoardManagerDialog(parent=self)
        dlg.exec()
        self._on_refresh_ports()  # installed cores may change available boards

    def _selected_board(self) -> BoardOption | None:
        return self._board_combo.currentData()

    def _selected_port(self) -> str:
        return self._port_combo.currentData() or ""

    def _set_busy(self, busy: bool):
        self._compile_btn.setEnabled(not busy)
        self._upload_btn.setEnabled(not busy)
        self._refresh_btn.setEnabled(not busy)
        self._board_combo.setEnabled(not busy)
        self._port_combo.setEnabled(not busy)

    def _show_warning(self, text: str):
        self._log_panel.append_line(text, "warning")
        QMessageBox.warning(self, APP_NAME, text)
