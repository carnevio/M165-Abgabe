import os
import sys
from pathlib import Path
from bson import ObjectId

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from task7_files.gridfs_helper import GridFSHelper

def print_banner():
    print("=" * 60)
    print("                FOTOALBUM MANAGER CLI  ")
    print("=" * 60)

def prompt_choice(prompt, allowed_values):
    while True:
        value = input(prompt).strip()
        if value in allowed_values:
            return value
        print("Ungültige Eingabe. Bitte versuchen Sie es erneut.")

def upload_photo(helper):
    print("\n--- Foto hochladen ---")
    
    while True:
        file_path_str = input("Pfad zum Bild (z.B. ./beispiel.jpg): ").strip()
        file_path = Path(file_path_str)
        if file_path.is_file():
            break
        print("Datei existiert nicht. Bitte einen gültigen Pfad eingeben.")

    existing_albums = helper.get_all_albums()
    if existing_albums:
        print("\nExistierende Alben:")
        for idx, album in enumerate(existing_albums, start=1):
            print(f" [{idx}] {album}")
        print(f" [{len(existing_albums) + 1}] Neues Album erstellen")
        
        choices = [str(i) for i in range(1, len(existing_albums) + 2)]
        choice = int(prompt_choice(f"Wählen Sie ein Album (1-{len(choices)}): ", choices))
        
        if choice <= len(existing_albums):
            album_name = existing_albums[choice - 1]
        else:
            album_name = input("Name des neuen Albums: ").strip()
    else:
        album_name = input("Keine existierenden Alben gefunden. Name des neuen Albums: ").strip()

    if not album_name:
        print("Albumname darf nicht leer sein!")
        return

    # Filename
    filename = input(f"Dateiname in der DB (Standard: {file_path.name}): ").strip()
    if not filename:
        filename = file_path.name

    try:
        file_id = helper.upload_file(file_path, filename=filename, album_name=album_name)
        print(f"\nErfolgreich hochgeladen!")
        print(f"  - ID: {file_id}")
        print(f"  - Album: {album_name}")
        print(f"  - Name: {filename}")
    except Exception as e:
        print(f" Fehler beim Hochladen: {e}")

def download_photos(helper):
    print("\n--- Fotos herunterladen ---")
    existing_albums = helper.get_all_albums()
    if not existing_albums:
        print("Keine Alben in der Datenbank vorhanden.")
        return

    print("\nExistierende Alben:")
    for idx, album in enumerate(existing_albums, start=1):
        print(f" [{idx}] {album}")
    
    choices = [str(i) for i in range(1, len(existing_albums) + 1)]
    choice = int(prompt_choice(f"Wählen Sie ein Album (1-{len(choices)}): ", choices))
    album_name = existing_albums[choice - 1]

    files = helper.get_files_by_album(album_name)
    if not files:
        print(f"Keine Fotos im Album '{album_name}' gefunden.")
        return

    print(f"\nFotos in '{album_name}':")
    for idx, file_doc in enumerate(files, start=1):
        size_kb = file_doc.length / 1024.0
        upload_date = file_doc.upload_date
        date_str = upload_date.strftime("%Y-%m-%d %H:%M:%S") if upload_date else "Unbekannt"
        print(f" [{idx}] {file_doc.filename} (Grösse: {size_kb:.1f} KB, Upload: {date_str})")
    print(f" [{len(files) + 1}] ALLE FOTOS HERUNTERLADEN")

    choices = [str(i) for i in range(1, len(files) + 2)]
    photo_choice = int(prompt_choice(f"Wählen Sie ein Foto (1-{len(choices)}): ", choices))

    # Target directory
    default_dir = Path(f"./downloaded_photos/{album_name}")
    target_dir_str = input(f"Speicherordner (Standard: {default_dir}): ").strip()
    target_dir = Path(target_dir_str) if target_dir_str else default_dir

    if photo_choice <= len(files):
        # Download single photo
        file_doc = files[photo_choice - 1]
        target_path = target_dir / file_doc.filename
        try:
            helper.download_file_by_id(file_doc._id, target_path)
            print(f"Foto erfolgreich heruntergeladen nach: {target_path}")
        except Exception as e:
            print(f"Fehler beim Herunterladen: {e}")
    else:
        # Download all photos
        print(f"Lade {len(files)} Fotos herunter...")
        success_count = 0
        for file_doc in files:
            target_path = target_dir / file_doc.filename
            try:
                helper.download_file_by_id(file_doc._id, target_path)
                success_count += 1
            except Exception as e:
                print(f"Fehler bei '{file_doc.filename}': {e}")
        print(f"{success_count}/{len(files)} Fotos erfolgreich heruntergeladen nach: {target_dir}")

def list_all_photos(helper):
    print("\n--- Übersicht aller Alben und Fotos ---")
    albums = helper.get_all_albums()
    if not albums:
        print("Keine Fotos oder Alben in der Datenbank gefunden.")
        return

    for album in albums:
        files = helper.get_files_by_album(album)
        print(f"\nAlbum: {album} ({len(files)} Fotos)")
        for file_doc in files:
            size_kb = file_doc.length / 1024.0
            print(f"  - {file_doc.filename} (ID: {file_doc._id}, {size_kb:.1f} KB)")

def delete_photo(helper):
    print("\n--- Foto löschen ---")
    albums = helper.get_all_albums()
    if not albums:
        print("Keine Fotos vorhanden.")
        return

    list_all_photos(helper)
    
    file_id_str = input("\nGeben Sie die ID des zu löschenden Fotos ein: ").strip()
    if not file_id_str:
        return

    try:
        file_id = ObjectId(file_id_str)
        # Check if file exists
        if helper.fs.exists(file_id):
            helper.delete_file_by_id(file_id)
            print(f"Foto mit ID {file_id_str} erfolgreich gelöscht.")
        else:
            print(f"Keine Datei mit ID {file_id_str} gefunden.")
    except Exception as e:
        print(f"Ungültige ID oder Fehler beim Löschen: {e}")

def main():
    try:
        helper = GridFSHelper()
    except Exception as e:
        print(f"Fehler bei der Verbindung zur MongoDB: {e}")
        sys.exit(1)

    while True:
        print_banner()
        print(" [1] Foto hochladen")
        print(" [2] Fotos aus einem Album herunterladen")
        print(" [3] Alle Alben und Fotos auflisten")
        print(" [4] Foto löschen")
        print(" [0] Beenden")
        print("=" * 60)
        
        choice = prompt_choice("Auswahl: ", ["1", "2", "3", "4", "0"])
        
        if choice == "1":
            upload_photo(helper)
        elif choice == "2":
            download_photos(helper)
        elif choice == "3":
            list_all_photos(helper)
        elif choice == "4":
            delete_photo(helper)
        elif choice == "0":
            print("\nProgramm beendet. Auf Wiedersehen!")
            break

if __name__ == "__main__":
    main()
