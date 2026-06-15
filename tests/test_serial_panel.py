"""Tests for ui/serial_panel.py — SerialPanel widget."""


def test_serial_panel_connect_toggle(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    seen = []
    panel.connect_requested.connect(lambda baud: seen.append(("connect", baud)))
    panel.disconnect_requested.connect(lambda: seen.append(("disconnect",)))
    panel._connect_btn.click()
    assert seen[0][0] == "connect" and isinstance(seen[0][1], int)
    panel.set_connected(True)
    panel._connect_btn.click()
    assert seen[-1] == ("disconnect",)


def test_serial_panel_append_and_clear(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    panel.append_output("hello 1 2 3")
    assert "hello" in panel._output.toPlainText()
    panel.clear()
    assert panel._output.toPlainText() == ""


def test_serial_panel_send(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    sent = []
    panel.send_requested.connect(lambda text, ending: sent.append((text, ending)))
    panel.set_connected(True)
    panel._send_box.setText("ping")
    panel._send_btn.click()
    assert sent and sent[0][0] == "ping"


def test_serial_panel_plotter_toggle_switches_stack(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    panel._plotter_btn.setChecked(True)
    assert panel._stack.currentIndex() == 1
    panel._plotter_btn.setChecked(False)
    assert panel._stack.currentIndex() == 0


def test_serial_panel_initial_state(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    assert panel._connected is False
    assert panel._connect_btn.text() == "Connect"
    assert not panel._send_box.isEnabled()
    assert not panel._send_btn.isEnabled()
    assert panel._autoscroll_btn.isChecked()


def test_serial_panel_current_baud_and_ending(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    assert panel.current_baud() == 9600
    assert panel.current_ending() == "Newline"


def test_serial_panel_set_baud(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    panel.set_baud(115200)
    assert panel.current_baud() == 115200


def test_serial_panel_set_connected_disables_baud_combo(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    assert panel._baud_combo.isEnabled()
    panel.set_connected(True)
    assert not panel._baud_combo.isEnabled()
    assert panel._connect_btn.text() == "Disconnect"
    assert panel._send_box.isEnabled()
    assert panel._send_btn.isEnabled()
    panel.set_connected(False)
    assert panel._baud_combo.isEnabled()
    assert panel._connect_btn.text() == "Connect"


def test_serial_panel_send_clears_box_and_ignores_empty(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    sent = []
    panel.send_requested.connect(lambda text, ending: sent.append((text, ending)))
    panel.set_connected(True)

    # Empty text should not emit
    panel._send_box.setText("")
    panel._send_btn.click()
    assert sent == []

    panel._send_box.setText("hello")
    panel._send_btn.click()
    assert sent == [("hello", "Newline")]
    assert panel._send_box.text() == ""


def test_serial_panel_return_pressed_sends(qapp):
    from ui.serial_panel import SerialPanel

    panel = SerialPanel()
    sent = []
    panel.send_requested.connect(lambda text, ending: sent.append((text, ending)))
    panel.set_connected(True)
    panel._send_box.setText("abc")
    panel._send_box.returnPressed.emit()
    assert sent == [("abc", "Newline")]
