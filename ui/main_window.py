"""
ui/main_window.py — PyQt6 Main Application Window.

What to do here:
  1. Subclass QMainWindow.
  2. Build a central widget with a QSplitter (horizontal):
       - LEFT:  QWebEngineView (loads blockly/index.html) — the Blockly editor.
       - RIGHT: CodePanel (from code_panel.py) — live C++ preview.
  3. Set up the TOOLBAR with:
       - Board selector QComboBox  (populated by ArduinoCLI.list_boards())
       - Port selector QComboBox   (populated by ArduinoCLI.list_boards())
       - "Refresh Ports" QPushButton
       - "Compile" QPushButton  → triggers cli/arduino_cli.py compile()
       - "Upload"  QPushButton  → triggers cli/arduino_cli.py upload()
  4. Set up the STATUS BAR:
       - Permanent label showing: board · port · status (idle / compiling / uploading)
  5. Dock a LogPanel (from log_panel.py) at the bottom.
  6. Initialise QWebChannel and register the Bridge object (from bridge/channel.py).
     Inject the channel into the QWebEngineView so JS can talk to Python.
  7. Connect Bridge.code_changed signal → CodePanel.update_code slot.
  8. Set up File menu: Save (Ctrl+S) and Open (Ctrl+O) for workspace JSON.
  9. On close / resize, save window geometry to QSettings for persistence.
"""

# TODO: from PyQt6.QtWidgets import (
#     QMainWindow, QSplitter, QToolBar, QComboBox, QPushButton,
#     QStatusBar, QDockWidget, QWidget, QFileDialog
# )
# TODO: from PyQt6.QtWebEngineWidgets import QWebEngineView
# TODO: from PyQt6.QtWebChannel import QWebChannel
# TODO: from PyQt6.QtCore import Qt, QUrl
# TODO: from ui.code_panel import CodePanel
# TODO: from ui.log_panel import LogPanel
# TODO: from bridge.channel import Bridge
# TODO: from cli.arduino_cli import ArduinoCLI


class MainWindow:
    # TODO: implement __init__, _build_toolbar, _build_blockly_view,
    #       _build_splitter, _setup_channel, _on_compile, _on_upload,
    #       _on_save, _on_open, _refresh_ports
    pass
