"""
ui/editor/editor_tabs.py — tabbed multi-file editor host.

Tab 0 is the read-only block-generated "Generated" view (same update_code /
current_code surface the old CodePanel exposed, so bridge wiring is unchanged).
Further tabs are editable companion files backed by CodeEditor. Project lifecycle
and disk I/O policy live in MainWindow; this widget only edits files it is told to
open.
"""

from pathlib import Path

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ui import theme
from ui.editor.code_editor import CodeEditor

SAMPLE_CODE = """\
// Generated C++ will appear here as you place blocks.

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
  delay(1000);
}
"""


class EditorTabs(QWidget):
    """Tabbed editor: read-only Generated view + editable companion files."""

    dirty_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editors: dict[Path, CodeEditor] = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.tabCloseRequested.connect(self._on_tab_close_requested)

        # ── Generated tab (header chrome + read-only editor) ──
        gen = QWidget()
        gl = QVBoxLayout(gen)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(36)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(12, 0, 10, 0)
        self._live_dot = QLabel("Live sync")
        self._live_dot.setStyleSheet(
            f"color: {getattr(theme, 'ACCENT_GRN', '#4ade80')};"
            f" font-family: {theme.FONT_MONO}; font-size: 10px; font-weight: 600;"
        )
        hl.addWidget(self._live_dot)
        hl.addStretch()
        self._line_count = QLabel("0 lines")
        self._line_count.setStyleSheet(
            f"color: {getattr(theme, 'TEXT_DIM', '#5c7468')};"
            f" font-family: {theme.FONT_MONO}; font-size: 10px; margin-right: 8px;"
        )
        hl.addWidget(self._line_count)
        copy_btn = QPushButton("Copy")
        copy_btn.setFixedSize(60, 24)
        copy_btn.clicked.connect(self._copy_generated)
        hl.addWidget(copy_btn)
        gl.addWidget(header)

        self._generated = CodeEditor()
        self._generated.set_read_only(True)
        self._generated.setText(SAMPLE_CODE)
        self._generated.textChanged.connect(self._update_line_count)
        gl.addWidget(self._generated)

        self._tabs.addTab(gen, "Generated")
        # The Generated tab cannot be closed.
        self._tabs.tabBar().setTabButton(0, self._tabs.tabBar().ButtonPosition.RightSide, None)

        root.addWidget(self._tabs)
        self._update_line_count()

    # ── Generated view surface (matches the old CodePanel) ──────────────────────

    @pyqtSlot(str)
    def update_code(self, cpp_str: str) -> None:
        self._generated.setText(cpp_str)

    def current_code(self) -> str:
        return self._generated.text()

    # ── Companion files ─────────────────────────────────────────────────────────

    def open_file(self, path: Path) -> None:
        path = Path(path)
        if path in self._editors:
            self._tabs.setCurrentWidget(self._editors[path])
            return
        ed = CodeEditor()
        ed.setText(path.read_text(encoding="utf-8"))
        ed.setModified(False)
        ed.modificationChanged.connect(lambda _=None: self._on_modified(path))
        self._editors[path] = ed
        self._tabs.addTab(ed, path.name)
        self._tabs.setCurrentWidget(ed)
        self._refresh_tab_label(path)

    def new_file(self, path: Path) -> None:
        path = Path(path)
        path.write_text("", encoding="utf-8")
        self.open_file(path)

    def close_file(self, path: Path) -> None:
        ed = self._editors.pop(Path(path), None)
        if ed is not None:
            self._tabs.removeTab(self._tabs.indexOf(ed))
            ed.deleteLater()
        self.dirty_changed.emit(self.has_dirty())

    def editor_for(self, path: Path) -> CodeEditor:
        return self._editors[Path(path)]

    def open_paths(self) -> list[Path]:
        return list(self._editors.keys())

    def count(self) -> int:
        return self._tabs.count()

    def dirty_buffers(self) -> dict[Path, str]:
        return {p: ed.text() for p, ed in self._editors.items() if ed.is_modified()}

    def has_dirty(self) -> bool:
        return any(ed.is_modified() for ed in self._editors.values())

    def mark_saved(self, path: Path) -> None:
        ed = self._editors.get(Path(path))
        if ed is not None:
            ed.setModified(False)
            self._refresh_tab_label(Path(path))
        self.dirty_changed.emit(self.has_dirty())

    # ── Internal ──────────────────────────────────────────────────────────────

    def _on_modified(self, path: Path):
        self._refresh_tab_label(path)
        self.dirty_changed.emit(self.has_dirty())

    def _refresh_tab_label(self, path: Path):
        ed = self._editors.get(path)
        if ed is None:
            return
        idx = self._tabs.indexOf(ed)
        marker = "● " if ed.is_modified() else ""
        self._tabs.setTabText(idx, f"{marker}{path.name}")

    def _on_tab_close_requested(self, index: int):
        widget = self._tabs.widget(index)
        for path, ed in self._editors.items():
            if ed is widget:
                self.close_file(path)
                return

    def _update_line_count(self):
        n = len(self._generated.text().splitlines())
        self._line_count.setText(f"{n} line{'s' if n != 1 else ''}")

    def _copy_generated(self):
        QApplication.clipboard().setText(self._generated.text())
