"""
main.py — SparkIDE application entry point.

What to do here:
  1. Import QApplication from PyQt6.QtWidgets.
  2. Import MainWindow from ui.main_window.
  3. Create a QApplication instance (pass sys.argv).
  4. Instantiate MainWindow and call .show() on it.
  5. Call sys.exit(app.exec()) to start the Qt event loop.

Notes:
  - On some Linux systems you may need to set the Qt platform plugin:
      os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
  - HiDPI: add QApplication.setHighDpiScaleFactorRoundingPolicy(...)
    before creating the app for crisp rendering on HiDPI displays.
"""

import sys

# TODO: from PyQt6.QtWidgets import QApplication
# TODO: from ui.main_window import MainWindow

def main():
    # TODO: Create QApplication, show MainWindow, start event loop
    pass

if __name__ == "__main__":
    main()
