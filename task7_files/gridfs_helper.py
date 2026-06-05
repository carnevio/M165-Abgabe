import os
import sys
from pathlib import Path
from bson import ObjectId
import gridfs

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_client, get_database

class GridFSHelper:
    
    def __init__(self, db=None):
        if db is None:
            self.db = get_database()
        else:
            self.db = db
        self.fs = gridfs.GridFS(self.db)

    def upload_file(self, file_path, filename=None, album_name=None):
        
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Die Datei {file_path} wurde nicht gefunden.")

        if not filename:
            filename = path.name

        metadata = {}
        if album_name:
            metadata["album"] = album_name

        with open(path, "rb") as f:
            file_id = self.fs.put(
                f,
                filename=filename,
                metadata=metadata
            )
        return file_id

    def download_file_by_id(self, file_id, target_path):
        
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)

        try:
            grid_out = self.fs.get(file_id)
        except gridfs.errors.NoFile:
            raise FileNotFoundError(f"Keine Datei mit ID {file_id} gefunden.")

        target_file_path = Path(target_path)
        target_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_file_path, "wb") as f:
            f.write(grid_out.read())
        return target_file_path

    def get_files_by_album(self, album_name):
        
        query = {"metadata.album": album_name}
        return list(self.fs.find(query))

    def get_all_albums(self):
        
        files_collection = self.db["fs.files"]
        albums = files_collection.distinct("metadata.album")
        return [album for album in albums if album]

    def delete_file_by_id(self, file_id):
        
        if isinstance(file_id, str):
            file_id = ObjectId(file_id)
        
        self.fs.delete(file_id)
