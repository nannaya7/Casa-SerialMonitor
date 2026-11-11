"""Shared serial connection settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SerialSettings:
    """pyserial-ready settings selected from the UI."""

    port: str
    baudrate: int
    bytesize: int
    parity: str
    stopbits: float
    rtscts: bool
    xonxoff: bool

    @property
    def cmd_key(self) -> str:
        """Key under which this target's CMD send data is stored."""
        return f"serial:{self.port}"


@dataclass(frozen=True)
class BleSettings:
    """Bluetooth LE (Nordic UART Service) connection target."""

    address: str
    name: str = ""

    @property
    def port(self) -> str:
        """Display label used where a serial port name is shown."""
        return f"{self.name} ({self.address})" if self.name else self.address

    @property
    def cmd_key(self) -> str:
        """Key under which this target's CMD send data is stored (name, else address)."""
        return f"ble:{self.name or self.address}"
