"""core/mode_manager.py - VexOS Modal State Machine"""
from enum import Enum, auto
from PyQt5.QtCore import QObject, pyqtSignal


class Mode(Enum):
    NORMAL = auto()
    INSERT = auto()
    COMMAND = auto()
    VISUAL = auto()  # Placeholder for future versions


class ModeManager(QObject):
    """Central authority for VexOS modal state and key translation."""

    mode_changed = pyqtSignal(Mode)
    command_line_changed = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = Mode.NORMAL
        self._command_buffer = ""
        self._pending_keys = ""

    @property
    def mode(self) -> Mode:
        return self._mode

    def set_mode(self, new_mode: Mode):
        if new_mode != self._mode:
            self._mode = new_mode
            if new_mode != Mode.COMMAND:
                self._command_buffer = ""
                self.command_line_changed.emit("")
            self.mode_changed.emit(new_mode)
            self.status_message.emit(f"-- {new_mode.name} --")

    def handle_key(self, key: int, text: str, modifiers) -> bool:
        """Process a raw key event. Returns True if consumed."""
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

        if key == Qt.Key_I:
            self.set_mode(Mode.INSERT)
            return True
        elif key == Qt.Key_Colon:
            self.set_mode(Mode.COMMAND)
            return True
        elif key == Qt.Key_Escape:
            self._pending_keys = ""
            self.status_message.emit("")
            return True
        return False

    def _handle_command_key(self, key: int, text: str) -> bool:
        from PyQt5.QtCore import Qt

        if key == Qt.Key_Escape:
            self.set_mode(Mode.NORMAL)
            return True
        elif key in (Qt.Key_Return, Qt.Key_Enter):
            cmd = self._command_buffer.strip()
            self.status_message.emit(f":{cmd} [not implemented]")
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
