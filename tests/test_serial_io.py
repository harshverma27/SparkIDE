from cli.serial_io import BAUD_RATES, list_serial_ports, parse_plot_values


def test_parse_plot_values_csv_positional():
    assert parse_plot_values("12,3.5,-7") == {"ch0": 12.0, "ch1": 3.5, "ch2": -7.0}


def test_parse_plot_values_whitespace():
    assert parse_plot_values("12 3.5 -7") == {"ch0": 12.0, "ch1": 3.5, "ch2": -7.0}


def test_parse_plot_values_labelled():
    assert parse_plot_values("temp:21.5 hum=40") == {"temp": 21.5, "hum": 40.0}


def test_parse_plot_values_mixed_skips_non_numeric():
    assert parse_plot_values("temp:21.5 status:ok") == {"temp": 21.5}


def test_parse_plot_values_non_numeric_returns_empty():
    assert parse_plot_values("hello world") == {}
    assert parse_plot_values("") == {}


def test_baud_rates_include_common():
    assert 9600 in BAUD_RATES and 115200 in BAUD_RATES


def test_list_serial_ports_uses_pyserial(monkeypatch):
    class FakePort:
        def __init__(self, device):
            self.device = device

    monkeypatch.setattr(
        "cli.serial_io.comports", lambda: [FakePort("/dev/ttyUSB0"), FakePort("/dev/ttyACM0")]
    )
    assert list_serial_ports() == ["/dev/ttyACM0", "/dev/ttyUSB0"]
