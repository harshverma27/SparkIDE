"""Tests for ui/serial_plotter.py."""


def test_plotter_feed_creates_series(qapp):
    from ui.serial_plotter import SerialPlotter

    p = SerialPlotter()
    p.feed("1,2,3")
    p.feed("4,5,6")
    assert set(p._curves) == {"ch0", "ch1", "ch2"}
    p.feed("not numbers")  # ignored
    assert set(p._curves) == {"ch0", "ch1", "ch2"}
    p.clear()
    assert p._curves == {}


def test_plotter_rolling_window(qapp):
    from ui.serial_plotter import SerialPlotter

    p = SerialPlotter(max_points=3)
    for i in range(5):
        p.feed(str(i))
    assert list(p._buffers["ch0"]) == [2.0, 3.0, 4.0]
