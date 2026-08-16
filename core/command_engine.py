"""core/command_engine.py - VexOS Command Execution Engine"""
from PyQt5.QtCore import QObject, pyqtSignal


class CommandEngine(QObject):
    """Parses and executes :commands entered in COMMAND mode."""

    message = pyqtSignal(str)
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._commands = {
            "q": self._cmd_quit,
            "quit": self._cmd_quit,
            "w": self._cmd_write,
            "write": self._cmd_write,
            "echo": self._cmd_echo,
            "help": self._cmd_help,
        }

    def execute(self, raw_input: str):
        """Parse and dispatch a command string."""
        parts = raw_input.strip().split(maxsplit=1)
        if not parts or not parts[0]:
            return

        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        handler = self._commands.get(cmd)
        if handler:
            handler(args)
        else:
            self.message.emit(f"E492: Not a VexOS command: {cmd}")

    def _cmd_quit(self, args: str):
        self.quit_requested.emit()

    def _cmd_write(self, args: str):
        # Placeholder: real filesystem integration comes in a03+
        target = args.strip() or "(unnamed buffer)"
        self.message.emit(f'"{target}" [write not yet implemented]')

    def _cmd_echo(self, args: str):
        self.message.emit(args if args else "")

    def _cmd_help(self, args: str):
        available = ", ".join(sorted(set(self._commands.keys())))
        self.message.emit(f"Available commands: {available}")
