from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import psutil


@dataclass
class Power:
    cpu: float | None = None
    ram_total: int | None = None
    ram_used: int | None = None
    timestamp: datetime | None = None

    def __post_init__(self) -> None:
        if self.cpu is None:
            self.cpu = float(psutil.cpu_percent(interval=None))

        if self.ram_total is None or self.ram_used is None:
            memory = psutil.virtual_memory()
            if self.ram_total is None:
                self.ram_total = int(memory.total)
            if self.ram_used is None:
                self.ram_used = int(memory.used)

        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_document(self) -> dict:
        return {
            "cpu": float(self.cpu),
            "ram_total": int(self.ram_total),
            "ram_used": int(self.ram_used),
            "timestamp": self.timestamp,
        }
