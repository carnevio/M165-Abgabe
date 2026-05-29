from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_client, get_database


def bytes_to_gib(value: int) -> float:
    return value / (1024**3)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Visualisiert gespeicherte CPU/RAM Logs.")
    parser.add_argument("--database", type=str, default=os.getenv("MONGODB_DB", "m165"), help="Datenbankname")
    parser.add_argument("--collection", type=str, default="power_logs", help="Collection-Name")
    parser.add_argument("--limit", type=int, default=300, help="Anzahl Logs fuer den Graph")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    client = get_client()
    database = get_database(client=client, database_name=args.database)
    collection = database[args.collection]

    logs = list(collection.find().sort("timestamp", -1).limit(args.limit))
    if not logs:
        print("Keine Power-Logs vorhanden.")
        return

    logs.reverse()

    timestamps = [entry.get("timestamp") for entry in logs]
    cpu_values = [float(entry.get("cpu", 0.0)) for entry in logs]
    ram_used_gib = [bytes_to_gib(int(entry.get("ram_used", 0))) for entry in logs]
    ram_total_gib = [bytes_to_gib(int(entry.get("ram_total", 0))) for entry in logs]

    figure, (ax_cpu, ax_ram) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    ax_cpu.plot(timestamps, cpu_values, color="tab:blue", linewidth=1.5, label="CPU %")
    ax_cpu.set_ylabel("CPU %")
    ax_cpu.set_title("CPU Auslastung")
    ax_cpu.grid(True, alpha=0.3)
    ax_cpu.legend()

    ax_ram.plot(timestamps, ram_used_gib, color="tab:green", linewidth=1.5, label="RAM used (GiB)")
    ax_ram.plot(timestamps, ram_total_gib, color="tab:red", linewidth=1.2, linestyle="--", label="RAM total (GiB)")
    ax_ram.set_ylabel("RAM (GiB)")
    ax_ram.set_title("RAM Auslastung")
    ax_ram.set_xlabel("Zeit")
    ax_ram.grid(True, alpha=0.3)
    ax_ram.legend()

    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
