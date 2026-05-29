from __future__ import annotations

from dataclasses import dataclass
import os
import sys
from pathlib import Path

from bson import ObjectId
from pymongo.collection import Collection

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_client, get_database


@dataclass
class Room:
    name: str
    seats: int
    building: str

    def to_document(self) -> dict:
        return {
            "name": self.name,
            "seats": int(self.seats),
            "building": self.building,
        }


class DaoRoom:
    def __init__(self, collection: Collection):
        self.collection = collection

    @classmethod
    def from_database(
        cls,
        database_name: str | None = None,
        collection_name: str = "rooms",
    ) -> "DaoRoom":
        client = get_client()
        database = get_database(client=client, database_name=database_name or os.getenv("MONGODB_DB", "m165"))
        return cls(database[collection_name])

    def insert(self, room: Room) -> ObjectId:
        result = self.collection.insert_one(room.to_document())
        return result.inserted_id

    def get_all(self) -> list[dict]:
        return list(self.collection.find())

    def get_by_id(self, room_id: str) -> dict | None:
        try:
            object_id = ObjectId(room_id)
        except Exception:
            return None
        return self.collection.find_one({"_id": object_id})

    def update(self, room_id: str, updates: dict) -> bool:
        try:
            object_id = ObjectId(room_id)
        except Exception:
            return False

        allowed_fields = {"name", "seats", "building"}
        safe_updates = {key: value for key, value in updates.items() if key in allowed_fields}
        if not safe_updates:
            return False

        result = self.collection.update_one({"_id": object_id}, {"$set": safe_updates})
        return result.modified_count == 1

    def delete(self, room_id: str) -> bool:
        try:
            object_id = ObjectId(room_id)
        except Exception:
            return False

        result = self.collection.delete_one({"_id": object_id})
        return result.deleted_count == 1


Dao_room = DaoRoom
