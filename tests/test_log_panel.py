import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication

from ui.log_panel import LogPanel


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_append_line_adds_timestamped_message(app):
    panel = LogPanel()

    panel.append_line("Compiled sketch", level="success")

    text = panel._editor.toPlainText()
    assert "SparkIDE v1.0" in text
    assert "Compiled sketch" in text
    assert "[" in text and "]" in text


def test_clear_removes_all_output(app):
    panel = LogPanel()
    panel.append_line("Something happened", level="info")

    panel.clear()

    assert panel._editor.toPlainText() == ""
