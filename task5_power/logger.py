from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from pymongo.collection import Collection

from power import Power

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_client, get_database


def trim_to_max_logs(collection: Collection, max_logs: int) -> int:
    count = collection.count_documents({})
    overflow = count - max_logs
    if overflow <= 0:
        return 0

    old_ids = [
        document["_id"]
        for document in collection.find({}, {"_id": 1}).sort("timestamp", 1).limit(overflow)
    ]
    if not old_ids:
        return 0

    result = collection.delete_many({"_id": {"$in": old_ids}})
    return result.deleted_count


def log_loop(collection: Collection, interval_seconds: float, max_logs: int) -> None:
    collection.create_index("timestamp")

    print("Power logger gestartet. Stoppen mit Ctrl+C.")
    while True:
        power = Power()
        collection.insert_one(power.to_document())

        deleted = trim_to_max_logs(collection, max_logs)
        if deleted > 0:
            print(f"{deleted} alte Logs entfernt.")

        print(
            f"[{power.timestamp:%Y-%m-%d %H:%M:%S}] "
            f"CPU={power.cpu:.1f}% RAM_USED={power.ram_used} RAM_TOTAL={power.ram_total}"
        )
        time.sleep(interval_seconds)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Loggt Power-Werte im Sekundentakt in MongoDB.")
    parser.add_argument("--interval", type=float, default=1.0, help="Messintervall in Sekunden")
    parser.add_argument("--max-logs", type=int, default=10000, help="Maximale Anzahl gespeicherter Logs")
    parser.add_argument("--database", type=str, default=os.getenv("MONGODB_DB", "m165"), help="Datenbankname")
    parser.add_argument("--collection", type=str, default="power_logs", help="Collection-Name")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    client = get_client()
    database = get_database(client=client, database_name=args.database)
    collection = database[args.collection]

    try:
        log_loop(collection, interval_seconds=args.interval, max_logs=args.max_logs)
    except KeyboardInterrupt:
        print("\nPower logger beendet.")


if __name__ == "__main__":
    main()
