"""Application font and stylesheet (modern, readable defaults)."""

from __future__ import annotations

import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


def apply_app_theme(app: QApplication) -> None:
    """Set a slightly larger system-appropriate font and light polish."""
    base = app.font()
    if sys.platform == "darwin":
        # Prefer SF Pro Text if available; fall back to system UI font.
        f = QFont("SF Pro Text")
        if not f.exactMatch():
            f = base
        f.setPointSize(13)
    elif sys.platform == "win32":
        f = QFont("Segoe UI Variable", 10)
        if not f.exactMatch():
            f = QFont("Segoe UI", 10)
    else:
        f = QFont(base)
        f.setPointSize(11)
    app.setFont(f)

    app.setStyleSheet(
        """
        QGroupBox {
            font-weight: 600;
            margin-top: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
        }
        QPushButton {
            padding: 7px 16px;
        }
        QTextEdit {
            font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
            font-size: 12px;
        }
        QLabel#HeaderTitle {
            font-size: 22px;
            font-weight: 600;
            letter-spacing: -0.4px;
        }
        QLabel#HeaderSubtitle {
            font-size: 13px;
            color: palette(mid);
        }
        QLabel#PreviewCaption {
            font-size: 12px;
            color: palette(mid);
        }
        """
    )
