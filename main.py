"""
main.py — SparkIDE application entry point.
"""

import os
import sys

# Use the xcb platform plugin on Linux (most common Wayland / X11 setup)
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication

from app_config import APP_NAME, APP_ORG, APP_VERSION
from ui.main_window import MainWindow


def _apply_dark_theme(app: QApplication) -> None:
    """Apply a dark Fusion palette to the whole application."""
    app.setStyle("Fusion")

    palette = QPalette()

    # Window chrome
    palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#d4d4d4"))

    # Widgets
    palette.setColor(QPalette.ColorRole.Base, QColor("#252526"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2d2d30"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#6a6a6a"))

    # Buttons
    palette.setColor(QPalette.ColorRole.Button, QColor("#2a2a2a"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#d4d4d4"))

    # Highlights / selections
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#264f78"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))

    # Tooltips
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2a2a2a"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#d4d4d4"))

    # Borders / lines
    palette.setColor(QPalette.ColorRole.Mid, QColor("#3a3a3a"))
    palette.setColor(QPalette.ColorRole.Dark, QColor("#141414"))
    palette.setColor(QPalette.ColorRole.Shadow, QColor("#0a0a0a"))

    app.setPalette(palette)

    # Global font
    app.setFont(QFont("Inter", 11))


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG)

    _apply_dark_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
