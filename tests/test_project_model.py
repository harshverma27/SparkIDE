import pytest

from project.model import (
    create_project,
    is_sketch_folder,
    open_project,
)


def test_create_project_makes_sketch_folder(tmp_path):
    proj = create_project(tmp_path, "blinky")
    assert proj.root == tmp_path / "blinky"
    assert proj.name == "blinky"
    assert proj.main_ino == tmp_path / "blinky" / "blinky.ino"
    assert proj.main_ino.exists()
    assert proj.workspace_path == tmp_path / "blinky" / "blinky.blocks.json"
    assert proj.workspace_path.exists()


def test_create_project_rejects_duplicate(tmp_path):
    create_project(tmp_path, "blinky")
    with pytest.raises(FileExistsError):
        create_project(tmp_path, "blinky")


def test_create_project_rejects_bad_name(tmp_path):
    with pytest.raises(ValueError):
        create_project(tmp_path, "bad name/slash")


def test_is_sketch_folder(tmp_path):
    proj = create_project(tmp_path, "demo")
    assert is_sketch_folder(proj.root) is True
    assert is_sketch_folder(tmp_path) is False


def test_open_project_from_folder_or_file(tmp_path):
    created = create_project(tmp_path, "demo")
    by_folder = open_project(created.root)
    by_file = open_project(created.main_ino)
    assert by_folder.root == created.root
    assert by_file.root == created.root


def test_open_project_rejects_non_sketch(tmp_path):
    with pytest.raises(ValueError):
        open_project(tmp_path)


def test_files_tags_generated_main_and_lists_companions(tmp_path):
    proj = create_project(tmp_path, "demo")
    (proj.root / "helpers.h").write_text("// h")
    (proj.root / "extra.cpp").write_text("// cpp")
    files = proj.files()
    main = [f for f in files if f.is_generated]
    assert len(main) == 1
    assert main[0].path == proj.main_ino
    assert main[0].kind == "main_ino"
    companions = {f.path.name for f in proj.companion_files()}
    assert companions == {"helpers.h", "extra.cpp"}
