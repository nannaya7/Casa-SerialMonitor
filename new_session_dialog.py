"""New monitoring session dialog."""

from __future__ import annotations

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
    QVBoxLayout,
    QWidget,
)


class NewSessionDialog(QDialog):
    """New monitoring session configuration dialog."""

    def __init__(self, ports: list[tuple[str, str]], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New monitoring session")
        self.setModal(True)
        self.setMinimumWidth(312)
        self._selected_port: str | None = None
        self._start_now = True
        self._selected_visualizer = "Dump view"
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

    def _build_ui(self, ports: list[tuple[str, str]]) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(16)

        port_col = QVBoxLayout()
        port_col.addWidget(QLabel("Choose serial ports for monitoring:"))
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
        port_col.addWidget(self.port_list)
        top.addLayout(port_col, 1)

        root.addLayout(top)


        session_group = QGroupBox("New session options")
        session_layout = QHBoxLayout(session_group)
        self.start_now_check = QCheckBox("Start monitoring now")
        self.start_now_check.setChecked(True)
        session_layout.addWidget(self.start_now_check)
        session_layout.addStretch()
        root.addWidget(session_group)

        button_box = QDialogButtonBox()
        button_box.addButton("Start monitoring", QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        root.addWidget(button_box)

    def _on_accept(self) -> None:
        item = self.port_list.currentItem()
        if item:
            self._selected_port = item.data(Qt.ItemDataRole.UserRole)
        self._start_now = self.start_now_check.isChecked()
        self.accept()
