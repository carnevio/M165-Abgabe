from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()
connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)

print(client.server_info())