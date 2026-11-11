"""Bluetooth LE workers: device scanner and Nordic UART Service (NUS) session."""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QObject, QThread, pyqtSignal

try:
    from bleak import BleakClient, BleakScanner
except ImportError:  # bleak is optional at import time; reported when used.
    BleakClient = None  # type: ignore[assignment,misc]
    BleakScanner = None  # type: ignore[assignment,misc]

from settings import BleSettings


# Nordic UART Service. Names are from the peripheral's point of view:
#   RX characteristic: the peripheral receives (we write to it)
#   TX characteristic: the peripheral transmits (we get notifications)
NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
NUS_RX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
NUS_TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

CONNECT_TIMEOUT_SECONDS = 15.0
RX_COALESCE_DELAY_SECONDS = 0.01
DEFAULT_CHUNK_SIZE = 20
BLEAK_MISSING_MESSAGE = "bleak 패키지가 필요합니다. pip install bleak"


class BleScanThread(QThread):
    """Continuously scans for BLE advertisements until stop() is called."""

    device_found = pyqtSignal(str, str, int)  # address, name, rssi
    error_occurred = pyqtSignal(str)

    def __init__(
        self,
        scanner_factory: Callable[..., Any] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._scanner_factory = scanner_factory or BleakScanner
        self._stop_requested = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._async_stop: asyncio.Event | None = None

    def stop(self) -> None:
        self._stop_requested.set()
        loop = self._loop
        async_stop = self._async_stop
        if loop is not None and async_stop is not None:
            try:
                loop.call_soon_threadsafe(async_stop.set)
            except RuntimeError:
                pass  # event loop already closed: the thread has finished

    def run(self) -> None:
        if self._scanner_factory is None:
            self.error_occurred.emit(BLEAK_MISSING_MESSAGE)
            return
        try:
            asyncio.run(self._scan())
        except Exception as exc:
            if not self._stop_requested.is_set():
                self.error_occurred.emit(f"블루투스 스캔 실패: {exc}")

    async def _scan(self) -> None:
        self._async_stop = asyncio.Event()
        self._loop = asyncio.get_running_loop()
        if self._stop_requested.is_set():
            return

        def on_detect(device: Any, advertisement: Any) -> None:
            name = getattr(advertisement, "local_name", None) or device.name or ""
            rssi = getattr(advertisement, "rssi", None)
            self.device_found.emit(
                str(device.address), str(name), int(rssi) if rssi is not None else -127
            )

        async with self._scanner_factory(detection_callback=on_detect):
            await self._async_stop.wait()


class BleWorker(QThread):
    """Background thread that owns one BLE connection using Nordic UART Service.

    Exposes the same interface as SerialWorker so MonitorSubWindow can use either.
    """

    data_received = pyqtSignal(bytes)
    bytes_written = pyqtSignal(int)
    data_written = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    port_opened = pyqtSignal(str)
    port_closed = pyqtSignal(str)

    def __init__(
        self,
        settings: BleSettings,
        client_factory: Callable[..., Any] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = settings
        self._client_factory = client_factory or BleakClient
        self._stop_requested = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._async_stop: asyncio.Event | None = None
        self._write_queue: asyncio.Queue[bytes] | None = None
        self._ready = threading.Event()
        self._rx_buffer = bytearray()
        self._flush_handle: asyncio.TimerHandle | None = None

    # -- public interface (GUI thread) ---------------------------------------

    def stop(self) -> None:
        """Request disconnect. Also cancels a connection attempt in progress."""
        self._stop_requested.set()
        loop = self._loop
        async_stop = self._async_stop
        if loop is not None and async_stop is not None:
            try:
                loop.call_soon_threadsafe(async_stop.set)
            except RuntimeError:
                pass  # event loop already closed: the thread has finished

    def write_data(self, payload: bytes) -> bool:
        """Queue payload for sending. Completion is reported via bytes_written."""
        if not payload:
            return False

        loop = self._loop
        queue = self._write_queue
        if not self._ready.is_set() or loop is None or queue is None:
            self.error_occurred.emit("Cannot send data because Bluetooth is not connected.")
            return False

        try:
            loop.call_soon_threadsafe(queue.put_nowait, bytes(payload))
        except RuntimeError:
            self.error_occurred.emit("Cannot send data because Bluetooth is not connected.")
            return False
        return True

    # -- thread body ----------------------------------------------------------

    def run(self) -> None:
        label = self.settings.port
        if self._client_factory is None:
            self.error_occurred.emit(BLEAK_MISSING_MESSAGE)
            self.port_closed.emit(label)
            return
        try:
            asyncio.run(self._session())
        except Exception as exc:
            if not self._stop_requested.is_set():
                self.error_occurred.emit(f"Bluetooth error: {exc}")
        finally:
            self._ready.clear()
            self.port_closed.emit(label)

    async def _session(self) -> None:
        self._async_stop = asyncio.Event()
        self._write_queue = asyncio.Queue()
        self._loop = asyncio.get_running_loop()
        if self._stop_requested.is_set():
            return

        disconnected = asyncio.Event()
        client = self._client_factory(
            self.settings.address,
            # 일부 백엔드는 다른 스레드에서 콜백을 호출하므로 thread-safe 하게 처리한다.
            disconnected_callback=lambda _client: self._loop.call_soon_threadsafe(
                disconnected.set
            ),
            timeout=CONNECT_TIMEOUT_SECONDS,
        )

        writer_task: asyncio.Future[None] | None = None
        connected = False
        try:
            if not await self._connect(client):
                return
            connected = True

            service = client.services.get_service(NUS_SERVICE_UUID)
            if service is None:
                self.error_occurred.emit(
                    "Nordic UART Service(NUS)를 찾을 수 없습니다. NUS를 지원하는 장치인지 확인하세요."
                )
                return
            rx_char = service.get_characteristic(NUS_RX_CHAR_UUID)
            if rx_char is None or service.get_characteristic(NUS_TX_CHAR_UUID) is None:
                self.error_occurred.emit("NUS RX/TX 특성(characteristic)을 찾을 수 없습니다.")
                return

            await client.start_notify(NUS_TX_CHAR_UUID, self._on_notify)
            writer_task = asyncio.ensure_future(self._writer_loop(client, rx_char))
            self._ready.set()
            self.port_opened.emit(self.settings.port)

            stop_wait = asyncio.ensure_future(self._async_stop.wait())
            lost_wait = asyncio.ensure_future(disconnected.wait())
            done, pending = await asyncio.wait(
                {stop_wait, lost_wait}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)
            if lost_wait in done and not self._stop_requested.is_set():
                self.error_occurred.emit("블루투스 연결이 끊어졌습니다.")
        finally:
            self._ready.clear()
            if writer_task is not None:
                writer_task.cancel()
                await asyncio.gather(writer_task, return_exceptions=True)
            self._flush_rx()
            if connected:
                try:
                    await client.disconnect()
                except Exception as exc:
                    if not self._stop_requested.is_set():
                        self.error_occurred.emit(f"Bluetooth disconnect failed: {exc}")

    async def _connect(self, client: Any) -> bool:
        """Connect, aborting early if stop() is requested. Returns True if connected."""
        assert self._async_stop is not None
        connect_task = asyncio.ensure_future(client.connect())
        stop_task = asyncio.ensure_future(self._async_stop.wait())
        done, _pending = await asyncio.wait(
            {connect_task, stop_task}, return_when=asyncio.FIRST_COMPLETED
        )
        if connect_task not in done:
            connect_task.cancel()
            await asyncio.gather(connect_task, return_exceptions=True)
            return False
        stop_task.cancel()
        await asyncio.gather(stop_task, return_exceptions=True)
        connect_task.result()  # raises on connection failure
        return not self._async_stop.is_set()

    async def _writer_loop(self, client: Any, rx_char: Any) -> None:
        assert self._write_queue is not None
        properties = set(getattr(rx_char, "properties", []) or [])
        with_response = "write" in properties or "write-without-response" not in properties
        while True:
            payload = await self._write_queue.get()
            mtu = int(getattr(client, "mtu_size", 0) or 0)
            chunk_size = max(DEFAULT_CHUNK_SIZE, mtu - 3)
            try:
                for start in range(0, len(payload), chunk_size):
                    await client.write_gatt_char(
                        rx_char, payload[start : start + chunk_size], response=with_response
                    )
            except Exception as exc:
                self.error_occurred.emit(f"Failed to send data over Bluetooth: {exc}")
                continue
            self.bytes_written.emit(len(payload))
            self.data_written.emit(payload)

    # -- RX (runs on the asyncio thread) -------------------------------------

    def _on_notify(self, _characteristic: Any, data: bytearray) -> None:
        self._rx_buffer.extend(data)
        if self._flush_handle is None and self._loop is not None:
            self._flush_handle = self._loop.call_later(
                RX_COALESCE_DELAY_SECONDS, self._flush_rx
            )

    def _flush_rx(self) -> None:
        self._flush_handle = None
        if self._rx_buffer:
            data = bytes(self._rx_buffer)
            self._rx_buffer.clear()
            self.data_received.emit(data)
