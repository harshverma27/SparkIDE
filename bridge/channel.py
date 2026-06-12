"""
bridge/channel.py — QWebChannel Python-side bridge between PyQt6 and Blockly (JavaScript).
"""

import json

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class Bridge(QObject):
    """
    Registered with QWebChannel under the name 'bridge'.
    JavaScript calls:  bridge.on_code_update(cppString)
    Python emits:      code_changed(cppString)  → CodePanel.update_code()
    """

    # Emitted whenever Blockly generates new C++ code; connected to CodePanel
    code_changed = pyqtSignal(str)

    # Emitted whenever the workspace block count changes; connected to the telemetry strip
    block_count_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._page = None  # set by MainWindow via set_page() after page is ready

    # ── Python → JS ──────────────────────────────────────────────────────────

    def set_page(self, page) -> None:
        """Store a reference to QWebEnginePage so we can call runJavaScript."""
        self._page = page

    def load_workspace(self, json_str: str) -> None:
        """
        Push a saved workspace JSON to the Blockly editor.
        Called by MainWindow when the user opens a .json file.
        """
        if self._page:
            # Double-encode so the string is safe to pass as a JS argument
            safe = json.dumps(json_str)
            self._page.runJavaScript(f"window.loadWorkspace({safe});")

    def get_workspace_json(self, callback) -> None:
        """
        Asynchronously retrieve the current workspace as a JSON string.
        `callback(result)` is called by Qt with the JS return value.
        Called by MainWindow during Save.
        """
        if self._page:
            self._page.runJavaScript("window.getWorkspaceJson();", callback)

    # ── JS → Python ───────────────────────────────────────────────────────────

    @pyqtSlot(str)
    def on_code_update(self, cpp_code: str) -> None:
        """
        Called from JavaScript every time the Blockly workspace changes.
        Emits code_changed so the CodePanel updates in real time.
        """
        self.code_changed.emit(cpp_code)

    @pyqtSlot(int)
    def on_block_count_update(self, count: int) -> None:
        """
        Called from JavaScript every time the Blockly workspace changes.
        Emits block_count_changed so the telemetry strip updates.
        """
        self.block_count_changed.emit(count)
