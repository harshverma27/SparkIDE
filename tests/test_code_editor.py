import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication

from ui.editor.code_editor import CodeEditor


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
