import os
from dotenv import load_dotenv
from db import get_client, get_database

def print_path_env():
                                                                  
    path_value = os.getenv("PATH", "")
    print("PATH:")
    print(path_value)

def get_env_value(name):
    load_dotenv()
    return os.getenv(name)

def masked(value):
                                                                            
    if not value:
        return "<not set>"
    if len(value) <= 12:
        return value
    return value[:6] + "..." + value[-6:]

def show_connection_info():
                                     
    uri = get_env_value("MONGODB_URI")
    dbname = get_env_value("MONGODB_DB")
    print("MongoDB Environment")
    print(f" - MONGODB_URI: {masked(uri)}")
    print(f" - MONGODB_DB: {dbname or '<not set>'}")

def test_mongo_connection():
                                                                          
    try:
        client = get_client()
        info = client.server_info()
        version = info.get("version", "unknown")
        print(f"MongoDB connected — server version: {version}")
    except Exception as exc:
        print(f"MongoDB connection failed: {exc}")

def try_list_collections():
                                                                
    try:
        client = get_client()
        dbname = os.getenv("MONGODB_DB")
        if not dbname:
            print("MONGODB_DB not set — skipping collection list")
            return
        db = get_database(client=client, database_name=dbname)
        cols = db.list_collection_names()
        print(f"Collections in {dbname}:")
        for c in cols:
            print(f" - {c}")
    except Exception:
        print("Could not list collections (check credentials/connection)")

def main():
    print_path_env()
    print()
    show_connection_info()
    print()
    test_mongo_connection()
    print()
    try_list_collections()

if __name__ == "__main__":
    main()
