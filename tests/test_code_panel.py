"""Tests for the C++ preview panel (ui/code_panel.py)."""

from ui.code_panel import CodePanel, CppHighlighter


def test_update_code_replaces_content_and_reports_it(qapp):
    panel = CodePanel()

    panel.update_code("void loop() {}\n")

    assert panel.current_code() == "void loop() {}\n"


def test_update_code_resets_cursor_to_start(qapp):
    panel = CodePanel()

    panel.update_code("line one\nline two\nline three\n")

    # Cursor parked at the top so the preview scrolls to the start of the sketch.
    assert panel._editor.textCursor().position() == 0


def test_line_count_label_updates(qapp):
    panel = CodePanel()

    panel.update_code("a\nb\nc")

    assert panel._line_count.text() == "3 lines"


def test_highlighter_builds_rules(qapp):
    panel = CodePanel()

    assert isinstance(panel._highlighter, CppHighlighter)
    # Keyword, builtin, preprocessor, number, string, comment families.
    assert len(panel._highlighter._rules) == 6
