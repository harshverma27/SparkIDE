"""
bridge/channel.py — QWebChannel Python-side bridge between PyQt6 and Blockly (JavaScript).

What to do here:
  1. Subclass QObject (required for QWebChannel registration).
  2. Define a pyqtSignal:
       code_changed = pyqtSignal(str)
     This signal is emitted whenever Blockly generates new C++ code.
     MainWindow connects it to CodePanel.update_code().

  3. Define a pyqtSlot that JavaScript can call:
       @pyqtSlot(str)
       def on_code_update(self, cpp_code: str) -> None:
           # Called from JS via: bridge.on_code_update(generatedCppString)
           # Emit code_changed so CodePanel receives the new code.
           self.code_changed.emit(cpp_code)

  4. Define a method to push workspace JSON from Python → JS:
       def load_workspace(self, json_str: str) -> None:
           # Call a JS function to restore a saved workspace.
           # Use QWebEnginePage.runJavaScript() for this.
           # You'll need a reference to the QWebEnginePage stored on this object.

  5. Store a reference to the QWebEnginePage (set from MainWindow after page is ready).

How QWebChannel wiring works (summary):
  - MainWindow creates: channel = QWebChannel()
  - MainWindow calls:   channel.registerObject("bridge", bridge_instance)
  - MainWindow sets:    web_view.page().setWebChannel(channel)
  - index.html loads qwebchannel.js and does:
      new QWebChannel(qt.webChannelTransport, function(channel) {
          window.bridge = channel.objects.bridge;
          // Now JS can call: bridge.on_code_update(code)
      });
"""

# TODO: from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class Bridge:
    # TODO: subclass QObject
    # TODO: define code_changed = pyqtSignal(str)
    # TODO: implement __init__(self, parent=None) — store page reference
    # TODO: implement on_code_update(self, cpp_code: str) slot
    # TODO: implement load_workspace(self, json_str: str)
    pass
