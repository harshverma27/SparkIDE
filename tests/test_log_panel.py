"""Tests for the build/upload log panel (ui/log_panel.py)."""

from ui.log_panel import LogPanel


def test_append_line_adds_timestamped_message(qapp):
    panel = LogPanel()

    panel.append_line("Compiled sketch", level="success")

    text = panel._editor.toPlainText()
    assert "SparkIDE v1.0" in text
    assert "Compiled sketch" in text
    assert "[" in text and "]" in text


def test_clear_removes_all_output(qapp):
    panel = LogPanel()
    panel.append_line("Something happened", level="info")

    panel.clear()

    assert panel._editor.toPlainText() == ""
