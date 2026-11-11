"""CasaSerial application entry point."""

from __future__ import annotations

import ctypes
from pathlib import Path
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from PyQt6.QtWidgets import QApplication

from app_resources import APP_NAME, ICON_RELATIVE_PATH, resource_path
from main_window import CasaSerialWindow


def main() -> int:
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CasaSerial.App")

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("CasaSerial")
    app.setWindowIcon(QIcon(str(resource_path(ICON_RELATIVE_PATH))))

    QFontDatabase.addApplicationFont(
        str(resource_path(Path("Fonts") / "Inter-VariableFont_opsz,wght.ttf"))
    )
    QFontDatabase.addApplicationFont(
        str(resource_path(Path("Fonts") / "D2Coding-Ver1.3.2-20180524-all.ttc"))
    )
    app.setFont(QFont("Inter", 10))

    window = CasaSerialWindow()
    window.show()
    # 시작 직후 이벤트 루프에서 New Session 창을 하나 띄운다.
    QTimer.singleShot(0, window.new_session_action.trigger)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
