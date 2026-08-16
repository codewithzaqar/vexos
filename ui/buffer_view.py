"""ui/buffer_view.py - Central VexOS Workspace Buffer"""
from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QFont, QTextCursor


class BufferView(QPlainTextEdit):
    """Primary workspace widget. In v0.0.1a serves as desktop and scratch buffer."""

    WELCOME_TEXT = """\
╔══════════════════════════════════════╗
║            VexOS v0.0.1a             ║
║   A Vim-like Operating Environment   ║
╠══════════════════════════════════════╣
║                                      ║
║  Modes:                              ║
║    i     → Enter INSERT mode         ║
║    Esc   → Return to NORMAL mode     ║
║    :     → Enter COMMAND mode        ║
║                                      ║
║  This buffer IS your desktop.        ║
║  Edit freely in INSERT mode.         ║
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
