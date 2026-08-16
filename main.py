#!/usr/bin/env python3
"""VexOS v0.0.1a - Entry Point"""
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("VexOS")
    app.setApplicationVersion("0.0.1a")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
