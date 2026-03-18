"""
ui/code_panel.py — Read-only C++ code preview panel with syntax highlighting.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QLabel
from PyQt6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat
from PyQt6.QtCore import Qt, QRegularExpression, pyqtSlot


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


class CppHighlighter(QSyntaxHighlighter):
    """Minimal C++ syntax highlighter for the code preview panel."""

    def __init__(self, document):
        super().__init__(document)
        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []
        self._setup_rules()

    def _fmt(self, colour: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(colour))
        if bold:
            fmt.setFontWeight(700)
        if italic:
            fmt.setFontItalic(True)
        return fmt

    def _setup_rules(self):
        # ── Keywords ─────────────────────────────────────────────────────────
        keywords = (
            "void", "int", "bool", "float", "double", "char", "long",
            "unsigned", "byte", "String", "return", "if", "else", "while",
            "for", "do", "switch", "case", "break", "continue",
            "true", "false", "HIGH", "LOW", "INPUT", "OUTPUT", "INPUT_PULLUP",
        )
        kw_fmt = self._fmt("#c678dd", bold=True)  # purple
        kw_pattern = r"\b(" + "|".join(keywords) + r")\b"
        self._rules.append((QRegularExpression(kw_pattern), kw_fmt))

        # ── Arduino built-in functions ────────────────────────────────────────
        builtins = (
            "pinMode", "digitalWrite", "digitalRead", "analogRead",
            "analogWrite", "delay", "millis", "micros",
            "Serial", "setup", "loop",
        )
        bi_fmt = self._fmt("#61afef")  # light blue
        bi_pattern = r"\b(" + "|".join(builtins) + r")\b"
        self._rules.append((QRegularExpression(bi_pattern), bi_fmt))

        # ── Numbers ───────────────────────────────────────────────────────────
        self._rules.append((QRegularExpression(r"\b\d+(\.\d+)?\b"), self._fmt("#d19a66")))

        # ── Strings ───────────────────────────────────────────────────────────
        self._rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self._fmt("#98c379")))

        # ── Single-line comments ──────────────────────────────────────────────
        self._rules.append((QRegularExpression(r"//[^\n]*"), self._fmt("#5c6370", italic=True)))

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)


class CodePanel(QWidget):
    """Read-only C++ preview panel, updated by the Blockly bridge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.update_code(SAMPLE_CODE)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header bar
        header = QWidget()
        header.setFixedHeight(28)
        header.setStyleSheet("background:#1e1e1e; border-bottom: 1px solid #3a3a3a;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 8, 0)

        title = QLabel("Generated C++")
        title.setStyleSheet("color:#888; font-size:11px; font-weight:600; letter-spacing:1px;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        copy_btn = QPushButton("Copy")
        copy_btn.setFixedSize(52, 20)
        copy_btn.setStyleSheet(
            "QPushButton { background:#2a2a2a; color:#888; border:1px solid #3a3a3a;"
            " border-radius:3px; font-size:10px; }"
            "QPushButton:hover { background:#333; color:#ccc; }"
        )
        copy_btn.clicked.connect(self._copy_to_clipboard)
        h_layout.addWidget(copy_btn)

        root.addWidget(header)

        # Editor
        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        font = QFont("Fira Code", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._editor.setFont(font)
        self._editor.setStyleSheet(
            "QPlainTextEdit {"
            "  background: #1e1e1e;"
            "  color: #abb2bf;"
            "  border: none;"
            "  padding: 8px 12px;"
            "  selection-background-color: #3e4451;"
            "}"
        )
        self._highlighter = CppHighlighter(self._editor.document())
        root.addWidget(self._editor)

    # ── Public slot ───────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def update_code(self, cpp_str: str) -> None:
        """Replace panel content with new generated C++ code."""
        self._editor.setPlainText(cpp_str)
        # Keep cursor at top so user sees the beginning
        cursor = self._editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self._editor.setTextCursor(cursor)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _copy_to_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._editor.toPlainText())
