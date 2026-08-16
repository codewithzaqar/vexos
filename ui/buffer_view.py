"""ui/buffer_view.py - Central VexOS Workspace Buffer"""
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt


class BufferView(QPlainTextEdit):
    """Primary workspace widget. In v0.0.1a serves as desktop and scratch buffer."""

    WELCOME_TEXT = """\
╔══════════════════════════════════════╗
║            VexOS v0.0.1a             ║
║   A Vim-like Operating Environment   ║
╠══════════════════════════════════════╣
║                                      ║
║   NEW in a02:                        ║
║     h/j/k/l -> Basic cursor motions  ║
║     :q -> Quit VexOS                 ║
║     :echo -> Print to status line    ║
║     :help -> List commands           ║
║                                      ║
║  Modes:                              ║
║    i     → Enter INSERT mode         ║
║    Esc   → Return to NORMAL mode     ║
║    :     → Enter COMMAND mode        ║
║                                      ║       
╚══════════════════════════════════════╝
"""

    STYLE_READONLY = """
        QPlainTextEdit {
            background-color: #1c1c1c; color: #808080;
            border: none; padding: 8px; selection-background-color: #3a3a3a;
        }"""
    STYLE_EDITABLE = """
        QPlainTextEdit {
            background-color: #1c1c1c; color: #d0d0d0;
            border: none; padding: 8px; selection-background-color: #3a3a3a;
        }"""

    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont("Monospace", 12)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        self.setTabStopDistance(40)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet(self.STYLE_READONLY)
        self.setPlainText(self.WELCOME_TEXT)
        self.moveCursor(QTextCursor.End)

    def set_readonly_visual(self, readonly: bool):
        self.setStyleSheet(self.STYLE_READONLY if readonly else self.STYLE_EDITABLE)

    # --- Programmatic Motion API (works in read-only mode) ---

    def move_cursor(self, operation: QTextCursor.MoveOperation,
                    mode: QTextCursor.MoveMode = QTextCursor.MoveAnchor,
                    count: int = 1):
        """Move cursor programmatically regardless of read-only state."""
        cursor = self.textCursor()
        cursor.movePosition(operation, mode, count)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def move_line(self, direction: int, count: int = 1):
        """Move up (-1) or down (+1) by count lines."""
        op = QTextCursor.Down if direction > 0 else QTextCursor.Up
        self.move_cursor(op, count=count)

    def move_char(self, direction: int, count: int = 1):
        """Move left (-1) or right (+1) by count characters."""
        op = QTextCursor.Right if direction > 0 else QTextCursor.Left
        self.move_cursor(op, count=count)
