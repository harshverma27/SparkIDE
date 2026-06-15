"""Tests for the build/upload log panel (ui/log_panel.py)."""

from app_config import version_label
from ui.log_panel import LogPanel


def test_append_line_adds_timestamped_message(qapp):
    panel = LogPanel()

    panel.append_line("Compiled sketch", level="success")

    text = panel._editor.toPlainText()
    assert version_label() in text
    assert "Compiled sketch" in text
    assert "[" in text and "]" in text


def test_clear_removes_all_output(qapp):
    panel = LogPanel()
    panel.append_line("Something happened", level="info")

    panel.clear()

    assert panel._editor.toPlainText() == ""
