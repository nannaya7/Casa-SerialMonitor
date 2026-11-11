"""New monitoring session dialog."""

from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ble_scan_dialog import BleScanPanel
from ble_worker import BleScanThread


class NewSessionDialog(QDialog):
    """New monitoring session configuration dialog."""

    SERIAL_TAB = 0
    BLUETOOTH_TAB = 1

    def __init__(
        self,
        ports: list[tuple[str, str]],
        parent: QWidget | None = None,
        scan_thread_factory: Callable[[], BleScanThread] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("New monitoring session")
        self.setModal(True)
        self.setMinimumWidth(312)
        self._selected_port: str | None = None
        self._start_now = True
        self._selected_visualizer = "Dump view"
        self._connection_type = "serial"
        self._selected_device: tuple[str, str] | None = None
        self._scan_thread_factory = scan_thread_factory
        self._build_ui(ports)
        self.resize(312, self.sizeHint().height())

    @property
    def selected_port(self) -> str | None:
        return self._selected_port

    @property
    def start_now(self) -> bool:
        return self._start_now

    @property
    def selected_visualizer(self) -> str:
        return self._selected_visualizer

    @property
    def connection_type(self) -> str:
        """"serial" or "bluetooth", depending on the tab used to accept the dialog."""
        return self._connection_type

    @property
    def selected_device(self) -> tuple[str, str] | None:
        """(address, name) of the chosen Bluetooth device (bluetooth connections)."""
        return self._selected_device

    def _build_ui(self, ports: list[tuple[str, str]]) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_serial_tab(ports), "Serial")
        self.ble_panel = BleScanPanel(scan_thread_factory=self._scan_thread_factory)
        self.ble_panel.device_activated.connect(self._on_accept)
        self.ble_panel.selection_changed.connect(lambda _has: self._update_controls())
        self.tabs.addTab(self.ble_panel, "Bluetooth")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self.tabs)

        self.session_group = QGroupBox("New session options")
        session_layout = QHBoxLayout(self.session_group)
        self.start_now_check = QCheckBox("Start monitoring now")
        self.start_now_check.setChecked(True)
        session_layout.addWidget(self.start_now_check)
        session_layout.addStretch()
        root.addWidget(self.session_group)

        button_box = QDialogButtonBox()
        self.start_button: QPushButton = button_box.addButton(
            "Start monitoring", QDialogButtonBox.ButtonRole.AcceptRole
        )
        button_box.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        root.addWidget(button_box)

    def _build_serial_tab(self, ports: list[tuple[str, str]]) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Choose serial ports for monitoring:"))
        self.port_list = QListWidget()
        self.port_list.setMinimumHeight(160)
        if ports:
            for device, label in ports:
                item = QListWidgetItem(label)
                item.setData(Qt.ItemDataRole.UserRole, device)
                self.port_list.addItem(item)
            self.port_list.setCurrentRow(0)
        else:
            placeholder = QListWidgetItem("No serial ports detected")
            placeholder.setFlags(
                placeholder.flags()
                & ~Qt.ItemFlag.ItemIsSelectable
                & ~Qt.ItemFlag.ItemIsEnabled
            )
            self.port_list.addItem(placeholder)
        # 포트를 더블클릭하면 Start monitoring 버튼을 누른 것과 같이 바로 확정한다.
        self.port_list.itemDoubleClicked.connect(lambda _item: self._on_accept())
        layout.addWidget(self.port_list)
        return page

    def _on_tab_changed(self, index: int) -> None:
        # 블루투스 스캔은 Bluetooth 탭이 보일 때만 수행한다.
        if index == self.BLUETOOTH_TAB:
            self.ble_panel.start_scan()
        else:
            self.ble_panel.stop_scan()
        self._update_controls()

    def _update_controls(self) -> None:
        bluetooth = self.tabs.currentIndex() == self.BLUETOOTH_TAB
        # 블루투스는 항상 바로 연결한다. 장치를 선택해야 시작할 수 있다.
        self.session_group.setEnabled(not bluetooth)
        self.start_button.setEnabled(
            self.ble_panel.selected_device is not None if bluetooth else True
        )

    def _on_accept(self) -> None:
        if self.tabs.currentIndex() == self.BLUETOOTH_TAB:
            device = self.ble_panel.selected_device
            if device is None:
                return
            self._connection_type = "bluetooth"
            self._selected_device = device
            self._start_now = True
        else:
            item = self.port_list.currentItem()
            if item:
                self._selected_port = item.data(Qt.ItemDataRole.UserRole)
            self._start_now = self.start_now_check.isChecked()
        self.accept()

    def done(self, result: int) -> None:
        self.ble_panel.stop_scan()
        super().done(result)
