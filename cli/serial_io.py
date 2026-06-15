"""cli/serial_io.py — Qt-free serial helpers (ports, line parsing)."""

from __future__ import annotations

import re

from serial.tools.list_ports import comports

BAUD_RATES = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 74880, 115200, 230400, 250000]
# label -> bytes appended to outgoing lines
LINE_ENDINGS = {
    "No line ending": b"",
    "Newline": b"\n",
    "Carriage return": b"\r",
    "Both NL & CR": b"\r\n",
}

_LABELLED = re.compile(r"([A-Za-z_]\w*)\s*[:=]\s*(-?\d+(?:\.\d+)?)")
_NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")


def list_serial_ports() -> list[str]:
    """Sorted list of serial device paths discovered by pyserial."""
    return sorted(p.device for p in comports())


def parse_plot_values(line: str) -> dict[str, float]:
    """Extract {series: value} from one serial line. {} if no numbers found.

    Supports `label:value`/`label=value`, and positional CSV/whitespace numbers
    (named ch0, ch1, ...). Labelled pairs take priority; if any exist, only they
    are returned.
    """
    line = line.strip()
    if not line:
        return {}
    labelled = {m.group(1): float(m.group(2)) for m in _LABELLED.finditer(line)}
    if labelled:
        return labelled
    tokens = re.split(r"[,\s]+", line)
    values: dict[str, float] = {}
    for i, tok in enumerate(tokens):
        if _NUMBER.match(tok):
            values[f"ch{i}"] = float(tok)
    return values
