from __future__ import annotations
from mmo_viewer.ui.main_window import MainWindow

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from mmo_viewer.ui.main_window import MainWindow
from mmo_viewer.ui.theme import load_qss


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("MMO Viewer")
    app.setOrganizationName("MMO Viewer")
    app.setStyle("Fusion")
    app.setStyleSheet(load_qss())

    window = MainWindow()
    window.show()

    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1])
        if candidate.is_file():
            window.load_file(candidate)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
