"""
project/model.py — Qt-free model of a SparkIDE project (an Arduino sketch folder).

A project is a sketch folder named after its main sketch:
    blinky/
      blinky.ino          ← block-generated main sketch (authoritative)
      blinky.blocks.json  ← saved Blockly workspace
      helpers.h, ...      ← optional hand-edited companion files
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_VALID_NAME = re.compile(r"^[A-Za-z0-9_]+$")
_SOURCE_SUFFIXES = {".ino", ".h", ".cpp"}

_STARTER_INO = """\
void setup() {
  // put your setup code here, to run once:
}

void loop() {
  // put your main code here, to run repeatedly:
}
"""


@dataclass(frozen=True)
class ProjectFile:
    path: Path
    kind: str  # "main_ino" | "ino" | "header" | "source"
    is_generated: bool


@dataclass(frozen=True)
class Project:
    root: Path
    name: str

    @property
    def main_ino(self) -> Path:
        return self.root / f"{self.name}.ino"

    @property
    def workspace_path(self) -> Path:
        return self.root / f"{self.name}.blocks.json"

    def files(self) -> list[ProjectFile]:
        out: list[ProjectFile] = []
        for p in sorted(self.root.iterdir()):
            if not p.is_file() or p.suffix not in _SOURCE_SUFFIXES:
                continue
            if p == self.main_ino:
                out.append(ProjectFile(p, "main_ino", True))
            elif p.suffix == ".ino":
                out.append(ProjectFile(p, "ino", False))
            elif p.suffix == ".h":
                out.append(ProjectFile(p, "header", False))
            else:
                out.append(ProjectFile(p, "source", False))
        return out

    def companion_files(self) -> list[ProjectFile]:
        return [f for f in self.files() if not f.is_generated]


def is_sketch_folder(path: Path) -> bool:
    path = Path(path)
    if not path.is_dir():
        return False
    return (path / f"{path.name}.ino").exists()


def create_project(parent_dir: Path, name: str) -> Project:
    if not _VALID_NAME.match(name):
        raise ValueError(f"Invalid project name: {name!r} (letters, digits, underscore only)")
    root = Path(parent_dir) / name
    if root.exists():
        raise FileExistsError(f"Project folder already exists: {root}")
    root.mkdir(parents=True)
    proj = Project(root=root, name=name)
    proj.main_ino.write_text(_STARTER_INO, encoding="utf-8")
    proj.workspace_path.write_text("", encoding="utf-8")
    return proj


def open_project(path: Path) -> Project:
    path = Path(path)
    folder = path if path.is_dir() else path.parent
    if not is_sketch_folder(folder):
        raise ValueError(f"Not a SparkIDE/Arduino sketch folder: {folder}")
    return Project(root=folder, name=folder.name)
