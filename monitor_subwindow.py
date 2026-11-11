"""MDI subwindow that owns one serial monitoring session."""

from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QCloseEvent,
    QFont,
    QKeySequence,
    QShortcut,
    QTextCharFormat,
    QTextCursor,
)
from PyQt6.QtWidgets import QMdiSubWindow, QPlainTextEdit, QWidget

from serial_worker import SerialWorker
from settings import SerialSettings


class MonitorSubWindow(QMdiSubWindow):
    """MDI subwindow that owns one serial monitoring session."""

    state_changed = pyqtSignal(object)
    error_occurred = pyqtSignal(object, str)
    bytes_sent = pyqtSignal(object, int)

    _CATEGORY_COLORS: dict[str, str] = {
        "RX": "#0D47A1",
        "TX": "#1B5E20",
        "SESSION": "#424242",
        "ERR": "#B71C1C",
    }

    def __init__(self, title: str, dump_mode: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._worker: SerialWorker | None = None
        self._worker_factory = SerialWorker
        self._current_settings: SerialSettings | None = None
        self._rx_bytes = 0
        self._tx_bytes = 0
        self._rx_buffer = bytearray()
        self._log_format = "String"
        self._timestamp_enabled = False
        self._dump_mode = dump_mode
        self._file_backed = False

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("D2Coding", 10))
        self.log_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.log_view.document().setMaximumBlockCount(5000)
        self.log_view.setStyleSheet(
            """
            QPlainTextEdit {
                background: #ffffff;
                color: #1f2933;
                border: 1px solid #eee5da;
                border-radius: 12px;
                padding: 12px;
                selection-background-color: #d8b98f;
            }
            QPlainTextEdit:focus {
                border-color: #d9c1aa;
            }
            """
        )
        self.clear_shortcut = QShortcut(QKeySequence("Ctrl+X"), self.log_view)
        self.clear_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.clear_shortcut.activated.connect(self.clear_log)
        self.setWidget(self.log_view)
        self.setWindowTitle(title)
        self.resize(600, 400)

    @property
    def is_connected(self) -> bool:
        return self._worker is not None

    @property
    def current_settings(self) -> SerialSettings | None:
        return self._current_settings

    @property
    def rx_bytes(self) -> int:
        return self._rx_bytes

    @property
    def tx_bytes(self) -> int:
        return self._tx_bytes

    @property
    def received_data(self) -> bytes:
        return bytes(self._rx_buffer)

    @property
    def log_format(self) -> str:
        return self._log_format

    @log_format.setter
    def log_format(self, fmt: str) -> None:
        self._log_format = fmt
        if self._file_backed:
            self._render_loaded_data()

    @property
    def timestamp_enabled(self) -> bool:
        return self._timestamp_enabled

    @timestamp_enabled.setter
    def timestamp_enabled(self, enabled: bool) -> None:
        self._timestamp_enabled = enabled

    def start(self, settings: SerialSettings) -> None:
        if self._worker is not None:
            return
        self._current_settings = settings
        self._rx_bytes = 0
        self._tx_bytes = 0
        self._rx_buffer.clear()
        self._append("SESSION", f"{settings.port} 연결 시도 중 ({settings.baudrate} baud)")

        worker = self._worker_factory(settings, parent=self)
        worker.data_received.connect(self._on_data_received)
        worker.bytes_written.connect(self._on_bytes_written)
        if self._dump_mode:
            worker.data_written.connect(self._on_data_written)
        worker.error_occurred.connect(self._on_error)
        worker.port_opened.connect(self._on_port_opened)
        worker.port_closed.connect(self._on_port_closed)
        worker.finished.connect(lambda: self._on_finished(worker))
        self._worker = worker
        worker.start()
        self.state_changed.emit(self)

    def stop(self, wait: bool = False) -> None:
        worker = self._worker
        if worker is None:
            return
        worker.stop()
        if wait:
            worker.wait(3000)

    def write_data(self, payload: bytes) -> bool:
        if self._worker is None:
            return False
        return self._worker.write_data(payload)

    def append_log(self, category: str, message: str) -> None:
        if self._dump_mode and category == "TX":
            return
        self._append(category, message)

    def clear_log(self) -> None:
        self.log_view.clear()
        self._rx_buffer.clear()
        self._rx_bytes = 0
        self._tx_bytes = 0
        self.state_changed.emit(self)

    def load_received_data(self, data: bytes, title: str | None = None) -> None:
        self.stop(wait=False)
        self._file_backed = True
        self._current_settings = None
        self._rx_buffer = bytearray(data)
        self._rx_bytes = len(data)
        self._tx_bytes = 0
        if title:
            self.setWindowTitle(title)
        self._render_loaded_data()
        self.state_changed.emit(self)

    def _on_data_received(self, data: bytes) -> None:
        self._rx_buffer.extend(data)
        self._rx_bytes += len(data)
        self._append("RX", self._format_for_view(data))
        self.state_changed.emit(self)

    def _on_data_written(self, data: bytes) -> None:
        self._append("TX", self._format_for_view(data))

    def _on_bytes_written(self, count: int) -> None:
        self._tx_bytes += count
        self.bytes_sent.emit(self, count)
        self.state_changed.emit(self)

    def _on_error(self, msg: str) -> None:
        self._append("ERR", msg)
        self.error_occurred.emit(self, msg)

    def _on_port_opened(self, port: str) -> None:
        settings = self._current_settings
        baud = settings.baudrate if settings else "?"
        self.setWindowTitle(f"{port} - {baud} [연결됨]")
        self._append("SESSION", f"{port} 연결됨")
        self.state_changed.emit(self)

    def _on_port_closed(self, port: str) -> None:
        self._append("SESSION", f"{port} 연결 해제됨")

    def _on_finished(self, worker: SerialWorker) -> None:
        if self._worker is not worker:
            return
        self._worker = None
        settings = self._current_settings
        if settings:
            self.setWindowTitle(f"{settings.port} - {settings.baudrate}")
        self.state_changed.emit(self)
        worker.deleteLater()

    @staticmethod
    def _format_dump(data: bytes) -> str:
        hex_part = " ".join(f"{b:02X}" for b in data)
        ascii_part = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in data)
        return f"{hex_part}  |  {ascii_part}"

    def _format_for_view(self, data: bytes) -> str:
        # Dump view는 로그 형식이 Hex일 때만 "HEX | ASCII" 형태로 표시한다.
        # String 등 다른 형식에서는 해당 형식의 값만 출력한다.
        if self._dump_mode and self._log_format == "Hex":
            return self._format_dump(data)
        return self._format_bytes(data)

    def _format_bytes(self, data: bytes) -> str:
        mode = self._log_format
        if mode == "Hex":
            return " ".join(f"{b:02X}" for b in data)
        if mode == "Dec":
            return " ".join(str(b) for b in data)
        if mode == "Oct":
            return " ".join(f"{b:03o}" for b in data)
        if mode == "Bin":
            return " ".join(f"{b:08b}" for b in data)
        text = data.decode("utf-8", errors="replace")
        return (
            text.replace("\\", "\\\\")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )

    def _render_loaded_data(self) -> None:
        self.log_view.clear()
        data = bytes(self._rx_buffer)
        if not data:
            return
        self._append("RX", self._format_bytes(data))

    def _append(self, category: str, message: str) -> None:
        parts = []
        if self._timestamp_enabled:
            parts.append(datetime.now().strftime("%H:%M:%S.%f")[:-3])
        parts.append(f"[{category}]")
        line = f"{' '.join(parts)} {message}"

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(self._CATEGORY_COLORS.get(category, "#1f2933")))

        cursor = self.log_view.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if cursor.position() > 0:
            cursor.insertText("\n", QTextCharFormat())
        cursor.insertText(line, fmt)
        self.log_view.setTextCursor(cursor)
        self.log_view.moveCursor(QTextCursor.MoveOperation.End)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.stop(wait=True)
        super().closeEvent(event)
