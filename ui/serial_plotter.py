"""ui/serial_plotter.py — live multi-series plot of numeric serial values."""

from collections import defaultdict, deque

import pyqtgraph as pg
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from cli.serial_io import parse_plot_values
from ui import theme

_CURVE_COLOURS = [theme.ACCENT_GRN, theme.ACCENT_AMBER, "#5aa9e6", theme.ACCENT_ERROR, "#b07fff"]


class SerialPlotter(QWidget):
    """Parses numeric values from serial lines and draws one rolling curve per series."""

    def __init__(self, max_points: int = 500, parent=None):
        super().__init__(parent)
        self._max_points = max_points
        self._buffers: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self._curves: dict[str, pg.PlotDataItem] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        pg.setConfigOptions(antialias=True)
        self._plot = pg.PlotWidget(background=theme.BG_PANEL)
        self._plot.showGrid(x=True, y=True, alpha=0.15)
        self._plot.addLegend()
        layout.addWidget(self._plot)

    def feed(self, line: str) -> None:
        values = parse_plot_values(line)
        if not values:
            return
        for name, value in values.items():
            self._buffers[name].append(value)
            if name not in self._curves:
                colour = _CURVE_COLOURS[len(self._curves) % len(_CURVE_COLOURS)]
                self._curves[name] = self._plot.plot(name=name, pen=pg.mkPen(colour, width=2))
            self._curves[name].setData(list(self._buffers[name]))

    def clear(self) -> None:
        self._buffers.clear()
        for curve in self._curves.values():
            self._plot.removeItem(curve)
        self._curves.clear()
