import os
import sys
from pathlib import Path

from bson import ObjectId

                                                                           
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_client, get_database

class Room:
    def __init__(self, name, seats, building):
        """
        Klasse zur Repraesentation eines Zimmers.
        """
        self.name = name
        self.seats = int(seats)
        self.building = building

    def to_document(self):
        """
        Konvertiert das Raum-Objekt in ein MongoDB-Dokument.
        """
        return {
            "name": self.name,
            "seats": self.seats,
            "building": self.building,
        }

class DaoRoom:
    """
    Data Access Object (DAO) fuer Zimmer (Rooms). (Aufgabe 6.1)
    """
    def __init__(self, collection):
        self.collection = collection

    @classmethod
    def from_database(cls, database_name=None, collection_name="rooms"):
        client = get_client()
        database = get_database(client=client, database_name=database_name or os.getenv("MONGODB_DB", "m165"))
        return cls(database[collection_name])

    def insert(self, room):
                                    
        result = self.collection.insert_one(room.to_document())
        return result.inserted_id

    def get_all(self):
                                              
        return list(self.collection.find())

    def get_by_id(self, room_id):
                                        
        try:
            object_id = ObjectId(room_id)
        except Exception:
            return None
        return self.collection.find_one({"_id": object_id})

    def update(self, room_id, updates):
                                                                        
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

    def delete(self, room_id):
                                                        
        try:
            object_id = ObjectId(room_id)
        except Exception:
            return False

        result = self.collection.delete_one({"_id": object_id})
        return result.deleted_count == 1

                                        
Dao_room = DaoRoom

