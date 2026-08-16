"""core/mode_manager.py - VexOS Modal State Machine"""
from enum import Enum, auto
from PyQt5.QtCore import QObject, pyqtSignal
from core.command_engine import CommandEngine


class Mode(Enum):
    NORMAL = auto()
    INSERT = auto()
    COMMAND = auto()
    VISUAL = auto()


class ModeManager(QObject):
    """Central authority for VexOS modal state, motions, and commands."""

    mode_changed = pyqtSignal(Mode)
    command_line_changed = pyqtSignal(str)
    status_message = pyqtSignal(str)
    motion_requested = pyqtSignal(str, int)  # (direction, count)
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = Mode.NORMAL
        self._command_buffer = ""
        self._pending_count = ""

        # Command engine
        self.cmd_engine = CommandEngine(self)
        self.cmd_engine.message.connect(self.status_message.emit)
        self.cmd_engine.quit_requested.connect(self.quit_requested.emit)

    @property
    def mode(self) -> Mode:
        return self._mode

    def set_mode(self, new_mode: Mode):
        if new_mode != self._mode:
            self._mode = new_mode
            if new_mode != Mode.COMMAND:
                self._command_buffer = ""
                self.command_line_changed.emit("")
            if new_mode == Mode.NORMAL:
                self._pending_count = ""
            self.mode_changed.emit(new_mode)
            self.status_message.emit(f"-- {new_mode.name} --")

    def handle_key(self, key: int, text: str, modifiers) -> bool:
        from PyQt5.QtCore import Qt

        if self._mode == Mode.COMMAND:
            return self._handle_command_key(key, text)
        if self._mode == Mode.NORMAL:
            return self._handle_normal_key(key, text)
        if self._mode == Mode.INSERT:
            if key == Qt.Key_Escape:
                self.set_mode(Mode.NORMAL)
                return True
            return False
        return False

    def _handle_normal_key(self, key: int, text: str) -> bool:
        from PyQt5.QtCore import Qt

        # Count prefix accumulation
        if text.isdigit() and not (text == '0' and not self._pending_count):
            self._pending_count += text
            return True

        count = max(1, int(self._pending_count)) if self._pending_count else 1
        consumed = False

        if key == Qt.Key_H:
            self.motion_requested.emit("left", count)
            consumed = True
        elif key == Qt.Key_J:
            self.motion_requested.emit("down", count)
            consumed = True
        elif key == Qt.Key_K:
            self.motion_requested.emit("up", count)
            consumed = True
        elif key == Qt.Key_L:
            self.motion_requested.emit("right", count)
            consumed = True
        elif key == Qt.Key_I:
            self.set_mode(Mode.INSERT)
            consumed = True
        elif key == Qt.Key_Colon:
            self.set_mode(Mode.COMMAND)
            consumed = True
        elif key == Qt.Key_Escape:
            self._pending_count = ""
            self.status_message.emit("")
            consumed = True

        if consumed:
            self._pending_count = ""
        return consumed

    def _handle_command_key(self, key: int, text: str) -> bool:
        from PyQt5.QtCore import Qt

        if key == Qt.Key_Escape:
            self.set_mode(Mode.NORMAL)
            return True
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            self.cmd_engine.execute(self._command_buffer)
            self.set_mode(Mode.NORMAL)
            return True
        elif key == Qt.Key_Backspace:
            if self._command_buffer:
                self._command_buffer = self._command_buffer[:-1]
            else:
                self.set_mode(Mode.NORMAL)
            self.command_line_changed.emit(self._command_buffer)
            return True
        elif text and text.isprintable():
            self._command_buffer += text
            self.command_line_changed.emit(self._command_buffer)
            return True
        return False
