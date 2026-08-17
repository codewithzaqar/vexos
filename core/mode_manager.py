"""core/mode_manager.py - VexOS Modal State Machine v0.0.1a"""
from enum import Enum, auto
from PyQt5.QtCore import QObject, pyqtSignal
from core.command_engine import CommandEngine
from core.operator import OperatorType, PendingOperator, OPERATOR_MAP, SIMPLE_OPERATORS
from core.register import RegisterManager


class Mode(Enum):
    NORMAL = auto()
    INSERT = auto()
    COMMAND = auto()
    VISUAL = auto()
    OPERATOR_PENDING = auto()


class ModeManager(QObject):
    """Modal state machine with operator-pending support."""

    mode_changed = pyqtSignal(Mode)
    command_line_changed = pyqtSignal(str)
    status_message = pyqtSignal(str)
    motion_requested = pyqtSignal(str, int)
    quit_requested = pyqtSignal()
    operator_execute = pyqtSignal(object)  # Emits PendingOperator when complete
    simple_operator = pyqtSignal(object)   # Emits for x, dd etc.
    paste_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = Mode.NORMAL
        self._command_buffer = ""
        self._pending_count = ""
        self._pending_op: PendingOperator | None = None

        self.cmd_engine = CommandEngine(self)
        self.cmd_engine.message.connect(self.status_message.emit)
        self.cmd_engine.quit_requested.connect(self.quit_requested.emit)

        self.registers = RegisterManager(self)

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
                self._pending_op = None
            self.mode_changed.emit(new_mode)
            if new_mode == Mode.OPERATOR_PENDING:
                op_name = self._pending_op.op_type.name if self._pending_op else "?"
                self.status_message.emit(f"-- {op_name} PENDING --")
            else:
                self.status_message.emit(f"-- {new_mode.name} --")

    def handle_key(self, key: int, text: str, modifiers) -> bool:
        from PyQt5.QtCore import Qt

        if self._mode == Mode.COMMAND:
            return self._handle_command_key(key, text)
        if self._mode in (Mode.NORMAL, Mode.OPERATOR_PENDING):
            return self._handle_normal_key(key, text)
        if self._mode == Mode.INSERT:
            if key == Qt.Key_Escape:
                self.set_mode(Mode.NORMAL)
                return True
            return False
        return False

    def _handle_normal_key(self, key: int, text: str) -> bool:
        from PyQt5.QtCore import Qt

        # Escape cancels everything
        if key == Qt.Key_Escape:
            self._pending_count = ""
            self._pending_op = None
            self.set_mode(Mode.NORMAL)
            self.status_message.emit("")
            return True

        # Count prefix accumulation
        if text.isdigit() and not (text == '0' and not self._pending_count):
            self._pending_count += text
            return True

        count = max(1, int(self._pending_count)) if self._pending_count else 1

        # --- OPERATOR-PENDING MODE: waiting for motion ---
        if self._mode == Mode.OPERATOR_PENDING and self._pending_op:
            # Double operator = line-wise (dd, yy, cc)
            op_char = {'d': 'd', 'y': 'y', 'c': 'c'}
            expected = op_char.get({v: k for k, v in OPERATOR_MAP.items()}.get(
                self._pending_op.op_type), None)

            if text == expected:
                # Line-wise operator
                self._pending_op.count *= count
                self.simple_operator.emit(self._pending_op)
                self.set_mode(Mode.NORMAL)
                return True

            # Map motion keys to directions
            motion_map = {'h': 'left', 'j': 'down', 'k': 'up', 'l': 'right',
                          'w': 'word_forward', 'b': 'word_backward',
                          '0': 'line_start', '$': 'line_end'}
            if text in motion_map:
                self._pending_op.count *= count
                # Emit operator + motion for MainWindow to execute
                self.operator_execute.emit((self._pending_op, motion_map[text], count))
                self.set_mode(Mode.NORMAL)
                return True

            # Invalid motion after operator → cancel
            self._pending_op = None
            self.set_mode(Mode.NORMAL)
            self.status_message.emit("E: Invalid motion")
            return True

        # --- NORMAL MODE ---
        # Check for operator start
        if text in OPERATOR_MAP:
            self._pending_op = PendingOperator(
                op_type=OPERATOR_MAP[text],
                count=count,
                register='"'
            )
            self.set_mode(Mode.OPERATOR_PENDING)
            return True

        # Simple operators (no motion needed)
        if text in SIMPLE_OPERATORS:
            op = PendingOperator(op_type=SIMPLE_OPERATORS[text], count=count)
            self.simple_operator.emit(op)
            self._pending_count = ""
            return True

        # Paste
        if text == 'p':
            self.paste_requested.emit()
            self._pending_count = ""
            return True

        # Motions without operator
        motion_map = {'h': 'left', 'j': 'down', 'k': 'up', 'l': 'right'}
        if text in motion_map:
            self.motion_requested.emit(motion_map[text], count)
            self._pending_count = ""
            return True

        # Mode transitions
        if key == Qt.Key_I:
            self.set_mode(Mode.INSERT)
            return True
        if key == Qt.Key_Colon:
            self.set_mode(Mode.COMMAND)
            return True

        return False

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
