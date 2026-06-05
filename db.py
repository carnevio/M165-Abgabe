import os
from dotenv import load_dotenv
from pymongo import MongoClient

                                                
load_dotenv()

def get_connection_string(env_var="MONGODB_URI"):
    
    connection_string = os.getenv(env_var)
    if not connection_string:
        print(f"Fehler: Umgebungsvariable {env_var} ist nicht gesetzt!")
        exit(1)
    return connection_string

def get_client(connection_string=None):
    
    if connection_string is None:
        connection_string = get_connection_string()
    return MongoClient(connection_string)

def get_database(client=None, database_name=None):
    
    if client is None:
        client = get_client()
    if database_name is None:
        database_name = os.getenv("MONGODB_DB")
    
                                                                     
    if not database_name:
        database_name = "m165"
        
    return client[database_name]