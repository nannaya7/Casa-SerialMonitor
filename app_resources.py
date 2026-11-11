"""Application resource paths and helpers."""

from __future__ import annotations

from pathlib import Path
import sys


APP_NAME = "CasaSerialMonitor"
ICON_RELATIVE_PATH = Path("image") / "CASA_Serial_APP_ICON.png"
BUTTONS_RELATIVE_PATH = Path("image") / "buttons"
MAIN_WINDOW_UI_RELATIVE_PATH = Path("UI") / "mainWindow.ui"


def resource_path(relative_path: Path) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path
