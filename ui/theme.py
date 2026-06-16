"""
ui/theme.py — "Hybrid Lab Console" design tokens and widget factories.

Single source of truth for the colour palette, monospace font, and the small
style-string widget factories shared across the UI. Previously these constants
were duplicated (and had drifted) across main_window.py, the editor, and
log_panel.py; those modules now import from here.
"""

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QGraphicsDropShadowEffect,
    QLabel,
    QPushButton,
    QWidget,
)

# ── Colour palette ────────────────────────────────────────────────────────────
BG_DEEP = "#0a0f0c"
BG_DARK = "#0d1310"
BG_MID = "#121a16"
BG_RAISED = "#171f1b"
BG_PANEL = "#101512"
BG_GUTTER = "#0d130f"
BORDER = "#22322a"
BORDER_HI = "#3c5347"
ACCENT_GRN = "#4ade80"
ACCENT_GRN_HI = "#3fc270"
ACCENT_AMBER = "#f0a93e"
ACCENT_ERROR = "#f0654a"
TEXT_DIM = "#5c7468"
TEXT_MID = "#93a89c"
TEXT_MAIN = "#e4f0e8"

FONT_MONO = '"JetBrains Mono", "Fira Code", "DejaVu Sans Mono", monospace'


# ── Widget factories ──────────────────────────────────────────────────────────
def tb_label(text: str) -> QLabel:
    """A small uppercase toolbar field label (e.g. 'Board')."""
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {TEXT_DIM}; font-family: {FONT_MONO}; font-size: 10px; font-weight: 700;"
        f" letter-spacing: 0.5px; margin-left: 6px; margin-right: 2px;"
    )
    return lbl


def make_combo(items: list, width: int) -> QComboBox:
    cb = QComboBox()
    cb.addItems(items)
    cb.setFixedWidth(width)
    cb.setFixedHeight(34)
    cb.setStyleSheet(
        f"QComboBox {{ background: {BG_RAISED}; color: {TEXT_MAIN}; font-family: {FONT_MONO};"
        f" border: 1px solid {BORDER}; border-radius: 6px; padding: 4px 12px;"
        f" font-size: 12px; }}"
        f"QComboBox:hover {{ border: 1px solid {BORDER_HI}; }}"
        f"QComboBox::drop-down {{ border: none; width: 24px; }}"
        f"QComboBox QAbstractItemView {{ background: {BG_DARK}; color: {TEXT_MAIN};"
        f" border: 1px solid {BORDER_HI}; selection-background-color: #1d3a2c; }}"
    )
    return cb


def make_btn(
    label: str,
    color: str = "",
    hover: str = "",
    secondary: bool = False,
    outline: bool = False,
    tooltip: str = "",
) -> QPushButton:
    btn = QPushButton(label)
    btn.setFixedHeight(34)
    if tooltip:
        btn.setToolTip(tooltip)
    if secondary:
        btn.setStyleSheet(
            f"QPushButton {{ background: {BG_RAISED}; color: {TEXT_MID}; font-family: {FONT_MONO};"
            f" border: 1px solid {BORDER}; border-radius: 6px;"
            f" padding: 0 12px; font-size: 12px; font-weight: 600; }}"
            f"QPushButton:hover {{ background: #1c2620; color: {TEXT_MAIN};"
            f" border-color: {BORDER_HI}; }}"
            f"QPushButton:pressed {{ background: {BG_DARK}; }}"
        )
    elif outline:
        btn.setFixedWidth(124)
        btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {ACCENT_GRN}; font-family: {FONT_MONO};"
            f" border: 1px solid {ACCENT_GRN}; border-radius: 6px;"
            f" padding: 0 16px; font-size: 12px; font-weight: 700; }}"
            f"QPushButton:hover {{ background: rgba(74, 222, 128, 0.12); }}"
            f"QPushButton:pressed {{ background: rgba(74, 222, 128, 0.2); }}"
        )
    else:
        btn.setFixedWidth(124)
        btn.setStyleSheet(
            f"QPushButton {{ background: {color}; color: {BG_DEEP}; font-family: {FONT_MONO};"
            f" border: none; border-radius: 6px;"
            f" padding: 0 16px; font-size: 12px; font-weight: 700; }}"
            f"QPushButton:hover {{ background: {hover}; }}"
            f"QPushButton:pressed {{ background: {hover}; }}"
        )
    return btn


def make_icon_btn(symbol: str, tooltip: str) -> QPushButton:
    btn = QPushButton(symbol)
    btn.setFixedSize(32, 34)
    btn.setToolTip(tooltip)
    btn.setStyleSheet(
        f"QPushButton {{ background: {BG_RAISED}; color: {TEXT_MID}; font-family: {FONT_MONO};"
        f" border: 1px solid {BORDER}; border-radius: 6px; font-size: 13px; font-weight: 600; }}"
        f"QPushButton:hover {{ background: #1c2620; color: {ACCENT_GRN}; border-color: {BORDER_HI}; }}"
        f"QPushButton:pressed {{ background: {BG_DARK}; }}"
    )
    return btn


def status_pill() -> QLabel:
    from PyQt6.QtCore import Qt

    lbl = QLabel()
    lbl.setTextFormat(Qt.TextFormat.RichText)
    lbl.setStyleSheet(
        f"QLabel {{ background: {BG_PANEL}; color: {TEXT_MID}; font-family: {FONT_MONO};"
        f" font-size: 11px; padding: 3px 10px; border: 1px solid {BORDER};"
        f" border-radius: 6px; margin: 3px 4px; }}"
    )
    return lbl


def pill_html(label: str, value: str, accent: str) -> str:
    return (
        f'<span style="color:{accent};">■</span>&nbsp;'
        f'<span style="color:{TEXT_DIM};">{label}</span> {value}'
    )


def apply_glow(widget: QWidget, colour: str) -> None:
    effect = QGraphicsDropShadowEffect(widget)
    effect.setColor(QColor(colour))
    effect.setBlurRadius(14)
    effect.setOffset(0, 0)
    widget.setGraphicsEffect(effect)


def window_stylesheet() -> str:
    return (
        f"QMainWindow {{"
        f"  background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
        f"    stop:0 {BG_DEEP}, stop:0.5 {BG_MID}, stop:1 #0c130f);"
        f"}}"
        f"QLabel {{ color: {TEXT_MAIN}; }}"
        f"QToolTip {{"
        f"  background: {BG_PANEL}; color: {TEXT_MAIN}; font-family: {FONT_MONO};"
        f"  border: 1px solid {BORDER_HI}; padding: 6px 8px;"
        f"}}"
    )
