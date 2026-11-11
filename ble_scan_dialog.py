"""Bluetooth LE scan UI: a reusable panel and a standalone dialog."""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ble_worker import BleScanThread


class BleScanPanel(QWidget):
    """Filter box + live device list. Scans only between start_scan() and stop_scan()."""

    selection_changed = pyqtSignal(bool)  # True when a device is selected
    device_activated = pyqtSignal()  # device double-clicked

    def __init__(
        self,
        parent: QWidget | None = None,
        scan_thread_factory: Callable[[], BleScanThread] | None = None,
    ) -> None:
        super().__init__(parent)
        self._scan_thread_factory = scan_thread_factory or BleScanThread
        self._scanner: BleScanThread | None = None
        # address -> (name, rssi)
        self._devices: dict[str, tuple[str, int]] = {}
        self._scan_error = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("필터 (장치 이름 또는 주소)")
        self.filter_edit.setClearButtonEnabled(True)
        self.filter_edit.textChanged.connect(self._rebuild_list)
        layout.addWidget(self.filter_edit)

        self.device_list = QListWidget()
        self.device_list.setMinimumHeight(160)
        self.device_list.itemDoubleClicked.connect(lambda _item: self.device_activated.emit())
        self.device_list.currentItemChanged.connect(
            lambda current, _previous: self.selection_changed.emit(current is not None)
        )
        layout.addWidget(self.device_list, 1)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

    # -- public API -----------------------------------------------------------

    @property
    def is_scanning(self) -> bool:
        return self._scanner is not None and self._scanner.isRunning()

    @property
    def selected_device(self) -> tuple[str, str] | None:
        """(address, name) of the selected device, or None."""
        item = self.device_list.currentItem()
        if item is None:
            return None
        return (
            str(item.data(Qt.ItemDataRole.UserRole)),
            str(item.data(Qt.ItemDataRole.UserRole + 1) or ""),
        )

    def start_scan(self) -> None:
        if self.is_scanning:
            return
        self._devices.clear()
        self._scan_error = ""
        self._rebuild_list()

        scanner = self._scan_thread_factory()
        scanner.device_found.connect(self._on_device_found)
        scanner.error_occurred.connect(self._on_scan_error)
        self._scanner = scanner
        scanner.start()
        self._update_status()

    def stop_scan(self) -> None:
        scanner = self._scanner
        if scanner is None:
            return
        scanner.stop()
        scanner.wait(3000)

    # -- scanning -----------------------------------------------------------

    def _on_device_found(self, address: str, name: str, rssi: int) -> None:
        previous = self._devices.get(address)
        # Keep a known name when a later advertisement has none.
        if previous and not name:
            name = previous[0]
        self._devices[address] = (name, rssi)
        self._rebuild_list()

    def _on_scan_error(self, message: str) -> None:
        self._scan_error = message
        self._update_status()

    # -- list ---------------------------------------------------------------

    def _rebuild_list(self) -> None:
        current = self.selected_device
        current_address = current[0] if current else None

        needle = self.filter_edit.text().strip().lower()
        rows = [
            (address, name, rssi)
            for address, (name, rssi) in self._devices.items()
            if not needle or needle in name.lower() or needle in address.lower()
        ]
        # Named devices first, then strongest signal first.
        rows.sort(key=lambda row: (not row[1], -row[2]))

        self.device_list.blockSignals(True)
        self.device_list.clear()
        select_row = -1
        for index, (address, name, rssi) in enumerate(rows):
            item = QListWidgetItem(f"{name or '(이름 없음)'}\n{address}  ·  {rssi} dBm")
            item.setData(Qt.ItemDataRole.UserRole, address)
            item.setData(Qt.ItemDataRole.UserRole + 1, name)
            self.device_list.addItem(item)
            if address == current_address:
                select_row = index
        if select_row >= 0:
            self.device_list.setCurrentRow(select_row)
        self.device_list.blockSignals(False)

        self.selection_changed.emit(self.device_list.currentItem() is not None)
        self._update_status()

    def _update_status(self) -> None:
        if self._scan_error:
            self.status_label.setText(self._scan_error)
        elif self.is_scanning:
            shown = self.device_list.count()
            self.status_label.setText(f"스캔 중... ({shown}/{len(self._devices)}개 장치)")
        else:
            self.status_label.setText("")


class BleScanDialog(QDialog):
    """Standalone scan dialog (toolbar button): scans while open, accepts with a device."""

    def __init__(
        self,
        parent: QWidget | None = None,
        scan_thread_factory: Callable[[], BleScanThread] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("블루투스 스캔")
        self.setModal(True)
        self.setMinimumWidth(360)
        self.resize(360, 420)
        self._selected: tuple[str, str] | None = None

        root = QVBoxLayout(self)
        root.setSpacing(10)

        self.panel = BleScanPanel(self, scan_thread_factory)
        self.panel.device_activated.connect(self._on_connect)
        self.panel.selection_changed.connect(self._update_connect_enabled)
        root.addWidget(self.panel, 1)

        button_box = QDialogButtonBox()
        self.connect_button: QPushButton = button_box.addButton(
            "연결", QDialogButtonBox.ButtonRole.AcceptRole
        )
        button_box.addButton("취소", QDialogButtonBox.ButtonRole.RejectRole)
        button_box.accepted.connect(self._on_connect)
        button_box.rejected.connect(self.reject)
        root.addWidget(button_box)
        self.connect_button.setEnabled(False)

        self.panel.start_scan()

    @property
    def selected_device(self) -> tuple[str, str] | None:
        """(address, name) of the chosen device after the dialog is accepted."""
        return self._selected

    def _update_connect_enabled(self, has_selection: bool) -> None:
        self.connect_button.setEnabled(has_selection)

    def _on_connect(self) -> None:
        device = self.panel.selected_device
        if device is None:
            return
        self._selected = device
        self.accept()

    def done(self, result: int) -> None:
        self.panel.stop_scan()
        super().done(result)
