import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication

from ui.editor.editor_tabs import EditorTabs


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_generated_tab_update_and_current(app):
    tabs = EditorTabs()
    tabs.update_code("void loop() {}")
    assert tabs.current_code() == "void loop() {}"


def test_open_file_creates_editable_tab(app, tmp_path):
    f = tmp_path / "helpers.h"
    f.write_text("#define PI 3")
    tabs = EditorTabs()
    tabs.open_file(f)
    assert f in tabs.open_paths()
    assert tabs.count() == 2  # Generated + helpers.h


def test_open_file_is_idempotent(app, tmp_path):
    f = tmp_path / "a.cpp"
    f.write_text("// a")
    tabs = EditorTabs()
    tabs.open_file(f)
    tabs.open_file(f)
    assert tabs.count() == 2


def test_dirty_buffers_reflect_edits(app, tmp_path):
    f = tmp_path / "a.cpp"
    f.write_text("// a")
    tabs = EditorTabs()
    tabs.open_file(f)
    tabs.editor_for(f).setText("// changed")
    assert tabs.dirty_buffers() == {f: "// changed"}


def test_close_file_removes_tab(app, tmp_path):
    f = tmp_path / "a.cpp"
    f.write_text("// a")
    tabs = EditorTabs()
    tabs.open_file(f)
    tabs.close_file(f)
    assert f not in tabs.open_paths()
    assert tabs.count() == 1
