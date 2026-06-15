import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from ui.workers import ArduinoJobWorker, CoreJobWorker, SerialReadWorker


def test_serial_worker_send_no_port_is_safe(qapp):
    w = SerialReadWorker("/dev/null", 9600)
    w.send("hi")  # _serial is None -> must not raise


def test_workers_have_expected_signals(qapp):
    assert hasattr(ArduinoJobWorker, "stats")
    assert hasattr(SerialReadWorker, "line_received")
    assert hasattr(SerialReadWorker, "connection_error")
    assert hasattr(CoreJobWorker, "finished")
    assert hasattr(CoreJobWorker, "line")
