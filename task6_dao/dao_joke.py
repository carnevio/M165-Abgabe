from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from bson import ObjectId
from pymongo.collection import Collection

from joke import Joke

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_client, get_database


class DaoJoke:
    def __init__(self, collection: Collection):
        self.collection = collection

    @classmethod
    def from_database(
        cls,
        database_name: str | None = None,
        collection_name: str = "jokes",
    ) -> "DaoJoke":
        client = get_client()
        database = get_database(client=client, database_name=database_name or os.getenv("MONGODB_DB", "m165"))
        return cls(database[collection_name])

    def insert(self, joke: Joke) -> ObjectId:
        result = self.collection.insert_one(joke.to_document())
        return result.inserted_id

    def get_category(self, category: str) -> list[dict]:
        query = {
            "category": {
                "$elemMatch": {"$regex": category, "$options": "i"},
            }
        }
        return list(self.collection.find(query))

    def delete(self, joke_id: str) -> bool:
        try:
            object_id = ObjectId(joke_id)
        except Exception:
            return False

        result = self.collection.delete_one({"_id": object_id})
        return result.deleted_count == 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kleines CLI fuer DaoJoke")
    subparsers = parser.add_subparsers(dest="command")

    add_cmd = subparsers.add_parser("insert")
    add_cmd.add_argument("--text", required=True)
    add_cmd.add_argument("--author", default="")
    add_cmd.add_argument("--category", nargs="*", default=[])

    get_cmd = subparsers.add_parser("get-category")
    get_cmd.add_argument("category")

    delete_cmd = subparsers.add_parser("delete")
    delete_cmd.add_argument("id")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    dao = DaoJoke.from_database()

    if args.command == "insert":
        joke = Joke(text=args.text, category=args.category, author=args.author)
        inserted_id = dao.insert(joke)
        print(f"Joke gespeichert: {inserted_id}")
    elif args.command == "get-category":
        jokes = dao.get_category(args.category)
        if not jokes:
            print("Keine Witze gefunden.")
            return
        for joke in jokes:
            print(f"{joke.get('_id')} | {joke.get('text')} | {joke.get('category')} | {joke.get('author')}")
    elif args.command == "delete":
        deleted = dao.delete(args.id)
        print("Geloescht" if deleted else "Nicht gefunden / ungueltige ID")
    else:
        print("Waehle einen Befehl: insert | get-category | delete")


if __name__ == "__main__":
    main()
