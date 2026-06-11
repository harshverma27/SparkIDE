"""
ui/code_panel.py — Read-only C++ code preview panel with syntax highlighting.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QLabel, QApplication,
)
from PyQt6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QPainter
from PyQt6.QtCore import Qt, QRegularExpression, pyqtSlot, QRect


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

BG_EDITOR = "#0f1728"
BG_GUTTER = "#0c1322"
BG_HEADER = "#101a2c"
COL_BORDER = "#263246"


class CppHighlighter(QSyntaxHighlighter):
    """Minimal C++ / Arduino syntax highlighter (One Dark palette)."""

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
        keywords = (
            "void", "int", "bool", "float", "double", "char", "long",
            "unsigned", "byte", "String", "return", "if", "else", "while",
            "for", "do", "switch", "case", "break", "continue",
            "true", "false", "HIGH", "LOW", "INPUT", "OUTPUT", "INPUT_PULLUP",
        )
        kw_fmt = self._fmt("#c678dd", bold=True)
        self._rules.append((
            QRegularExpression(r"\b(" + "|".join(keywords) + r")\b"), kw_fmt
        ))

        builtins = (
            "pinMode", "digitalWrite", "digitalRead", "analogRead", "analogWrite",
            "delay", "delayMicroseconds", "millis", "micros", "map", "constrain",
            "abs", "sqrt", "pow", "random", "min", "max", "round",
            "Serial", "setup", "loop",
        )
        bi_fmt = self._fmt("#61afef")
        self._rules.append((
            QRegularExpression(r"\b(" + "|".join(builtins) + r")\b"), bi_fmt
        ))

        # Pre-processor
        self._rules.append((QRegularExpression(r"#\w+"), self._fmt("#e5c07b")))

        # Numbers
        self._rules.append((
            QRegularExpression(r"\b\d+(\.\d+)?\b"), self._fmt("#d19a66")
        ))

        # Strings
        self._rules.append((
            QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self._fmt("#98c379")
        ))

        # Single-line comments
        self._rules.append((
            QRegularExpression(r"//[^\n]*"), self._fmt("#5c6370", italic=True)
        ))

    def highlightBlock(self, text: str):
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)


class CodePanel(QWidget):
    """Read-only C++ preview panel, updated live by the Blockly bridge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.update_code(SAMPLE_CODE)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ──────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(44)
        header.setStyleSheet(
            f"background: {BG_HEADER};"
            f"border-bottom: 1px solid {COL_BORDER};"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(14, 0, 10, 0)

        title_chip = QLabel("Generated Sketch")
        title_chip.setStyleSheet(
            "background: #18253a; color: #eef3ff;"
            "font-size: 11px; font-weight: 700;"
            "border-radius: 9px;"
            "padding: 5px 10px; letter-spacing: 0.4px;"
        )
        hl.addWidget(title_chip)

        self._live_dot = QLabel("Live sync")
        self._live_dot.setStyleSheet(
            "color: #7bd8aa; font-size: 10px; margin-left: 8px; font-weight: 600;"
        )
        hl.addWidget(self._live_dot)
        hl.addStretch()

        self._line_count = QLabel("0 lines")
        self._line_count.setStyleSheet("color: #7e8aa5; font-size: 10px; margin-right: 10px;")
        hl.addWidget(self._line_count)

        # Copy button
        copy_btn = QPushButton("Copy")
        copy_btn.setFixedSize(64, 26)
        copy_btn.setStyleSheet(
            "QPushButton { background: #18253a; color: #b2bdd2; border: 1px solid #2a3b57;"
            " border-radius: 8px; font-size: 10px; font-weight: 600; }"
            "QPushButton:hover { background: #21304a; color: #eef3ff; }"
            "QPushButton:pressed { background: #142034; }"
        )
        copy_btn.clicked.connect(self._copy_to_clipboard)
        hl.addWidget(copy_btn)

        root.addWidget(header)

        # ── Editor ──────────────────────────────────────────────────────────
        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        mono = QFont("Fira Code", 11)
        mono.setStyleHint(QFont.StyleHint.Monospace)
        if not mono.exactMatch():
            mono = QFont("JetBrains Mono", 11)
            mono.setStyleHint(QFont.StyleHint.Monospace)
        self._editor.setFont(mono)
        self._editor.setStyleSheet(
            f"QPlainTextEdit {{"
            f"  background: {BG_EDITOR};"
            f"  color: #d5def0;"
            f"  border: none;"
            f"  padding: 14px 16px;"
            f"  selection-background-color: #29446f;"
            f"}}"
            f"QScrollBar:vertical {{"
            f"  background: {BG_EDITOR}; width: 10px; border: none;"
            f"}}"
            f"QScrollBar::handle:vertical {{"
            f"  background: #30415e; border-radius: 5px; min-height: 24px;"
            f"}}"
            f"QScrollBar::handle:vertical:hover {{ background: #45608f; }}"
            f"QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}"
        )
        self._highlighter = CppHighlighter(self._editor.document())
        self._editor.document().blockCountChanged.connect(self._update_line_count)
        root.addWidget(self._editor)

    # ── Public slot ───────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def update_code(self, cpp_str: str) -> None:
        """Replace panel content with new generated C++ code."""
        self._editor.setPlainText(cpp_str)
        cursor = self._editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self._editor.setTextCursor(cursor)
        self._update_line_count(self._editor.document().blockCount())

    def current_code(self) -> str:
        """Return the generated sketch currently shown in the preview."""
        return self._editor.toPlainText()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _update_line_count(self, count: int):
        self._line_count.setText(f"{count} line{'s' if count != 1 else ''}")

    def _copy_to_clipboard(self):
        QApplication.clipboard().setText(self._editor.toPlainText())
        # Flash copy button text briefly
        btn = self.sender()
        if btn:
            btn.setText("Copied")
            btn.setStyleSheet(
                "QPushButton { background: #173224; color: #7bd8aa; border: 1px solid #25573d;"
                " border-radius: 8px; font-size: 10px; font-weight: 600; }"
            )
            from PyQt6.QtCore import QTimer
            def _reset():
                btn.setText("Copy")
                btn.setStyleSheet(
                    "QPushButton { background: #18253a; color: #b2bdd2; border: 1px solid #2a3b57;"
                    " border-radius: 8px; font-size: 10px; font-weight: 600; }"
                    "QPushButton:hover { background: #21304a; color: #eef3ff; }"
                )
            QTimer.singleShot(1500, _reset)
