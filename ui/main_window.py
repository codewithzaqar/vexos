"""ui/main_window.py - VexOS Main Shell Window v0.0.1a"""
import sys
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication
from PyQt5.QtGui import QKeyEvent, QTextCursor

from core.mode_manager import ModeManager, Mode
from core.operator import OperatorType, PendingOperator
from ui.buffer_view import BufferView
from ui.status_bar import StatusBar


class MainWindow(QMainWindow):
    """Primary VexOS window with operator+motion composition."""

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
        mm = self.mode_manager
        mm.mode_changed.connect(self._on_mode_changed)
        mm.command_line_changed.connect(self.status_bar.update_command_line)
        mm.status_message.connect(self.status_bar.show_message)
        mm.motion_requested.connect(self._on_motion)
        mm.quit_requested.connect(self._on_quit)
        mm.simple_operator.connect(self._on_simple_operator)
        mm.operator_execute.connect(self._on_operator_motion)
        mm.paste_requested.connect(self._on_paste)

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
        motion_actions = {
            "left": lambda c: self.buffer.move_char(-1, c),
            "right": lambda c: self.buffer.move_char(1, c),
            "up": lambda c: self.buffer.move_line(-1, c),
            "down": lambda c: self.buffer.move_line(1, c),
        }
        action = motion_actions.get(direction)
        if action:
            action(count)

    def _on_simple_operator(self, op: PendingOperator):
        """Handle operators that don't need a motion (x, dd, yy)."""
        if op.op_type == OperatorType.DELETE:
            if op.count == 1 and not hasattr(op, '_line_wise'):
                # 'x' - delete char under cursor
                for _ in range(op.count):
                    text = self.buffer.delete_char_under_cursor()
                    self.mode_manager.registers.delete(text)
            else:
                # 'dd' - delete line(s)
                texts = []
                for _ in range(op.count):
                    texts.append(self.buffer.delete_current_line())
                self.mode_manager.registers.delete(''.join(texts))

        elif op.op_type == OperatorType.YANK:
            # 'yy' - yank line(s)
            cursor = self.buffer.textCursor()
            texts = []
            for _ in range(op.count):
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
                texts.append(cursor.selectedText())
                cursor.movePosition(QTextCursor.Down)
            self.mode_manager.registers.yank(''.join(texts))
            self.status_bar.show_message(f"{op.count} line(s) yanked")

    def _on_operator_motion(self, payload: tuple):
        """Handle operator + motion combinations (dw, d3j, etc.)."""
        op, motion, motion_count = payload
        total_count = op.count * motion_count

        # For a03, implement basic char/line motions with operators
        if motion in ('left', 'right'):
            cursor = self.buffer.textCursor()
            direction = 1 if motion == 'right' else -1
            op_type = QTextCursor.NextCharacter if direction > 0 else QTextCursor.PreviousCharacter
            cursor.movePosition(op_type, QTextCursor.KeepAnchor, total_count)
            text = cursor.selectedText()
            if op.op_type == OperatorType.DELETE:
                cursor.removeSelectedText()
                self.buffer.setTextCursor(cursor)
                self.mode_manager.registers.delete(text)
            elif op.op_type == OperatorType.YANK:
                self.mode_manager.registers.yank(text)
                self.status_bar.show_message(f"Yanked {len(text)} chars")

        elif motion in ('up', 'down'):
            # Line-range operations
            cursor = self.buffer.textCursor()
            cursor.movePosition(QTextCursor.StartOfLine)
            line_op = QTextCursor.Down if motion == 'down' else QTextCursor.Up
            cursor.movePosition(line_op, QTextCursor.KeepAnchor, total_count)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
            text = cursor.selectedText()
            if op.op_type == OperatorType.DELETE:
                cursor.removeSelectedText()
                self.buffer.setTextCursor(cursor)
                self.mode_manager.registers.delete(text)
            elif op.op_type == OperatorType.YANK:
                self.mode_manager.registers.yank(text)
                lines = text.count('\n') + text.count('\u2029')
                self.status_bar.show_message(f"{lines} line(s) yanked")

        # TODO: word_forward, word_backward, line_start, line_end

    def _on_paste(self):
        text = self.mode_manager.registers.get('"')
        if text:
            # Temporarily enable editing for paste
            was_readonly = self.buffer.isReadOnly()
            self.buffer.setReadOnly(False)
            self.buffer.paste_after_cursor(text)
            self.buffer.setReadOnly(was_readonly)
            self.status_bar.show_message(f"Pasted {len(text)} chars")

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
