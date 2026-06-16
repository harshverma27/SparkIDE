import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.Qsci import QsciLexerCPP
from PyQt6.QtWidgets import QApplication

from ui.editor.code_editor import CodeEditor, _monospace_font


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_set_and_get_text(app):
    ed = CodeEditor()
    ed.setText("int x = 1;")
    assert ed.text() == "int x = 1;"


def test_read_only_toggle(app):
    ed = CodeEditor()
    ed.set_read_only(True)
    assert ed.isReadOnly() is True
    ed.set_read_only(False)
    assert ed.isReadOnly() is False


def test_modified_flag(app):
    ed = CodeEditor()
    ed.setText("seed")
    ed.setModified(False)
    assert ed.is_modified() is False
    ed.append_text(" more")
    assert ed.is_modified() is True


def test_resolved_font_is_fixed_pitch(app):
    # A proportional substitute makes QScintilla overlap glyphs, so the resolved
    # face must be genuinely monospace even when no preferred family is installed.
    assert _monospace_font(11).fixedPitch() is True


def test_all_token_styles_are_visible_on_dark_paper(app):
    # Regression: identifiers/operators (pinMode, "(", ",") used to keep the
    # lexer's default black colour and vanished against the dark panel.
    ed = CodeEditor()
    lex = ed._lexer
    paper = lex.paper(QsciLexerCPP.Default).name()
    for style in (
        QsciLexerCPP.Default,
        QsciLexerCPP.Identifier,
        QsciLexerCPP.Operator,
        QsciLexerCPP.Keyword,
        QsciLexerCPP.Number,
    ):
        assert lex.color(style).name() != "#000000"
        assert lex.color(style).name() != paper
