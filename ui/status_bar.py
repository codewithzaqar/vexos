"""ui/status_bar.py - VexOS Status Line"""
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt
from core.mode_manager import Mode


class StatusBar(QWidget):
    """Bottom status bar mimicking Vim's cmdline/statusline."""

    MODE_COLORS = {
        Mode.NORMAL: "#5f87af",
        Mode.INSERT: "#5faf5f",
        Mode.COMMAND: "#d7af5f",
        Mode.VISUAL: "#af5faf",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(0)

        font = QFont("Monospace", 11)
        font.setStyleHint(QFont.Monospace)

        self.mode_label = QLabel("-- NORMAL --")
        self.mode_label.setFont(font)
        self.mode_label.setFixedWidth(140)

        self.message_label = QLabel("")
        self.message_label.setFont(font)
        self.message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(self.mode_label)
        layout.addWidget(self.message_label, 1)
        self._update_mode_style(Mode.NORMAL)

    def update_mode(self, mode: Mode):
        self.mode_label.setText(f"-- {mode.name} --")
        self._update_mode_style(mode)

    def update_command_line(self, text: str):
        self.message_label.setText(f":{text}" if text else "")

    def show_message(self, msg: str):
        self.message_label.setText(msg)

    def _update_mode_style(self, mode: Mode):
        color = self.MODE_COLORS.get(mode, "#888888")
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        palette.setColor(QPalette.WindowText, QColor("#1c1c1c"))
        self.setPalette(palette)
        self.mode_label.setPalette(palette)
        self.message_label.setPalette(palette)
