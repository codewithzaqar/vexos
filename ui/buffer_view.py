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
║   NEW in a03:                        ║
║     dw/d3j/dd -> Delete + motion     ║
║     x -> Delete single char          ║
║     yy/yw -> Yank to register        ║
║     p -> Paste from register         ║
║     Registers -> ", +, * supported   ║
║                                      ║
║   Previous:                          ║
║     h/j/k/l -> Cursor motions        ║
║     :q/:echo -> Command engine       ║
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
        cursor = self.textCursor()
        cursor.movePosition(operation, mode, count)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def move_line(self, direction: int, count: int = 1):
        op = QTextCursor.Down if direction > 0 else QTextCursor.Up
        self.move_cursor(op, count=count)

    def move_char(self, direction: int, count: int = 1):
        op = QTextCursor.Right if direction > 0 else QTextCursor.Left
        self.move_cursor(op, count=count)

    # --- Text Manipulation API (for operators) ---

    def get_char_under_cursor(self) -> str:
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        return cursor.selectedText()

    def delete_char_under_cursor(self) -> str:
        """Delete single character under cursor, return deleted text."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        cursor.removeSelectedText()
        self.setTextCursor(cursor)
        return text

    def delete_current_line(self) -> str:
        """Delete entire current line including newline, return deleted text."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        # Include the trailing newline
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        cursor.removeSelectedText()
        self.setTextCursor(cursor)
        return text

    def paste_after_cursor(self, text: str):
        """Paste text after cursor position."""
        if not text:
            return
        cursor = self.textCursor()
        # If text contains newlines, paste on next line
        if '\n' in text or '\u2029' in text:
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText('\n' + text.rstrip('\n').replace('\u2029', '\n'))
        else:
            cursor.movePosition(QTextCursor.NextCharacter)
            cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def get_selected_text(self) -> str:
        return self.textCursor().selectedText()

    def remove_selection(self):
        cursor = self.textCursor()
        cursor.removeSelectedText()
        self.setTextCursor(cursor)
