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
