"""Shared pytest fixtures for SparkIDE.

UI tests construct Qt widgets, which require a single QApplication for the whole
process. We force the offscreen platform so these run headlessly (including in
CI under xvfb / without a display).
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    """A process-wide QApplication, reused across all UI tests."""
    from PyQt6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])
