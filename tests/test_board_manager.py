from cli.arduino_cli import CoreInfo


class StubCLI:
    def core_list(self):
        return [
            CoreInfo(id="arduino:avr", name="Arduino AVR Boards", installed="1.8.6", latest="1.8.6")
        ]

    def core_search(self, query):
        return [CoreInfo(id="esp32:esp32", name="ESP32", installed="", latest="2.0.0")]


def test_board_manager_lists_installed(qapp):
    from ui.board_manager import BoardManagerDialog

    dlg = BoardManagerDialog(cli=StubCLI())
    assert dlg._table.rowCount() == 1
    assert dlg._table.item(0, 0).text() == "arduino:avr"


def test_board_manager_search(qapp):
    from ui.board_manager import BoardManagerDialog

    dlg = BoardManagerDialog(cli=StubCLI())
    dlg._search_box.setText("esp32")
    dlg._search_btn.click()
    assert dlg._table.item(0, 0).text() == "esp32:esp32"


def test_board_manager_empty_search_refreshes(qapp):
    from ui.board_manager import BoardManagerDialog

    dlg = BoardManagerDialog(cli=StubCLI())
    dlg._search_box.setText("")
    dlg._search_btn.click()
    assert dlg._table.item(0, 0).text() == "arduino:avr"


def test_board_manager_handles_cli_error(qapp):
    from cli.arduino_cli import ArduinoCLIError
    from ui.board_manager import BoardManagerDialog

    class FailingCLI:
        def core_list(self):
            raise ArduinoCLIError("arduino-cli was not found in PATH.")

    dlg = BoardManagerDialog(cli=FailingCLI())  # must not raise
    assert dlg._table.rowCount() == 0
    assert "not found" in dlg._log.toPlainText()
