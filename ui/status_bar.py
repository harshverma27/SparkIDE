"""
ui/status_bar.py — telemetry status bar (board / port / block-count pills).

StatusBarMixin builds the bottom status strip and provides the helpers that
update it. A mixin so the pills and their updater slots share one `self`.
"""

from PyQt6.QtWidgets import QLabel, QStatusBar

from ui import theme


class StatusBarMixin:
    """Provides the status-bar build + update helpers for MainWindow."""

    def _build_status_bar(self):
        sb = QStatusBar()
        sb.setFixedHeight(32)
        sb.setStyleSheet(
            f"QStatusBar {{ background: {theme.BG_DEEP}; border-top: 1px solid {theme.BORDER}; }}"
            f"QStatusBar::item {{ border: none; }}"
        )
        self.setStatusBar(sb)

        # Telemetry readouts
        self._sb_board = theme.status_pill()
        sb.addWidget(self._sb_board)

        self._sb_port = theme.status_pill()
        sb.addWidget(self._sb_port)

        self._sb_blocks = theme.status_pill()
        sb.addWidget(self._sb_blocks)

        # Status indicator (right side)
        self._sb_status = QLabel("● Idle")
        sb.addPermanentWidget(self._sb_status)

        self._update_status()
        self._update_block_count(0)
        self._set_status("● Idle", theme.ACCENT_GRN)

    def _update_status(self):
        b = getattr(self, "_board_combo", None)
        p = getattr(self, "_port_combo", None)
        board = b.currentText() if b else "—"
        port = p.currentText() if p else "—"

        if hasattr(self, "_sb_board"):
            self._sb_board.setText(theme.pill_html("BOARD:", board, theme.ACCENT_GRN))
        if hasattr(self, "_sb_port"):
            self._sb_port.setText(theme.pill_html("PORT:", port, theme.ACCENT_GRN))

    def _update_block_count(self, count: int):
        if hasattr(self, "_sb_blocks"):
            self._sb_blocks.setText(theme.pill_html("BLOCKS:", str(count), theme.ACCENT_AMBER))

    def _set_status(self, text: str, colour: str):
        if hasattr(self, "_sb_status"):
            self._sb_status.setText(text)
            self._sb_status.setStyleSheet(
                f"color: {colour}; font-family: {theme.FONT_MONO}; font-size: 11px; padding: 0 10px;"
            )
            theme.apply_glow(self._sb_status, colour)
