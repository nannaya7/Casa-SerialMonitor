"""Main application window for CasaSerial."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
from urllib.parse import quote

from PyQt6 import uic
from PyQt6.QtCore import QPoint, QRegularExpression, QSettings, QSize, QTimer, Qt
from PyQt6.QtGui import (
    QAction,
    QCloseEvent,
    QColor,
    QIcon,
    QKeySequence,
    QRegularExpressionValidator,
)
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMdiSubWindow,
    QPushButton,
    QSizePolicy,
    QWidget,
)
import serial
from serial.tools import list_ports

from app_resources import (
    APP_NAME,
    BUTTONS_RELATIVE_PATH,
    ICON_RELATIVE_PATH,
    MAIN_WINDOW_UI_RELATIVE_PATH,
    resource_path,
)
from ble_scan_dialog import BleScanDialog
from monitor_subwindow import MonitorSubWindow
from new_session_dialog import NewSessionDialog
from settings import BleSettings, SerialSettings


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class CasaSerialWindow(QMainWindow):
    """Main window for the cross-platform serial monitor."""

    def __init__(self) -> None:
        super().__init__()
        self._known_port_devices: tuple[str, ...] = ()
        self.last_settings_error = ""
        self._send_format = "String"
        self._cmd_panel_expanded = True
        self._cmd_panel_saved_width = 300

        self._load_main_window_ui()
        self._initialize_loaded_ui()
        self._create_status_bar()
        self._create_loop_send_timer()

        self.new_session_action.triggered.connect(self._open_new_session_dialog)
        self.close_session_action = QAction("세션 닫기", self)
        self.close_session_action.setShortcut(QKeySequence("Ctrl+W"))
        self.close_session_action.triggered.connect(self.mdi_area.closeActiveSubWindow)
        self.session_menu.addAction(self.close_session_action)
        self.save_action.triggered.connect(self._save_active_received_data)
        self.refresh_ports_action.triggered.connect(
            lambda: self.refresh_ports(show_status=True, force=True)
        )
        self.open_button.clicked.connect(self._toggle_serial_connection)
        self.open_action.triggered.connect(self._open_saved_received_data)
        self.send_button.clicked.connect(self._send_current_command)
        self.command_input.returnPressed.connect(self._send_current_command)
        self.loop_checkbox.toggled.connect(self._handle_loop_checkbox_toggled)
        self.start_loop_button.clicked.connect(self._toggle_loop_sending)
        self.erase_action.triggered.connect(self._clear_active_log)
        self.log_format_combo.currentTextChanged.connect(self._on_log_format_changed)
        self.timestamp_checkbox.toggled.connect(self._on_timestamp_changed)
        self.mdi_area.subWindowActivated.connect(self._on_active_subwindow_changed)
        self.format_group.buttonToggled.connect(
            lambda _btn, checked: self._on_send_format_changed() if checked else None
        )
        self.command_input.textChanged.connect(self._auto_format_command_input)
        self._on_send_format_changed()

        self.refresh_ports(show_status=True)

    def _load_main_window_ui(self) -> None:
        """Load the Qt Designer layout and bind named widgets to this window."""
        uic.loadUi(str(resource_path(MAIN_WINDOW_UI_RELATIVE_PATH)), self)
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(resource_path(ICON_RELATIVE_PATH))))

    def _initialize_loaded_ui(self) -> None:
        """Rebuild runtime-only relationships that are not represented in .ui."""
        self.mdi_area.setBackground(QColor("#fffdf9"))
        self.mdi_area.viewport().setStyleSheet("background: #fffdf9;")
        self.h_splitter.setStretchFactor(0, 1)
        self.h_splitter.setStretchFactor(1, 0)
        self.h_splitter.setSizes([700, 300])
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setSizes([500, 279])
        self.cmd_toggle_btn.setText("\u25b6")
        self.main_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolbar_spacer = getattr(self, "toolbar_spacer", None) or QWidget(self.main_toolbar)
        self.toolbar_spacer.setObjectName("toolbar_spacer")
        self.toolbar_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        self.main_toolbar.removeAction(self.refresh_ports_action)
        self.main_toolbar.addWidget(self.toolbar_spacer)

        for action, icon_name in (
            (self.new_session_action, "new"),
            (self.open_action, "open"),
            (self.save_action, "save"),
            (self.start_action, "start"),
            (self.pause_action, "pause"),
            (self.stop_action, "stop"),
            (self.erase_action, "erase"),
        ):
            action.setIcon(QIcon(str(resource_path(BUTTONS_RELATIVE_PATH / f"{icon_name}.png"))))
        self.refresh_ports_action.setIcon(
            QIcon(str(resource_path(BUTTONS_RELATIVE_PATH / "reload.png")))
        )
        self.refresh_ports_button = QPushButton(self.main_toolbar)
        self.refresh_ports_button.setObjectName("refresh_ports_button")
        self.refresh_ports_button.setFixedSize(138, 58)
        self.refresh_ports_button.setText("")
        self.refresh_ports_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_ports_button.clicked.connect(
            lambda: self.refresh_ports(show_status=True, force=True)
        )
        self.refresh_ports_button.setStyleSheet(
            f"""
            QPushButton#refresh_ports_button {{
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
                border-image: url("{resource_path(BUTTONS_RELATIVE_PATH / "reload.png").as_posix()}") 0 0 0 0 stretch stretch;
            }}
            QPushButton#refresh_ports_button:disabled {{
                opacity: 0.45;
            }}
            """
        )
        self.main_toolbar.addWidget(self.refresh_ports_button)

        self.ble_button = QPushButton("블루투스 스캔", self.main_toolbar)
        self.ble_button.setObjectName("ble_button")
        self.ble_button.setFixedSize(150, 58)
        self.ble_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ble_button.setStyleSheet(
            """
            QPushButton#ble_button {
                color: #3a2b1f;
                background: #fffefa;
                border: 1px solid #e6d9cc;
                border-radius: 14px;
                padding: 0 12px;
            }
            QPushButton#ble_button:hover {
                background: #f3e7da;
                border-color: #d9c1aa;
            }
            QPushButton#ble_button:pressed {
                background: #ead8c4;
            }
            """
        )
        self.ble_button.clicked.connect(self._on_ble_button_clicked)
        self.main_toolbar.addWidget(self.ble_button)

        for combo in (
            self.port_combo,
            self.baudrate_combo,
            self.databits_combo,
            self.parity_combo,
            self.flow_control_combo,
            self.stopbits_combo,
        ):
            combo.setFixedHeight(32)
        self.baudrate_combo.setCurrentText("115200")
        self.databits_combo.setCurrentText("8")
        self.command_input.setFixedHeight(34)
        self.loop_interval_spin.setFixedSize(132, 34)
        self.log_format_combo.setFixedWidth(132)
        self.save_action.setEnabled(False)
        self.erase_action.setEnabled(False)
        self.string_radio.setMinimumWidth(92)
        for radio in (
            self.hex_radio,
            self.dec_radio,
            self.oct_radio,
            self.bin_radio,
        ):
            radio.setMinimumWidth(72)

        self._apply_image_button(
            self.open_button,
            "connect",
            QSize(158, 101),
            QSize(158, 75),
            "연결 열기",
        )
        self._apply_image_button(
            self.send_button,
            "transfer",
            QSize(74, 41),
            QSize(74, 41),
            "전송",
        )
        self._apply_image_button(
            self.start_loop_button,
            "start_repeat",
            QSize(74, 41),
            QSize(74, 41),
            "반복 전송 시작",
        )

        self.format_group = QButtonGroup(self)
        self.format_group.setExclusive(True)
        for radio in (
            self.string_radio,
            self.hex_radio,
            self.dec_radio,
            self.oct_radio,
            self.bin_radio,
        ):
            self.format_group.addButton(radio)

        self._build_ble_status_label()

        self._cmd_grid = self.cmd_grid
        self._cmd_add_btn = self.cmd_add_btn
        self._cmd_remove_btn = self.cmd_remove_btn
        pm_btn_style = """
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
            }
        """
        for button, name, tooltip in (
            (self._cmd_add_btn, "plus", "추가"),
            (self._cmd_remove_btn, "minus", "삭제"),
        ):
            button.setToolTip(tooltip)
            button.setAccessibleName(tooltip)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFixedSize(67, 38)
            button.setIconSize(QSize(67, 38))
            button.setIcon(QIcon(str(resource_path(BUTTONS_RELATIVE_PATH / f"{name}.png"))))
            button.setStyleSheet(pm_btn_style)
        self._cmd_add_btn.clicked.connect(self._add_cmd_row)
        self._cmd_remove_btn.clicked.connect(self._remove_cmd_row)
        self.cmd_toggle_btn.clicked.connect(self._toggle_cmd_panel)

        self._cmd_formatting = False
        self._cmd_key: str | None = None  # CMD 전송 데이터를 저장 중인 연결 대상(포트/장치) 키
        self._cmd_entries: list[tuple[QLineEdit, QCheckBox, QCheckBox]] = []
        self._cmd_buttons: list[QPushButton] = []
        for i in range(10):
            btn = getattr(self, f"cmd_button_{i:02d}")
            inp = getattr(self, f"cmd_input_{i:02d}")
            bin_cb = getattr(self, f"cmd_bin_{i:02d}")
            crlf_cb = getattr(self, f"cmd_crlf_{i:02d}")
            btn.setStyleSheet(self._CMD_BTN_STYLE)
            btn.setToolTip(f"{i:02d}번 전송 데이터 보내기")
            inp.setMinimumHeight(34)
            btn.clicked.connect(lambda _checked=False, idx=i: self._send_cmd(idx))
            bin_cb.toggled.connect(
                lambda checked, idx=i: self._on_cmd_hex_toggled(idx, checked)
            )
            inp.textChanged.connect(
                lambda text, idx=i: self._on_cmd_text_changed(idx, text)
            )
            self._cmd_buttons.append(btn)
            self._cmd_entries.append((inp, bin_cb, crlf_cb))
        self._update_cmd_pm_buttons()
        self._sync_ble_button()

    def _build_ble_status_label(self) -> None:
        """'전송 설정' 제목 옆에 블루투스 연결 상태 라벨을 둔다."""
        self.ble_status_label = QLabel("", self.send_panel)
        self.ble_status_label.setObjectName("ble_status_label")
        self.ble_status_label.setStyleSheet(
            "color: #8a5d33; font-size: 10pt; min-height: 26px; max-height: 26px;"
        )
        self.ble_status_label.hide()

        self.send_panel_layout.removeWidget(self.panel_title)
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(14)
        title_row.addWidget(self.panel_title)
        title_row.addWidget(self.ble_status_label)
        title_row.addStretch(1)
        self.send_panel_layout.insertLayout(0, title_row)

    # -- shared UI helpers ---------------------------------------------------

    def _apply_image_button(
        self,
        button: QPushButton,
        image_name: str,
        button_size: QSize,
        icon_size: QSize,
        tooltip: str,
    ) -> None:
        button.setText("")
        button.setToolTip(tooltip)
        button.setAccessibleName(tooltip)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                border: none;
                padding: 0;
                min-width: {button_size.width()}px;
                max-width: {button_size.width()}px;
                min-height: {button_size.height()}px;
                max-height: {button_size.height()}px;
            }}
            """
        )
        button.setFixedSize(button_size)
        button.setIconSize(icon_size)
        button.setIcon(QIcon(str(resource_path(BUTTONS_RELATIVE_PATH / f"{image_name}.png"))))

    def _set_open_button_mode(self, connected: bool) -> None:
        if connected:
            image_name = "disconnect"
            tooltip = "연결 닫기"
        else:
            image_name = "connect"
            tooltip = "연결 열기"

        self.open_button.setToolTip(tooltip)
        self.open_button.setAccessibleName(tooltip)
        self.open_button.setIcon(
            QIcon(str(resource_path(BUTTONS_RELATIVE_PATH / f"{image_name}.png")))
        )

    # -- command quick-send panel ------------------------------------------

    _CMD_BTN_STYLE = """
        QPushButton {
            color: #3a2b1f;
            font-weight: 400;
            background: #f3e7da;
            border: 1px solid #d9c1aa;
            border-radius: 8px;
            padding: 2px 8px;
            min-height: 32px;
        }
        QPushButton:hover {
            background: #ead8c4;
            border-color: #b98552;
            color: #6b4423;
        }
        QPushButton:pressed {
            background: #d9bfa3;
            border-color: #a87443;
            padding-top: 4px;
            padding-bottom: 0;
        }
        QPushButton:disabled {
            color: #a89886;
            background: #f7f1ea;
            border-color: #e6d9cc;
        }
    """

    def _append_cmd_row(self, i: int) -> None:
        r = i + 1
        btn = QPushButton("SEND", self.cmd_content)
        btn.setFlat(True)
        btn.setStyleSheet(self._CMD_BTN_STYLE)
        btn.setToolTip(f"{i:02d}번 전송 데이터 보내기")
        btn.clicked.connect(lambda _, idx=i: self._send_cmd(idx))
        inp = QLineEdit(self.cmd_content)
        inp.setMinimumHeight(34)
        bin_cb = QCheckBox(self.cmd_content)
        crlf_cb = QCheckBox(self.cmd_content)
        bin_cb.toggled.connect(lambda checked, idx=i: self._on_cmd_hex_toggled(idx, checked))
        inp.textChanged.connect(lambda text, idx=i: self._on_cmd_text_changed(idx, text))
        self._cmd_grid.addWidget(btn, r, 0)
        self._cmd_grid.addWidget(inp, r, 1)
        self._cmd_grid.addWidget(bin_cb, r, 2, Qt.AlignmentFlag.AlignCenter)
        self._cmd_grid.addWidget(crlf_cb, r, 3, Qt.AlignmentFlag.AlignCenter)
        self._cmd_buttons.append(btn)
        self._cmd_entries.append((inp, bin_cb, crlf_cb))

    def _add_cmd_row(self) -> None:
        if len(self._cmd_entries) >= 20:
            return
        self._append_cmd_row(len(self._cmd_entries))
        self._update_cmd_pm_buttons()

    def _remove_cmd_row(self) -> None:
        if len(self._cmd_entries) <= 1:
            return
        inp, bin_cb, crlf_cb = self._cmd_entries.pop()
        btn = self._cmd_buttons.pop()
        for w in (btn, inp, bin_cb, crlf_cb):
            self._cmd_grid.removeWidget(w)
            w.deleteLater()
        self._update_cmd_pm_buttons()

    def _update_cmd_pm_buttons(self) -> None:
        count = len(self._cmd_entries)
        self._cmd_add_btn.setEnabled(count < 20)
        self._cmd_remove_btn.setEnabled(count > 1)

    def _toggle_cmd_panel(self) -> None:
        sizes = self.h_splitter.sizes()
        total = sum(sizes)
        if total == 0:
            return
        if self._cmd_panel_expanded:
            self._cmd_panel_saved_width = max(sizes[1], 200)
            self.h_splitter.setSizes([total - 18, 18])
            self.cmd_toggle_btn.setText("\u25c0")
            self._cmd_panel_expanded = False
        else:
            restore = self._cmd_panel_saved_width
            self.h_splitter.setSizes([total - restore, restore])
            self.cmd_toggle_btn.setText("\u25b6")
            self._cmd_panel_expanded = True

    def _on_cmd_hex_toggled(self, idx: int, checked: bool) -> None:
        if self._cmd_formatting or idx >= len(self._cmd_entries):
            return

        inp, _hex_cb, _crlf_cb = self._cmd_entries[idx]
        current = inp.text()
        self._cmd_formatting = True
        try:
            if checked:
                converted = self._cmd_text_to_hex(current)
                inp.setValidator(
                    QRegularExpressionValidator(QRegularExpression(r"[0-9A-Fa-f ]*"), inp)
                )
                inp.setText(converted)
                inp.setCursorPosition(len(converted))
            else:
                converted = self._cmd_hex_to_text(current)
                inp.setValidator(None)
                inp.setText(converted)
                inp.setCursorPosition(len(converted))
        finally:
            self._cmd_formatting = False

    def _on_cmd_text_changed(self, idx: int, text: str) -> None:
        if self._cmd_formatting or idx >= len(self._cmd_entries):
            return

        inp, hex_cb, _crlf_cb = self._cmd_entries[idx]
        if not hex_cb.isChecked():
            return

        formatted = self._group_hex_text(text)
        if formatted == text:
            return

        old_cursor = inp.cursorPosition()
        non_space_before = len(text[:old_cursor].replace(" ", ""))

        self._cmd_formatting = True
        try:
            inp.setText(formatted)
            inp.setCursorPosition(self._cursor_for_grouped_text(formatted, non_space_before))
        finally:
            self._cmd_formatting = False

    @staticmethod
    def _cmd_text_to_hex(text: str) -> str:
        return " ".join(f"{byte:02X}" for byte in text.encode("utf-8"))

    @staticmethod
    def _cmd_hex_to_text(text: str) -> str:
        compact = text.replace(" ", "")
        if not compact:
            return ""
        if len(compact) % 2:
            compact = compact[:-1]
        if not compact:
            return ""
        try:
            return bytes.fromhex(compact).decode("utf-8", errors="replace")
        except ValueError:
            return ""

    @staticmethod
    def _group_hex_text(text: str) -> str:
        compact = text.replace(" ", "").upper()
        return " ".join(compact[i:i + 2] for i in range(0, len(compact), 2))

    @staticmethod
    def _cursor_for_grouped_text(text: str, non_space_before: int) -> int:
        if non_space_before <= 0:
            return 0
        count = 0
        for index, char in enumerate(text):
            if char == " ":
                continue
            count += 1
            if count == non_space_before:
                return index + 1
        return len(text)

    # -- command entry persistence -----------------------------------------

    @staticmethod
    def _app_settings() -> QSettings:
        return QSettings("CasaSerial", "CasaSerial")

    @staticmethod
    def _cmd_settings_group(key: str) -> str:
        # 포트 경로(/dev/cu...)나 장치 이름에 들어 있는 '/' 등이 설정 경로로 해석되지 않게 인코딩한다.
        return "cmd_targets/" + quote(key, safe="")

    def _save_cmd_entries(self) -> None:
        """Save the CMD panel under the current connection target (no-op without one)."""
        if self._cmd_key is None:
            return
        settings = self._app_settings()
        settings.beginWriteArray(self._cmd_settings_group(self._cmd_key))
        for i, (inp, hex_cb, crlf_cb) in enumerate(self._cmd_entries):
            settings.setArrayIndex(i)
            settings.setValue("text", inp.text())
            settings.setValue("hex", hex_cb.isChecked())
            settings.setValue("crlf", crlf_cb.isChecked())
        settings.endArray()
        settings.sync()

    def _load_cmd_entries(self, key: str) -> None:
        """Show the CMD data saved for `key`; a target with nothing saved starts blank."""
        settings = self._app_settings()
        count = settings.beginReadArray(self._cmd_settings_group(key))
        rows = []
        for i in range(count):
            settings.setArrayIndex(i)
            rows.append(
                (
                    str(settings.value("text", "")),
                    settings.value("hex", False, type=bool),
                    settings.value("crlf", False, type=bool),
                )
            )
        settings.endArray()
        self._apply_cmd_rows(rows)

    def _apply_cmd_rows(self, rows: list[tuple[str, bool, bool]]) -> None:
        wanted = max(1, min(len(rows), 20)) if rows else 10
        while len(self._cmd_entries) < wanted:
            self._append_cmd_row(len(self._cmd_entries))
        while len(self._cmd_entries) > wanted:
            self._remove_cmd_row()
        self._update_cmd_pm_buttons()

        self._cmd_formatting = True
        try:
            for index, (inp, hex_cb, crlf_cb) in enumerate(self._cmd_entries):
                text, is_hex, is_crlf = rows[index] if index < len(rows) else ("", False, False)
                if is_hex:
                    inp.setValidator(
                        QRegularExpressionValidator(
                            QRegularExpression(r"[0-9A-Fa-f ]*"), inp
                        )
                    )
                else:
                    inp.setValidator(None)
                inp.setText(text)
                hex_cb.setChecked(is_hex)
                crlf_cb.setChecked(is_crlf)
        finally:
            self._cmd_formatting = False

    def _sync_cmd_target(self) -> None:
        """Switch the CMD panel to the active session's connection target."""
        sub = self._active_subwindow()
        key = sub.cmd_key if sub is not None else None
        if key is None or key == self._cmd_key:
            return
        self._save_cmd_entries()  # 이전 대상의 내용을 먼저 저장
        self._cmd_key = key
        self._load_cmd_entries(key)

    def _send_cmd(self, idx: int) -> None:
        inp, bin_cb, crlf_cb = self._cmd_entries[idx]
        text = inp.text().strip()
        if not text:
            return

        sub = self._active_subwindow()
        if sub is None or not sub.is_connected:
            self._show_send_error("연결된 세션이 없습니다.")
            return

        if bin_cb.isChecked():
            try:
                payload = bytes.fromhex(text.replace(" ", ""))
            except ValueError:
                self._show_send_error(f"SEND {idx:02d}: 올바른 HEX 값이 아닙니다.")
                return
        else:
            payload = text.encode("utf-8")

        if crlf_cb.isChecked():
            payload += b"\r\n"

        if sub.write_data(payload):
            sub.append_log("TX", self._format_payload_for_log(payload))
            self._save_cmd_entries()

    def _create_status_bar(self) -> None:
        status_bar = self.statusBar()
        status_bar.showMessage("준비")
        status_bar.setStyleSheet(
            """
            QStatusBar {
                background: #fffdf9;
                color: #635242;
                border-top: 1px solid #eee5da;
                padding: 7px 20px;
            }
            QStatusBar QLabel {
                color: #635242;
                padding: 0 10px;
            }
            """
        )

        self.connection_status_label = QLabel("연결 해제됨", self)
        self.port_status_label = QLabel("포트: -", self)
        self.rx_status_label = QLabel("RX: 0 bytes", self)
        self.tx_status_label = QLabel("TX: 0 bytes", self)

        for label in (
            self.connection_status_label,
            self.port_status_label,
            self.rx_status_label,
            self.tx_status_label,
        ):
            status_bar.addPermanentWidget(label)

    def _create_loop_send_timer(self) -> None:
        self.loop_send_timer = QTimer(self)
        self.loop_send_timer.setObjectName("loop_send_timer")
        self.loop_send_timer.timeout.connect(self._send_loop_command)

    # -- port scan ----------------------------------------------------------

    def refresh_ports(self, show_status: bool = True, force: bool = False) -> None:
        previous_port = self.port_combo.currentData()
        active_port = self._active_serial_port()

        try:
            ports = sorted(
                list_ports.comports(),
                key=lambda p: self._port_sort_key(p.device),
            )
        except Exception as exc:
            self._known_port_devices = ()
            self.port_combo.clear()
            self.port_combo.addItem("no serial ports detected", None)
            self._sync_open_button_with_port_state()
            self.port_status_label.setText(f"Port: {active_port}" if active_port else "Port: -")
            if show_status:
                self.statusBar().showMessage(f"Port scan failed: {exc}", 5000)
            return

        current_devices = tuple(p.device for p in ports)
        if not force and current_devices == self._known_port_devices:
            return

        self._known_port_devices = current_devices
        self.port_combo.clear()

        if not ports:
            self.port_combo.addItem("no serial ports detected", None)
            self._sync_open_button_with_port_state()
            self.port_status_label.setText(f"Port: {active_port}" if active_port else "Port: -")
            if show_status or previous_port is not None:
                self.statusBar().showMessage("No serial ports detected", 3000)
            return

        selected_index = 0
        for index, port in enumerate(ports):
            label = self._format_port_label(port)
            self.port_combo.addItem(label, port.device)
            if port.device == previous_port:
                selected_index = index

        self.port_combo.setCurrentIndex(selected_index)
        self._sync_open_button_with_port_state()
        self.port_status_label.setText(f"Port: {active_port or self.port_combo.currentData()}")
        if show_status or previous_port != self.port_combo.currentData():
            self.statusBar().showMessage(f"{len(ports)} serial port(s) detected", 3000)

    @staticmethod
    def _format_port_label(port: object) -> str:
        device = getattr(port, "device", "")
        description = getattr(port, "description", "")
        if description and description != "n/a":
            return f"{device} - {description}"
        return str(device)

    @staticmethod
    def _port_sort_key(device: str) -> tuple[str, int | str]:
        match = re.fullmatch(r"COM(\d+)", device.upper())
        if match:
            return ("COM", int(match.group(1)))
        return ("", device)

    # -- active subwindow access --------------------------------------------

    def _active_subwindow(self) -> MonitorSubWindow | None:
        sub = self.mdi_area.activeSubWindow()
        return sub if isinstance(sub, MonitorSubWindow) else None

    def _active_serial_port(self) -> str | None:
        sub = self._active_subwindow()
        if sub and sub.current_settings:
            return sub.current_settings.port
        return None

    # -- subwindow state callbacks ------------------------------------------

    def _on_active_subwindow_changed(self, sub: QMdiSubWindow | None) -> None:
        self._sync_cmd_target()
        if not isinstance(sub, MonitorSubWindow):
            self._set_connection_controls_enabled(True)
            self.connection_status_label.setText("연결 해제됨")
            self.port_status_label.setText("포트: -")
            self.rx_status_label.setText("RX: 0 bytes")
            self.tx_status_label.setText("TX: 0 bytes")
            self._set_open_button_mode(False)
            self._sync_open_button_with_port_state()
            self.send_button.setEnabled(False)
            self.save_action.setEnabled(False)
            self.erase_action.setEnabled(False)
            self._sync_loop_button_state()
            return
        self._refresh_ui_from_subwindow(sub)

    def _on_subwindow_state_changed(self, sub: MonitorSubWindow) -> None:
        if sub is not self._active_subwindow():
            return
        self._sync_cmd_target()
        self._refresh_ui_from_subwindow(sub)

    def _on_subwindow_error(self, sub: MonitorSubWindow, message: str) -> None:
        if sub is not self._active_subwindow():
            return
        self.statusBar().showMessage(message, 5000)
        if self.loop_send_timer.isActive():
            self._stop_loop_sending()

    def _on_subwindow_bytes_sent(self, sub: MonitorSubWindow, count: int) -> None:
        if sub is not self._active_subwindow():
            return
        self.statusBar().showMessage(f"Sent {count} byte(s)", 2000)

    def _refresh_ui_from_subwindow(self, sub: MonitorSubWindow) -> None:
        connected = sub.is_connected
        settings = sub.current_settings

        self.rx_status_label.setText(f"RX: {sub.rx_bytes} bytes")
        self.tx_status_label.setText(f"TX: {sub.tx_bytes} bytes")
        self.save_action.setEnabled(sub.rx_bytes > 0)
        self.erase_action.setEnabled(sub.rx_bytes > 0)

        if connected:
            self.connection_status_label.setText("연결됨")
            port = settings.port if settings else "-"
            self.port_status_label.setText(f"포트: {port}")
            self._set_open_button_mode(True)
            self.open_button.setEnabled(True)
            self.send_button.setEnabled(not self.loop_send_timer.isActive())
            self._set_connection_controls_enabled(False)
        else:
            self.connection_status_label.setText("연결 해제됨")
            port = settings.port if settings else (self.port_combo.currentData() or "-")
            self.port_status_label.setText(f"포트: {port}")
            self._set_open_button_mode(False)
            self._sync_open_button_with_port_state()
            self.send_button.setEnabled(False)
            self._set_connection_controls_enabled(True)
            if self.loop_send_timer.isActive():
                self._stop_loop_sending()

        self._sync_loop_button_state()

    # -- save / open received data -----------------------------------------

    def _save_active_received_data(self) -> None:
        sub = self._active_subwindow()
        if sub is None or not sub.received_data:
            self.statusBar().showMessage("저장할 수신 데이터가 없습니다.", 4000)
            return

        default_name = datetime.now().strftime("%Y-%m%d-%H%M-%S.cas")
        path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "수신 데이터 저장",
            str(Path.cwd() / default_name),
            "CasaSerial logs (*.cas);;Text files (*.txt);;All files (*)",
        )
        if not path:
            return
        save_path = Path(path)
        if not save_path.suffix:
            save_path = save_path.with_suffix(".cas")

        try:
            save_path.write_text(self._format_hex_file(sub.received_data), encoding="utf-8")
        except OSError as exc:
            self.statusBar().showMessage(f"저장 실패: {exc}", 5000)
            return

        self.statusBar().showMessage(f"저장 완료: {save_path}", 5000)

    def _open_saved_received_data(self) -> None:
        path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "수신 데이터 열기",
            str(Path.cwd()),
            "CasaSerial logs (*.cas);;Text files (*.txt);;All files (*)",
        )
        if not path:
            return

        try:
            raw_text = Path(path).read_text(encoding="utf-8")
            data = self._parse_hex_file(raw_text)
        except (OSError, ValueError) as exc:
            self.statusBar().showMessage(f"열기 실패: {exc}", 5000)
            return

        target = self._window_for_new_session()
        sub = target._create_monitor_subwindow(Path(path).name, dump_mode=False)
        sub.load_received_data(data, title=Path(path).name)
        target.statusBar().showMessage(f"열기 완료: {path}", 5000)

    @staticmethod
    def _format_hex_file(data: bytes) -> str:
        if not data:
            return ""
        lines = []
        for offset in range(0, len(data), 16):
            chunk = data[offset:offset + 16]
            lines.append(" ".join(f"{byte:02X}" for byte in chunk))
        return "\n".join(lines) + "\n"

    @staticmethod
    def _parse_hex_file(text: str) -> bytes:
        cleaned = re.sub(r"[^0-9A-Fa-f]", "", text)
        if not cleaned:
            return b""
        if len(cleaned) % 2:
            raise ValueError("HEX 데이터 길이가 올바르지 않습니다.")
        try:
            return bytes.fromhex(cleaned)
        except ValueError as exc:
            raise ValueError("HEX 데이터 형식이 올바르지 않습니다.") from exc

    # -- New Session dialog / subwindow creation ----------------------------

    def _create_monitor_subwindow(
        self, title: str, dump_mode: bool, cmd_key: str | None = None
    ) -> MonitorSubWindow:
        sub = MonitorSubWindow(title, dump_mode=dump_mode, parent=self)
        sub.initial_cmd_key = cmd_key
        sub.log_format = self.log_format_combo.currentText()
        sub.timestamp_enabled = self.timestamp_checkbox.isChecked()
        sub.state_changed.connect(self._on_subwindow_state_changed)
        sub.state_changed.connect(lambda _sub: self._sync_ble_button())
        sub.destroyed.connect(lambda *_: QTimer.singleShot(0, self._sync_ble_button))
        sub.error_occurred.connect(self._on_subwindow_error)
        sub.bytes_sent.connect(self._on_subwindow_bytes_sent)

        self.mdi_area.addSubWindow(sub)
        sub.showMaximized()  # 세션은 항상 창을 꽉 채워서 연다.
        self.mdi_area.setActiveSubWindow(sub)
        return sub

    # -- separate top-level windows -----------------------------------------

    # 새로 띄운 별도 창이 가비지 컬렉션 되지 않도록 참조를 유지한다.
    _extra_windows: list["CasaSerialWindow"] = []

    def _window_for_new_session(self) -> "CasaSerialWindow":
        """Window that should host a new session.

        This window if it has no session yet; otherwise a new separate top-level window.
        """
        if not self.mdi_area.subWindowList():
            return self

        window = CasaSerialWindow()
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        CasaSerialWindow._extra_windows.append(window)
        window.destroyed.connect(
            lambda *_a, w=window: (
                CasaSerialWindow._extra_windows.remove(w)
                if w in CasaSerialWindow._extra_windows
                else None
            )
        )
        window.resize(self.size())
        window.move(self.pos() + QPoint(40, 40))
        window.show()
        return window

    # -- Bluetooth (Nordic UART Service) ------------------------------------

    def _connected_ble_subwindows(self) -> list[MonitorSubWindow]:
        return [
            sub
            for sub in self.mdi_area.subWindowList()
            if isinstance(sub, MonitorSubWindow) and sub.is_ble and sub.is_connected
        ]

    def _sync_ble_button(self) -> None:
        connected = bool(self._connected_ble_subwindows())
        self.ble_button.setText("블루투스 연결종료" if connected else "블루투스 스캔")

    def _on_ble_button_clicked(self) -> None:
        connected = self._connected_ble_subwindows()
        if connected:
            for sub in connected:
                sub.stop(wait=False)
            self.statusBar().showMessage("블루투스 연결을 종료하는 중...", 3000)
            return
        self._open_ble_scan_dialog()

    def _open_ble_scan_dialog(self) -> None:
        dialog = BleScanDialog(parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected = dialog.selected_device
        if selected is None:
            return

        self._window_for_new_session()._start_ble_session(*selected)

    def _start_ble_session(self, address: str, name: str) -> None:
        settings = BleSettings(address=address, name=name)
        sub = self._create_monitor_subwindow(
            settings.port, dump_mode=True, cmd_key=settings.cmd_key
        )
        self._start_subwindow_connection(sub, ble_settings=settings)

    def _open_new_session_dialog(self) -> None:
        ports: list[tuple[str, str]] = []
        for i in range(self.port_combo.count()):
            device = self.port_combo.itemData(i)
            if device:
                ports.append((device, self.port_combo.itemText(i)))

        dialog = NewSessionDialog(ports, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        if dialog.connection_type == "bluetooth":
            device = dialog.selected_device
            if device is not None:
                self._window_for_new_session()._start_ble_session(*device)
            return

        selected_port = dialog.selected_port
        if not selected_port:
            return

        self._window_for_new_session()._start_serial_session(
            selected_port,
            dump_mode=dialog.selected_visualizer == "Dump view",
            start_now=dialog.start_now,
        )

    def _start_serial_session(self, selected_port: str, dump_mode: bool, start_now: bool) -> None:
        # Update port combo to selected port
        for i in range(self.port_combo.count()):
            if self.port_combo.itemData(i) == selected_port:
                self.port_combo.setCurrentIndex(i)
                break

        # Build title and create subwindow
        port_label = self.port_combo.currentText()
        sub = self._create_monitor_subwindow(
            port_label, dump_mode, cmd_key=f"serial:{selected_port}"
        )

        if start_now:
            settings = self.current_serial_settings()
            if settings:
                sub.start(settings)
                self._set_connection_controls_enabled(False)
                self.statusBar().showMessage(f"{settings.port} 연결 중...", 3000)

    # -- serial connection (Open/Close button) ------------------------------

    def _toggle_serial_connection(self) -> None:
        sub = self._active_subwindow()
        if sub is None:
            self.statusBar().showMessage(
                "NEW 버튼으로 새 모니터링 세션을 먼저 만들어주세요.", 4000
            )
            return

        if sub.is_connected:
            self._stop_subwindow_connection(sub, wait=False)
        else:
            self._start_subwindow_connection(sub)

    def _start_subwindow_connection(
        self, sub: MonitorSubWindow, ble_settings: BleSettings | None = None
    ) -> None:
        if ble_settings is not None:
            settings: SerialSettings | BleSettings | None = ble_settings
        elif sub.is_ble:
            settings = sub.current_settings  # reconnect to the same BLE device
        else:
            settings = self.current_serial_settings()
        if settings is None:
            return
        self.connection_status_label.setText("연결 중")
        self.port_status_label.setText(f"포트: {settings.port}")
        self.statusBar().showMessage(f"{settings.port} 연결 중...", 3000)
        self._set_connection_controls_enabled(False)
        self.send_button.setEnabled(False)
        self._set_open_button_mode(True)
        self.open_button.setEnabled(True)
        self._sync_loop_button_state()
        sub.start(settings)

    def _stop_subwindow_connection(self, sub: MonitorSubWindow, wait: bool) -> None:
        self.connection_status_label.setText("닫는 중")
        settings = sub.current_settings
        if settings:
            self.statusBar().showMessage(f"Closing {settings.port}...", 3000)
        self._set_open_button_mode(True)
        self.open_button.setEnabled(False)
        self._stop_loop_sending()
        self.send_button.setEnabled(False)
        sub.stop(wait=wait)

    # -- send ---------------------------------------------------------------

    def _send_current_command(self) -> bool:
        sub = self._active_subwindow()
        if sub is None or not sub.is_connected:
            self._show_send_error("연결된 세션이 없습니다.")
            return False

        payload = self._command_payload()
        if payload is None:
            return False

        if sub.write_data(payload):
            sub.append_log("TX", self._format_payload_for_log(payload))
            return True
        return False

    # -- loop send ----------------------------------------------------------

    def _handle_loop_checkbox_toggled(self, checked: bool) -> None:
        if not checked:
            self._stop_loop_sending()
        self._sync_loop_button_state()

    def _toggle_loop_sending(self) -> None:
        if self.loop_send_timer.isActive():
            self._stop_loop_sending()
        else:
            self._start_loop_sending()

    def _start_loop_sending(self) -> None:
        sub = self._active_subwindow()
        if sub is None or not sub.is_connected:
            self._show_send_error("시리얼 포트가 연결되어 있지 않습니다.")
            self._sync_loop_button_state()
            return

        if not self.loop_checkbox.isChecked():
            self._show_send_error("Loop this command 옵션을 먼저 선택하세요.")
            self._sync_loop_button_state()
            return

        if not self._send_current_command():
            self._stop_loop_sending()
            return

        interval = self.loop_interval_spin.value()
        self.loop_send_timer.start(interval)
        self.start_loop_button.setToolTip("반복 전송 정지")
        self.start_loop_button.setAccessibleName("반복 전송 정지")
        self.start_loop_button.setEnabled(True)
        self._set_loop_controls_enabled(False)
        self.statusBar().showMessage(f"Loop sending every {interval} ms", 3000)
        sub.append_log("SESSION", f"Loop sending started every {interval} ms")

    def _stop_loop_sending(self) -> None:
        if self.loop_send_timer.isActive():
            self.loop_send_timer.stop()
            sub = self._active_subwindow()
            if sub:
                sub.append_log("SESSION", "Loop sending stopped")

        self.start_loop_button.setToolTip("반복 전송 시작")
        self.start_loop_button.setAccessibleName("반복 전송 시작")
        self._set_loop_controls_enabled(True)
        self._sync_loop_button_state()

    def _send_loop_command(self) -> None:
        if not self._send_current_command():
            self._stop_loop_sending()

    def _set_loop_controls_enabled(self, enabled: bool) -> None:
        for widget in (
            self.command_input,
            self.crlf_checkbox,
            self.string_radio,
            self.hex_radio,
            self.dec_radio,
            self.oct_radio,
            self.bin_radio,
            self.loop_checkbox,
            self.loop_interval_spin,
        ):
            widget.setEnabled(enabled)

        sub = self._active_subwindow()
        self.send_button.setEnabled(enabled and sub is not None and sub.is_connected)

    def _sync_loop_button_state(self) -> None:
        if self.loop_send_timer.isActive():
            self.start_loop_button.setEnabled(True)
            return

        sub = self._active_subwindow()
        self.start_loop_button.setEnabled(
            sub is not None and sub.is_connected and self.loop_checkbox.isChecked()
        )

    # -- log format / timestamp sync ----------------------------------------

    def _on_send_format_changed(self) -> None:
        _fmt_info = {
            self.string_radio: ("String", None,              "Enter command"),
            self.hex_radio:    ("Hex",    r"[0-9A-Fa-f ]*", "e.g.  ff ff ff"),
            self.dec_radio:    ("Dec",    r"[0-9 ]*",       "e.g.  255 072 065"),
            self.oct_radio:    ("Oct",    r"[0-7 ]*",       "e.g.  377 110 101"),
            self.bin_radio:    ("Bin",    r"[01 ]*",        "e.g.  11111111 01000001"),
        }
        for radio, (name, pattern, placeholder) in _fmt_info.items():
            if not radio.isChecked():
                continue
            current = self.command_input.text()
            converted = (
                self._convert_send_format(self._send_format, name, current)
                if current.strip() and name != self._send_format
                else current
            )
            if pattern:
                self.command_input.setValidator(
                    QRegularExpressionValidator(QRegularExpression(pattern))
                )
            else:
                self.command_input.setValidator(None)
            self.command_input.setPlaceholderText(placeholder)
            self._send_format = name
            self.command_input.setText(converted)
            break

    def _convert_send_format(self, old_fmt: str, new_fmt: str, text: str) -> str:
        values = self._text_to_byte_values(old_fmt, text)
        if not values:
            return ""
        return self._byte_values_to_text(new_fmt, values)

    def _text_to_byte_values(self, fmt: str, text: str) -> list[int]:
        if fmt == "String":
            return list(text.encode("utf-8"))
        bases = {"Hex": 16, "Dec": 10, "Oct": 8, "Bin": 2}
        base = bases[fmt]
        result = []
        for token in text.split():
            try:
                val = int(token, base)
                if 0 <= val <= 255:
                    result.append(val)
            except ValueError:
                pass
        return result

    def _byte_values_to_text(self, fmt: str, values: list[int]) -> str:
        if fmt == "String":
            return bytes(values).decode("utf-8", errors="replace")
        if fmt == "Hex":
            return " ".join(f"{v:02x}" for v in values)
        if fmt == "Dec":
            return " ".join(f"{v:03d}" for v in values)
        if fmt == "Oct":
            return " ".join(f"{v:03o}" for v in values)
        if fmt == "Bin":
            return " ".join(f"{v:08b}" for v in values)
        return ""

    def _auto_format_command_input(self, text: str) -> None:
        if self.string_radio.isChecked():
            return

        group_size = (
            2 if self.hex_radio.isChecked() else
            8 if self.bin_radio.isChecked() else
            3  # dec or oct
        )

        stripped = text.replace(" ", "")
        if not stripped:
            return

        formatted = " ".join(
            stripped[i:i + group_size] for i in range(0, len(stripped), group_size)
        )
        if formatted == text:
            return

        old_cursor = self.command_input.cursorPosition()
        non_space_before = len(text[:old_cursor].replace(" ", ""))

        self.command_input.blockSignals(True)
        self.command_input.setText(formatted)
        self.command_input.blockSignals(False)

        # 공백을 제외한 문자 수 기준으로 커서 위치 복원
        count = 0
        new_cursor = len(formatted)
        for i, ch in enumerate(formatted):
            if ch != " ":
                count += 1
                if count == non_space_before:
                    new_cursor = i + 1
                    break
        self.command_input.setCursorPosition(new_cursor)

    def _on_log_format_changed(self, fmt: str) -> None:
        sub = self._active_subwindow()
        if sub:
            sub.log_format = fmt

    def _on_timestamp_changed(self, checked: bool) -> None:
        sub = self._active_subwindow()
        if sub:
            sub.timestamp_enabled = checked

    def _clear_active_log(self) -> None:
        sub = self._active_subwindow()
        if sub:
            sub.clear_log()

    # -- command payload ----------------------------------------------------

    def _command_payload(self) -> bytes | None:
        text = self.command_input.text()
        if self.string_radio.isChecked():
            if not text:
                self._show_send_error("송신할 문자열을 입력하세요.")
                return None
            payload: bytes = text.encode("utf-8")
        else:
            tokens = self._numeric_tokens(text)
            if not tokens:
                self._show_send_error("송신할 값을 입력하세요.")
                return None

            base = self._selected_numeric_base()
            values: list[int] = []
            for token in tokens:
                try:
                    value = int(self._normalize_numeric_token(token, base), base)
                except ValueError:
                    self._show_send_error(f"숫자 형식이 올바르지 않습니다: {token}")
                    return None

                if not 0 <= value <= 255:
                    self._show_send_error(f"byte 범위를 벗어났습니다: {token}")
                    return None
                values.append(value)

            payload = bytes(values)

        if self.crlf_checkbox.isChecked():
            payload += b"\r\n"

        return payload

    @staticmethod
    def _numeric_tokens(text: str) -> list[str]:
        return [token for token in re.split(r"[\s,;]+", text.strip()) if token]

    def _selected_numeric_base(self) -> int:
        if self.hex_radio.isChecked():
            return 16
        if self.dec_radio.isChecked():
            return 10
        if self.oct_radio.isChecked():
            return 8
        if self.bin_radio.isChecked():
            return 2
        return 10

    @staticmethod
    def _normalize_numeric_token(token: str, base: int) -> str:
        lowered = token.lower()
        if base == 16 and lowered.startswith("0x"):
            return token[2:]
        if base == 8 and lowered.startswith("0o"):
            return token[2:]
        if base == 2 and lowered.startswith("0b"):
            return token[2:]
        return token

    def _format_payload_for_log(self, payload: bytes) -> str:
        mode = self.log_format_combo.currentText()
        if mode == "Hex":
            return " ".join(f"{byte:02X}" for byte in payload)
        if mode == "Dec":
            return " ".join(str(byte) for byte in payload)
        if mode == "Oct":
            return " ".join(f"{byte:03o}" for byte in payload)
        if mode == "Bin":
            return " ".join(f"{byte:08b}" for byte in payload)
        text = payload.decode("utf-8", errors="replace")
        return (
            text.replace("\\", "\\\\")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )

    # -- settings helpers ---------------------------------------------------

    def current_serial_settings(self) -> SerialSettings | None:
        port = self.port_combo.currentData()
        if not port:
            self._show_settings_error("사용 가능한 시리얼 포트가 없습니다.")
            return None

        baudrate = self._parse_baudrate(self.baudrate_combo.currentText())
        if baudrate is None:
            return None

        try:
            bytesize = int(self.databits_combo.currentText())
        except ValueError:
            self._show_settings_error("데이터 비트 값이 올바르지 않습니다.")
            return None

        parity = self._map_parity(self.parity_combo.currentText())
        stopbits = self._map_stopbits(self.stopbits_combo.currentText())
        rtscts, xonxoff = self._map_flow_control(self.flow_control_combo.currentText())

        return SerialSettings(
            port=str(port),
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            rtscts=rtscts,
            xonxoff=xonxoff,
        )

    def _parse_baudrate(self, value: str) -> int | None:
        text = value.strip()
        if not text:
            self._show_settings_error("Baudrate를 입력하세요.")
            return None
        try:
            baudrate = int(text)
        except ValueError:
            self._show_settings_error("Baudrate는 정수여야 합니다.")
            return None
        if baudrate <= 0:
            self._show_settings_error("Baudrate는 0보다 커야 합니다.")
            return None
        return baudrate

    @staticmethod
    def _map_parity(value: str) -> str:
        return {
            "No parity": serial.PARITY_NONE,
            "Odd": serial.PARITY_ODD,
            "Even": serial.PARITY_EVEN,
            "Mark": serial.PARITY_MARK,
            "Space": serial.PARITY_SPACE,
        }[value]

    @staticmethod
    def _map_stopbits(value: str) -> float:
        return {
            "1 stop bit": serial.STOPBITS_ONE,
            "1.5 stop bits": serial.STOPBITS_ONE_POINT_FIVE,
            "2 stop bits": serial.STOPBITS_TWO,
        }[value]

    @staticmethod
    def _map_flow_control(value: str) -> tuple[bool, bool]:
        return {
            "None": (False, False),
            "RTS/CTS": (True, False),
            "XON/XOFF": (False, True),
        }[value]

    def _show_settings_error(self, message: str) -> None:
        self.last_settings_error = message
        self.statusBar().showMessage(message, 5000)

    def _show_send_error(self, message: str) -> None:
        self.statusBar().showMessage(message, 5000)
        sub = self._active_subwindow()
        if sub:
            sub.append_log("ERR", message)

    # -- UI state helpers ---------------------------------------------------

    def _set_connection_controls_enabled(self, enabled: bool) -> None:
        # 블루투스 세션에서는 시리얼 설정(포트, 보드레이트 등)이 의미 없으므로 항상 흐리게 둔다.
        sub = self._active_subwindow()
        ble = sub is not None and sub.is_ble
        for widget in (
            self.port_combo,
            self.baudrate_combo,
            self.databits_combo,
            self.parity_combo,
            self.flow_control_combo,
            self.stopbits_combo,
        ):
            widget.setEnabled(enabled and not ble)
        for label in (
            self.port_label,
            self.baudrate_label,
            self.databits_label,
            self.parity_label,
            self.flow_control_label,
            self.stopbits_label,
        ):
            label.setEnabled(not ble)
        for widget in (self.refresh_ports_action, self.refresh_ports_button):
            widget.setEnabled(enabled)
        self._update_ble_status_label(sub)

    def _update_ble_status_label(self, sub: MonitorSubWindow | None) -> None:
        if sub is None or not sub.is_ble:
            self.ble_status_label.hide()
            return
        settings = sub.current_settings
        name = (settings.name or settings.address) if settings else ""
        state = "연결됨" if sub.is_connected else "연결 해제됨"
        self.ble_status_label.setText(f"{name} {state}")
        self.ble_status_label.show()

    def _sync_open_button_with_port_state(self) -> None:
        sub = self._active_subwindow()
        if sub and sub.is_connected:
            self.open_button.setEnabled(
                self.connection_status_label.text() != "닫는 중"
            )
            return
        if sub is not None and sub.is_ble:
            self.open_button.setEnabled(True)
            return
        self.open_button.setEnabled(
            self._active_subwindow() is not None
            and self.port_combo.currentData() is not None
        )

    # -- close --------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        self._save_cmd_entries()
        for sub in list(self.mdi_area.subWindowList()):
            if isinstance(sub, MonitorSubWindow):
                sub.stop(wait=True)
        event.accept()
