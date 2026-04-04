"""`python -m deepmeerkat.ui` entry point."""

from __future__ import annotations

import sys

from PySide6.QtGui import QIcon, QPixmap


def main() -> None:
    from PySide6.QtWidgets import QApplication

    from deepmeerkat.ui.main_window import MainWindow
    from deepmeerkat.ui.resources import logo_png_bytes
    from deepmeerkat.ui.theme import apply_app_theme

    app = QApplication(sys.argv)
    apply_app_theme(app)

    pix = QPixmap()
    if pix.loadFromData(logo_png_bytes()):
        app.setWindowIcon(QIcon(pix))

    win = MainWindow()
    win.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
