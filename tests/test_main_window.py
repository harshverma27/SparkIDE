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
    assert window._code_panel is not None
    assert window._log_panel is not None
    # Block-count telemetry updates through the mixin helper.
    window._update_block_count(5)
    assert "5" in window._sb_blocks.text()
