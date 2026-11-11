"""Background serial I/O worker."""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal
import serial

from settings import SerialSettings


READ_TIMEOUT_SECONDS = 0.1
RX_COALESCE_DELAY_SECONDS = 0.01


class SerialWorker(QThread):
    """Background thread that owns a pyserial connection and receive loop."""

    data_received = pyqtSignal(bytes)
    bytes_written = pyqtSignal(int)
    data_written = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    port_opened = pyqtSignal(str)
    port_closed = pyqtSignal(str)

    def __init__(
        self,
        settings: SerialSettings,
        serial_factory: Callable[..., Any] = serial.Serial,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self._serial_factory = serial_factory
        self._stop_requested = threading.Event()
        self._serial: Any | None = None
        self._io_lock = threading.Lock()

    def stop(self) -> None:
        """Request the receive loop to stop and unblock a pending read."""
        self._stop_requested.set()
        current_serial = self._serial
        if current_serial is None:
            return

        cancel_read = getattr(current_serial, "cancel_read", None)
        if callable(cancel_read):
            try:
                cancel_read()
            except (OSError, serial.SerialException):
                pass

    def write_data(self, payload: bytes) -> bool:
        if not payload:
            return False

        with self._io_lock:
            current_serial = self._serial
            if current_serial is None or not getattr(current_serial, "is_open", True):
                self.error_occurred.emit("Cannot send data because the serial port is not open.")
                return False

            try:
                written = current_serial.write(payload)
                flush = getattr(current_serial, "flush", None)
                if callable(flush):
                    flush()
            except (OSError, serial.SerialException) as exc:
                self.error_occurred.emit(f"Failed to send data on {self.settings.port}: {exc}")
                return False

        self.bytes_written.emit(int(written))
        self.data_written.emit(payload[:int(written)])
        return True

    def run(self) -> None:
        try:
            self._serial = self._open_serial()
            self.port_opened.emit(self.settings.port)
            self._receive_loop()
        except serial.SerialException as exc:
            if not self._stop_requested.is_set():
                self.error_occurred.emit(f"Serial error on {self.settings.port}: {exc}")
        except OSError as exc:
            if not self._stop_requested.is_set():
                self.error_occurred.emit(f"Port error on {self.settings.port}: {exc}")
        except Exception as exc:
            if not self._stop_requested.is_set():
                self.error_occurred.emit(f"Unexpected serial worker error: {exc}")
        finally:
            self._close_serial()
            self.port_closed.emit(self.settings.port)

    def _open_serial(self) -> Any:
        return self._serial_factory(
            port=self.settings.port,
            baudrate=self.settings.baudrate,
            bytesize=self.settings.bytesize,
            parity=self.settings.parity,
            stopbits=self.settings.stopbits,
            rtscts=self.settings.rtscts,
            xonxoff=self.settings.xonxoff,
            timeout=READ_TIMEOUT_SECONDS,
        )

    def _receive_loop(self) -> None:
        while not self._stop_requested.is_set():
            current_serial = self._serial
            if current_serial is None:
                return

            with self._io_lock:
                waiting = getattr(current_serial, "in_waiting", 0)
                read_size = max(1, int(waiting or 1))
                chunk = current_serial.read(read_size)
            if chunk:
                self.data_received.emit(self._coalesce_rx_chunk(bytes(chunk)))

    def _coalesce_rx_chunk(self, first_chunk: bytes) -> bytes:
        data = bytearray(first_chunk)
        self._stop_requested.wait(RX_COALESCE_DELAY_SECONDS)

        current_serial = self._serial
        if current_serial is None:
            return bytes(data)

        with self._io_lock:
            waiting = int(getattr(current_serial, "in_waiting", 0) or 0)
            if waiting > 0:
                data.extend(current_serial.read(waiting))

        return bytes(data)

    def _close_serial(self) -> None:
        current_serial = self._serial
        self._serial = None
        if current_serial is None:
            return

        try:
            if getattr(current_serial, "is_open", True):
                current_serial.close()
        except (OSError, serial.SerialException) as exc:
            if not self._stop_requested.is_set():
                self.error_occurred.emit(f"Failed to close {self.settings.port}: {exc}")
