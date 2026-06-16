"""
ui/editor/code_editor.py — QScintilla C++ editor themed to the Hybrid Lab Console.

Used both as the read-only "Generated" view and as the editable companion-file
editor. Theming lives entirely in _apply_theme so the palette is retuned in one
place.
"""

from PyQt6.Qsci import QsciLexerCPP, QsciScintilla
from PyQt6.QtGui import QColor, QFont, QFontMetrics

from ui import theme


class CodeEditor(QsciScintilla):
    """A themed C++ code editor (line numbers, folding, brace match)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont("Fira Code", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        if not font.exactMatch():
            font = QFont("JetBrains Mono", 11)
            font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        lexer = QsciLexerCPP(self)
        lexer.setFont(font)
        self._lexer = lexer
        self.setLexer(lexer)

        self.setUtf8(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(2)
        self.setAutoIndent(True)
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, QFontMetrics(font).horizontalAdvance("0000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setCaretLineVisible(True)
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsDocument)
        self.setAutoCompletionThreshold(3)

        self._apply_theme()

    def _apply_theme(self):
        bg = QColor(theme.BG_PANEL)
        fg = QColor(getattr(theme, "TEXT_MAIN", "#e4f0e8"))
        margin_bg = QColor(theme.BG_DARK)
        accent = QColor(getattr(theme, "ACCENT_GRN", "#4ade80"))

        self.setColor(fg)
        self.setPaper(bg)
        self.setCaretForegroundColor(accent)
        self.setCaretLineBackgroundColor(QColor(theme.BG_DARK))
        self.setMarginsBackgroundColor(margin_bg)
        self.setMarginsForegroundColor(QColor(getattr(theme, "TEXT_DIM", "#5c7468")))
        self.setSelectionBackgroundColor(QColor("#1d3a2c"))
        self.setFoldMarginColors(margin_bg, margin_bg)

        lex = self._lexer
        lex.setDefaultPaper(bg)
        lex.setDefaultColor(fg)
        lex.setPaper(bg)  # all styles share the panel background
        lex.setColor(fg, QsciLexerCPP.Default)
        lex.setColor(QColor("#8aa6c4"), QsciLexerCPP.Keyword)
        lex.setColor(QColor("#7ee2a8"), QsciLexerCPP.GlobalClass)
        lex.setColor(QColor("#6fcfc0"), QsciLexerCPP.DoubleQuotedString)
        lex.setColor(QColor("#6fcfc0"), QsciLexerCPP.SingleQuotedString)
        lex.setColor(QColor("#d9b36a"), QsciLexerCPP.Number)
        lex.setColor(QColor(getattr(theme, "ACCENT_AMBER", "#f0a93e")), QsciLexerCPP.PreProcessor)
        lex.setColor(QColor("#5c7468"), QsciLexerCPP.Comment)
        lex.setColor(QColor("#5c7468"), QsciLexerCPP.CommentLine)

    # ── Public helpers ─────────────────────────────────────────────────────────

    def set_read_only(self, read_only: bool) -> None:
        self.setReadOnly(read_only)

    def is_modified(self) -> bool:
        return self.isModified()

    def append_text(self, text: str) -> None:
        self.append(text)
