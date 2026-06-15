"""
ui/board_manager.py — Boards Manager dialog (install/update/uninstall cores).
"""

from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from cli.arduino_cli import ArduinoCLI, ArduinoCLIError, CoreInfo
from ui.theme import (
    ACCENT_GRN,
    ACCENT_GRN_HI,
    BG_DARK,
    BG_PANEL,
    BG_RAISED,
    BORDER,
    BORDER_HI,
    FONT_MONO,
    TEXT_MAIN,
    TEXT_MID,
    make_btn,
)
from ui.workers import CoreJobWorker

_PLACEHOLDER = "—"


class BoardManagerDialog(QDialog):
    """Browse, install, update, and remove arduino-cli board cores."""

    def __init__(self, cli=None, parent=None):
        super().__init__(parent)
        self._cli = cli or ArduinoCLI()
        self._worker = None

        self.setWindowTitle("Boards Manager")
        self.resize(720, 520)
        self._build_ui()
        self._refresh()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet(f"QDialog {{ background: {BG_PANEL}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # ── Search row ───────────────────────────────────────────────────────
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("Search for a core (e.g. esp32:esp32)…")
        self._search_box.setFixedHeight(34)
        self._search_box.setStyleSheet(
            f"QLineEdit {{ background: {BG_RAISED}; color: {TEXT_MAIN}; font-family: {FONT_MONO};"
            f" border: 1px solid {BORDER}; border-radius: 6px; padding: 0 10px; font-size: 12px; }}"
            f"QLineEdit:focus {{ border-color: {BORDER_HI}; }}"
        )
        search_row.addWidget(self._search_box)

        self._search_btn = make_btn("Search", color=ACCENT_GRN, hover=ACCENT_GRN_HI)
        search_row.addWidget(self._search_btn)

        root.addLayout(search_row)

        # ── Table ────────────────────────────────────────────────────────────
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Core ID", "Name", "Installed", "Latest"])
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.setStyleSheet(
            f"QTableWidget {{ background: {BG_DARK}; color: {TEXT_MAIN}; font-family: {FONT_MONO};"
            f" border: 1px solid {BORDER}; border-radius: 6px; font-size: 12px;"
            f" gridline-color: {BORDER}; }}"
            f"QHeaderView::section {{ background: {BG_RAISED}; color: {TEXT_MID};"
            f" border: none; border-bottom: 1px solid {BORDER}; padding: 6px 8px;"
            f" font-size: 11px; font-weight: 700; }}"
            f"QTableWidget::item {{ padding: 4px 8px; }}"
            f"QTableWidget::item:selected {{ background: #1d3a2c; color: {TEXT_MAIN}; }}"
        )
        root.addWidget(self._table)

        # ── Action row ───────────────────────────────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self._install_btn = make_btn("Install", color=ACCENT_GRN, hover=ACCENT_GRN_HI)
        self._update_btn = make_btn("Update", secondary=True)
        self._uninstall_btn = make_btn("Uninstall", secondary=True)

        action_row.addWidget(self._install_btn)
        action_row.addWidget(self._update_btn)
        action_row.addWidget(self._uninstall_btn)
        action_row.addStretch()

        root.addLayout(action_row)

        # ── Log ──────────────────────────────────────────────────────────────
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setFixedHeight(140)
        font = self._log.font()
        font.setFamily("JetBrains Mono")
        self._log.setStyleSheet(
            f"QPlainTextEdit {{ background: {BG_DARK}; color: {TEXT_MAIN}; font-family: {FONT_MONO};"
            f" border: 1px solid {BORDER}; border-radius: 6px; padding: 8px; font-size: 11px; }}"
        )
        root.addWidget(self._log)

        # ── Wiring ───────────────────────────────────────────────────────────
        self._search_btn.clicked.connect(self._on_search)
        self._search_box.returnPressed.connect(self._on_search)
        self._install_btn.clicked.connect(self._install)
        self._update_btn.clicked.connect(self._update)
        self._uninstall_btn.clicked.connect(self._uninstall)

    # ── Table population ────────────────────────────────────────────────────

    def _populate(self, cores: list[CoreInfo]) -> None:
        self._table.setRowCount(len(cores))
        for row, core in enumerate(cores):
            self._table.setItem(row, 0, QTableWidgetItem(core.id))
            self._table.setItem(row, 1, QTableWidgetItem(core.name))
            self._table.setItem(row, 2, QTableWidgetItem(core.installed or _PLACEHOLDER))
            self._table.setItem(row, 3, QTableWidgetItem(core.latest or _PLACEHOLDER))

    # ── Data loading ─────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        try:
            cores = self._cli.core_list()
        except ArduinoCLIError as exc:
            self._log.appendPlainText(str(exc))
            self._table.setRowCount(0)
            return
        self._populate(cores)

    def _on_search(self) -> None:
        query = self._search_box.text().strip()
        if not query:
            self._refresh()
            return
        try:
            cores = self._cli.core_search(query)
        except ArduinoCLIError as exc:
            self._log.appendPlainText(str(exc))
            self._table.setRowCount(0)
            return
        self._populate(cores)

    # ── Selection ────────────────────────────────────────────────────────────

    def _selected_core_id(self) -> str | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        return item.text() if item else None

    # ── Core jobs ────────────────────────────────────────────────────────────

    def _install(self) -> None:
        self._start_core_job("install")

    def _update(self) -> None:
        self._start_core_job("upgrade")

    def _uninstall(self) -> None:
        self._start_core_job("uninstall")

    def _start_core_job(self, action: str) -> None:
        core_id = self._selected_core_id()
        if not core_id:
            self._log.appendPlainText("Select a core first.")
            return

        self._set_buttons_enabled(False)

        self._worker = CoreJobWorker(action, core_id, self)
        self._worker.line.connect(self._on_worker_line)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _on_worker_line(self, text: str, _level: str) -> None:
        self._log.appendPlainText(text)

    def _on_worker_finished(self, _ok: bool, message: str) -> None:
        self._set_buttons_enabled(True)
        self._log.appendPlainText(message)
        self._refresh()

    def _set_buttons_enabled(self, enabled: bool) -> None:
        self._install_btn.setEnabled(enabled)
        self._update_btn.setEnabled(enabled)
        self._uninstall_btn.setEnabled(enabled)
        self._search_btn.setEnabled(enabled)
