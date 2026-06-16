"""Smoke test for the assembled main window (ui/main_window.py).

QtWebEngine cannot initialise headlessly, so we stub QWebEngineView with a
lightweight QWidget. This still exercises the real window composition — menu,
toolbar (ToolbarMixin), central frame, log dock, and status bar (StatusBarMixin)
— catching wiring regressions from the module split.
"""

from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QWidget

# Imported before any QApplication exists (QtWebEngine requires this ordering).
from ui import main_window
from ui.main_window import MainWindow


class _FakeWebView(QWidget):
    """Stand-in for QWebEngineView: a real QWidget with stubbed web methods."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._page = MagicMock()

    def settings(self):
        return MagicMock()

    def page(self):
        return self._page

    def setUrl(self, *args, **kwargs):
        pass


def test_main_window_builds(qapp):
    # Avoid spinning a real board-refresh thread / arduino-cli subprocess.
    with (
        patch.object(main_window, "QWebEngineView", _FakeWebView),
        patch.object(main_window, "BoardRefreshWorker"),
    ):
        window = MainWindow()

    # Window shell + mixin-built widgets are all present and wired.
    assert window.windowTitle() == "SparkIDE"
    assert window._board_combo is not None  # ToolbarMixin
    assert window._port_combo is not None  # ToolbarMixin
    assert window._compile_btn is not None  # ToolbarMixin
    assert window._sb_status is not None  # StatusBarMixin
    assert window._editor is not None
    assert window._log_panel is not None
    # Block-count telemetry updates through the mixin helper.
    window._update_block_count(5)
    assert "5" in window._sb_blocks.text()


def test_open_project_populates_tabs_and_state(qapp, tmp_path):
    from project.model import create_project

    proj = create_project(tmp_path, "demo")
    (proj.root / "helpers.h").write_text("#define X 1")

    window = _build_window()
    window._load_project(proj)

    assert window._project is not None
    assert window._project.root == proj.root
    # Generated tab + helpers.h companion are both open.
    assert proj.root / "helpers.h" in window._editor.open_paths()


def _build_window():
    with (
        patch.object(main_window, "QWebEngineView", _FakeWebView),
        patch.object(main_window, "BoardRefreshWorker"),
    ):
        return MainWindow()


def test_serial_panel_and_dock_present(qapp):
    window = _build_window()
    assert hasattr(window, "_serial_panel")
    assert hasattr(window, "_serial_dock")
    assert window._serial_panel is not None


def test_tools_menu_present(qapp):
    window = _build_window()
    titles = [a.text() for a in window.menuBar().actions()]
    assert any("Tools" in t for t in titles)


def test_update_memory_handles_none_and_stats(qapp):
    from cli.arduino_cli import CompileStats

    window = _build_window()
    window._update_memory(None)
    window._update_memory(CompileStats(2408, 32256, 184, 2048))
