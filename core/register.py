"""core/register.py - VexOS Register & Clipboard System"""
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication


class RegisterManager(QObject):
    """Manages named registers and system clipboard for yank/delete."""

    register_updated = pyqtSignal(str, str)  # (name, content)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._registers: dict[str, str] = {}
        self._last_yank: str = ""

    @property
    def default_register(self) -> str:
        return self._last_yank

    def set(self, name: str, content: str):
        self._registers[name] = content
        if name == '"':
            self._last_yank = content
        self.register_updated.emit(name, content)

    def get(self, name: str = '"') -> str:
        if name == '+':
            clipboard = QApplication.clipboard()
            return clipboard.text() if clipboard else ""
        if name == '*':
            clipboard = QApplication.clipboard()
            return clipboard.text(mode=QApplication.clipboard().Selection) if clipboard else ""
        return self._registers.get(name, self._last_yank)

    def yank(self, text: str, reg: str = '"'):
        self.set(reg, text)

    def delete(self, text: str, reg: str = '"'):
        """Delete stores in register (like Vim's d, unlike c)."""
        self.set(reg, text)
