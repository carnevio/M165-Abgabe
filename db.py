from __future__ import annotations

import os

from dotenv import load_dotenv
from pymongo import MongoClient


def get_connection_string(env_var: str = "MONGODB_URI") -> str:
    load_dotenv()
    connection_string = os.getenv(env_var)
    if not connection_string:
        raise RuntimeError(f"Environment variable {env_var} is not set.")
    return connection_string


def get_client(connection_string: str | None = None) -> MongoClient:
    if connection_string is None:
        connection_string = get_connection_string()
    return MongoClient(connection_string)


def get_database(client: MongoClient | None = None, database_name: str | None = None):
    if client is None:
        client = get_client()
    if database_name is None:
        database_name = os.getenv("MONGODB_DB")
    if not database_name:
        raise RuntimeError("Environment variable MONGODB_DB is not set.")
    return client[database_name]