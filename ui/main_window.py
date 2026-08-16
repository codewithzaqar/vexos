"""ui/main_window.py - VexOS Main Shell Window"""
import sys
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication
from PyQt5.QtGui import QKeyEvent, QTextCursor

from core.mode_manager import ModeManager, Mode
from ui.buffer_view import BufferView
from ui.status_bar import StatusBar


class MainWindow(QMainWindow):
    """Primary VexOS window with motion and command support."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VexOS v0.0.1a")
        self.resize(960, 640)

        self.mode_manager = ModeManager(self)
        self.buffer = BufferView(self)
        self.status_bar = StatusBar(self)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.buffer, 1)
        layout.addWidget(self.status_bar)
        self.setCentralWidget(central)

        # Signals
        self.mode_manager.mode_changed.connect(self._on_mode_changed)
        self.mode_manager.command_line_changed.connect(self.status_bar.update_command_line)
        self.mode_manager.status_message.connect(self.status_bar.show_message)
        self.mode_manager.motion_requested.connect(self._on_motion)
        self.mode_manager.quit_requested.connect(self._on_quit)

        # Initial state
        self.buffer.setReadOnly(True)
        self.buffer.setFocus()
        self.setStyleSheet("QMainWindow { background-color: #1c1c1c; }")

    def _on_mode_changed(self, mode: Mode):
        self.status_bar.update_mode(mode)
        is_insert = mode == Mode.INSERT
        self.buffer.setReadOnly(not is_insert)
        self.buffer.set_readonly_visual(not is_insert)
        self.buffer.setFocus()

    def _on_motion(self, direction: str, count: int):
        """Handle programmatic cursor motions in NORMAL mode."""
        motion_map = {
            "left": lambda c: self.buffer.move_char(-1, c),
            "right": lambda c: self.buffer.move_char(1, c),
            "up": lambda c: self.buffer.move_line(-1, c),
            "down": lambda c: self.buffer.move_line(1, c),
        }
        action = motion_map.get(direction)
        if action:
            action(count)

    def _on_quit(self):
        QApplication.instance().quit()

    def keyPressEvent(self, event: QKeyEvent):
        consumed = self.mode_manager.handle_key(
            event.key(), event.text(), event.modifiers()
        )
        if not consumed and self.mode_manager.mode == Mode.INSERT:
            super().keyPressEvent(event)
        elif consumed:
            event.accept()
