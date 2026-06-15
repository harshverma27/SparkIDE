"""
ui/toolbar.py — main application toolbar.

ToolbarMixin builds the top toolbar (brand, workspace view controls, board/port
selectors, and the Compile/Upload actions) onto a MainWindow. It is a mixin so
the toolbar widgets and the slots they connect to share one `self`.
"""

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QLabel, QSizePolicy, QToolBar, QWidget

from ui import theme


class ToolbarMixin:
    """Provides `_build_toolbar`; expects MainWindow's action slots to exist."""

    def _build_toolbar(self):
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        tb.setFixedHeight(58)
        tb.setStyleSheet(
            f"QToolBar {{"
            f"  background: {theme.BG_DEEP};"
            f"  border-bottom: 1px solid {theme.BORDER};"
            f"  padding: 0 16px;"
            f"  spacing: 6px;"
            f"}}"
            f"QToolBar::separator {{"
            f"  background: {theme.BORDER_HI};"
            f"  width: 1px;"
            f"  margin: 12px 8px;"
            f"}}"
        )
        self.addToolBar(tb)

        brand = QLabel("SparkIDE")
        brand.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-family: {theme.FONT_MONO}; font-size: 18px;"
            " font-weight: 700; padding-right: 6px; letter-spacing: 0.4px;"
        )
        tb.addWidget(brand)
        tag = QLabel("> visual arduino studio")
        tag.setStyleSheet(
            f"color: {theme.TEXT_DIM}; font-family: {theme.FONT_MONO}; font-size: 11px;"
            " font-weight: 600; padding-right: 16px;"
        )
        tb.addWidget(tag)
        tb.addSeparator()

        # ── Workspace view controls ──────────────────────────────────────────
        self._center_btn = theme.make_icon_btn("⊙", "Center the workspace")
        self._center_btn.clicked.connect(self._on_center_workspace)
        tb.addWidget(self._center_btn)

        self._fit_btn = theme.make_icon_btn("⤢", "Zoom to fit")
        self._fit_btn.clicked.connect(self._on_zoom_to_fit)
        tb.addWidget(self._fit_btn)

        self._reset_view_btn = theme.make_icon_btn("⌫", "Reset workspace")
        self._reset_view_btn.clicked.connect(self._on_clear)
        tb.addWidget(self._reset_view_btn)

        tb.addSeparator()

        # ── Board selector ──────────────────────────────────────────────────
        tb.addWidget(theme.tb_label("Board"))
        self._board_combo = theme.make_combo(["Loading..."], 245)
        self._board_combo.currentTextChanged.connect(self._update_status)
        tb.addWidget(self._board_combo)

        tb.addSeparator()

        # ── Port selector ───────────────────────────────────────────────────
        tb.addWidget(theme.tb_label("Port"))
        self._port_combo = theme.make_combo(["No port detected"], 175)
        self._port_combo.currentTextChanged.connect(self._update_status)
        tb.addWidget(self._port_combo)

        self._refresh_btn = theme.make_btn("↺", secondary=True, tooltip="Refresh boards and ports")
        self._refresh_btn.setFixedWidth(32)
        self._refresh_btn.clicked.connect(self._on_refresh_ports)
        tb.addWidget(self._refresh_btn)

        # ── Spacer ──────────────────────────────────────────────────────────
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(spacer)

        # ── Action buttons ──────────────────────────────────────────────────
        self._compile_btn = theme.make_btn(
            "⚡  Compile", outline=True, tooltip="Compile sketch (arduino-cli)"
        )
        self._compile_btn.clicked.connect(self._on_compile)
        tb.addWidget(self._compile_btn)

        self._upload_btn = theme.make_btn(
            "⬆  Upload",
            color=theme.ACCENT_GRN,
            hover=theme.ACCENT_GRN_HI,
            tooltip="Compile & upload to board",
        )
        self._upload_btn.clicked.connect(self._on_upload)
        tb.addWidget(self._upload_btn)
