"""
ui/code_panel.py — Read-only C++ code preview panel.

What to do here:
  1. Subclass QWidget.
  2. Internally use a QPlainTextEdit set to read-only.
  3. Apply a monospace font (e.g. "Fira Code", "Monospace", or "Courier New").
  4. Implement a CppHighlighter(QSyntaxHighlighter) class that colours:
       - Keywords:   void, int, bool, if, else, return, true, false ...  (bold blue)
       - Strings:    "..." content                                         (green)
       - Comments:   // single-line and /* block */                        (grey italic)
       - Numbers:    integer and float literals                            (orange)
       - Functions:  word followed by '('                                  (light purple)
  5. Expose a public slot:
       def update_code(self, cpp_str: str) -> None:
           # Replaces the entire content of the editor with cpp_str.
           # Cursor is kept at top so the user always sees the beginning.
  6. Optional: add a small copy-to-clipboard button in the top-right corner.
"""

# TODO: from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
# TODO: from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor
# TODO: from PyQt6.QtCore import QRegularExpression, pyqtSlot


class CppHighlighter:
    # TODO: subclass QSyntaxHighlighter
    # TODO: define highlighting rules in __init__
    # TODO: implement highlightBlock(self, text: str)
    pass


class CodePanel:
    # TODO: subclass QWidget
    # TODO: set up layout with QPlainTextEdit + CppHighlighter
    # TODO: implement update_code(self, cpp_str: str) slot
    pass
