from __future__ import annotations

from bson import ObjectId

from db import get_client


def prompt_for_choice(prompt: str, allowed_values: list[str]) -> str:
    while True:
        value = input(prompt)
        if value in allowed_values:
            return value
        print("Eingabe nicht gefunden. Bitte erneut versuchen.")


def main() -> None:
    client = get_client()

    while True:
        databases = client.list_database_names()
        if not databases:
            print("No Database")
            input("\nPress any button to return")
            continue

        print("Databases")
        for database in databases:
            print(f" - {database}")

        selected_database = prompt_for_choice("\nSelect Database: ", databases)
        database = client[selected_database]

        print(f"\n{selected_database}\n")
        collections = database.list_collection_names()
        if not collections:
            print("No Collection")
            input("\nPress any button to return")
            continue

        print("Collections")
        for collection_name in collections:
            print(f" - {collection_name}")

        selected_collection = prompt_for_choice("\nSelect Collection: ", collections)
        collection = database[selected_collection]

        print(f"\n{selected_database}.{selected_collection}")
        documents = list(collection.find())
        if not documents:
            print("No Document")
            input("\nPress any button to return")
            continue

        print("Documents")
        document_ids = [str(document["_id"]) for document in documents]
        for document_id in document_ids:
            print(f" - {document_id}")

        selected_document = prompt_for_choice("\nSelect Document: ", document_ids)

        document = None
        try:
            object_id = ObjectId(selected_document)
            document = collection.find_one({"_id": object_id})
        except Exception:
            for candidate in documents:
                if str(candidate["_id"]) == selected_document:
                    document = candidate
                    break

        if not document:
            print("Document nicht gefunden. Bitte erneut versuchen.")
            continue

        print(f"\n{selected_database}.{selected_collection}.{selected_document}\n")
        for key, value in document.items():
            print(f"{key}: {value}")

        input("\nPress any button to return")


if __name__ == "__main__":
    main()