from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()
connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)

while True:
    # List databases
    databases = client.list_database_names()
    if not databases:
        print("No Database")
        input("\nDrücke eine beliebige Taste, um zurückzukehren")
        continue
    print("Databases")
    for db in databases:
        print(f" - {db}")

    while True:
        selected_db = input("\nSelect Database: ")
        if selected_db not in databases:
            print("Datenbank nicht gefunden. Bitte erneut versuchen.")
            continue
        break

    print(f"\n{selected_db}\n")
    db = client[selected_db]

    # List collections
    collections = db.list_collection_names()
    if not collections:
        print("No Collection")
        input("\nDrücke eine beliebige Taste, um zurückzukehren")
        continue
    print("Collections")
    for col in collections:
        print(f" - {col}")

    while True:
        selected_col = input("\nSelect Collection: ")
        if selected_col not in collections:
            print("Collection not found. Bitte erneut versuchen.")
            continue
        break

    # List documents
    print(f"\n{selected_db}.{selected_col}")
    collection = db[selected_col]
    documents = list(collection.find())
    if not documents:
        print("No Document")
        input("\nDrücke eine beliebige Taste, um zurückzukehren")
        continue
    print("Documents")
    doc_ids = [str(document['_id']) for document in documents]
    for doc_id in doc_ids:
        print(f" - {doc_id}")

    while True:
        selected_doc = input("\nWähle das Document (ID) aus: ")
        try:
            doc_id_type = type(documents[0]['_id'])
            document = collection.find_one({'_id': doc_id_type(selected_doc)})
        except Exception:
            document = None
        if not document:
            print("Document nicht gefunden. Bitte erneut versuchen.")
            continue
        break

    print(f"\n{selected_db}.{selected_col}.{selected_doc}\n")
    for key, value in document.items():
        print(f"{key}: {value}")

    input("\nDrücke eine beliebige Taste, um zurückzukehren")
    continue