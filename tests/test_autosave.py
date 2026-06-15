from pathlib import Path

from project.autosave import files_to_autosave


def test_returns_only_dirty_buffers():
    a, b, c = Path("a.h"), Path("b.h"), Path("c.h")
    buffers = {a: "changed", b: "same", c: "also changed"}
    on_disk = {a: "original", b: "same", c: "original"}
    assert files_to_autosave(buffers, on_disk) == {a: "changed", c: "also changed"}


def test_new_file_not_on_disk_is_dirty():
    a = Path("new.h")
    assert files_to_autosave({a: "hello"}, {}) == {a: "hello"}


def test_no_dirty_returns_empty():
    a = Path("a.h")
    assert files_to_autosave({a: "x"}, {a: "x"}) == {}
