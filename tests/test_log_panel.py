"""
tests/test_log_panel.py — Unit tests for ui/log_panel.py

What to test here:
  1. test_append_line_info
       - Create a LogPanel instance.
       - Call append_line("Hello", level="info").
       - Assert the text appears in the widget's plain text.

  2. test_append_line_error
       - Call append_line("Something broke", level="error").
       - Assert the text appears.
       - Assert the line's colour format is red (check QTextCharFormat).

  3. test_clear
       - Append a few lines, then call clear().
       - Assert the widget's text is empty afterward.

Notes:
  - PyQt6 widget tests require a QApplication instance to be running.
  - Use a module-level fixture:
      @pytest.fixture(scope="module")
      def app():
          return QApplication([])
"""

# TODO: import pytest
# TODO: from PyQt6.QtWidgets import QApplication
# TODO: from ui.log_panel import LogPanel


class TestLogPanel:
    # TODO: implement test methods listed above
    pass
