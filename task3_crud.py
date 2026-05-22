from __future__ import annotations

from datetime import datetime
import math
import os

from bson import ObjectId

from db import get_client, get_database


DATABASE_NAME = os.getenv("MONGODB_DB", "restaurants")
COLLECTION_NAME = "restaurants"


def get_collection():
    client = get_client()
    database = get_database(client, DATABASE_NAME)
    return database[COLLECTION_NAME]


def prompt_choice(prompt: str, allowed_values: list[str]) -> str:
    while True:
        value = input(prompt).strip()
        if value in allowed_values:
            return value
        print("Eingabe nicht gefunden. Bitte erneut versuchen.")


def print_separator() -> None:
    print()


def get_borough_values(collection) -> list[str]:
    try:
        values = collection.distinct("borough")
        return sorted(value for value in values if value)
    except Exception:
        return []


def show_boroughs(collection) -> None:
    boroughs = get_borough_values(collection)
    if not boroughs:
        print("No Borough")
        return

    print("Boroughs")
    for borough in boroughs:
        print(f" - {borough}")


def show_top_restaurants(collection) -> None:
    pipeline = [
        {"$match": {"score": {"$type": "number"}}},
        {
            "$group": {
                "_id": "$name",
                "avg_score": {"$avg": "$score"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"avg_score": -1, "count": -1, "_id": 1}},
        {"$limit": 3},
    ]

    results = list(collection.aggregate(pipeline))
    if not results:
        print("No Restaurant")
        return

    print("Top 3 Restaurants")
    for index, restaurant in enumerate(results, start=1):
        name = restaurant.get("_id", "Unknown")
        avg_score = restaurant.get("avg_score", 0)
        count = restaurant.get("count", 0)
        print(f"{index}. {name} - Durchschnitt: {avg_score:.2f} ({count} Einträge)")


def extract_coordinates(document: dict) -> list[float] | None:
    candidates = [
        document.get("coordinates"),
        document.get("coord"),
        document.get("location", {}).get("coordinates") if isinstance(document.get("location"), dict) else None,
        document.get("address", {}).get("coord") if isinstance(document.get("address"), dict) else None,
        document.get("address", {}).get("coordinates") if isinstance(document.get("address"), dict) else None,
    ]

    for candidate in candidates:
        if isinstance(candidate, (list, tuple)) and len(candidate) == 2:
            try:
                return [float(candidate[0]), float(candidate[1])]
            except (TypeError, ValueError):
                continue
    return None


def haversine_distance(coord_a: list[float], coord_b: list[float]) -> float:
    lon1, lat1 = coord_a
    lon2, lat2 = coord_b
    radius = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def find_restaurant_by_name(collection, name: str) -> dict | None:
    return collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})


def find_nearest_to_le_perigord(collection) -> None:
    reference = collection.find_one({"name": {"$regex": "^Le Perigord$", "$options": "i"}})
    if not reference:
        print("Le Perigord nicht gefunden.")
        return

    reference_coordinates = extract_coordinates(reference)
    if not reference_coordinates:
        print("Keine Koordinaten für Le Perigord gefunden.")
        return

    nearest_restaurant = None
    nearest_distance = None

    for restaurant in collection.find({"_id": {"$ne": reference["_id"]}}):
        coordinates = extract_coordinates(restaurant)
        if not coordinates:
            continue

        distance = haversine_distance(reference_coordinates, coordinates)
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_restaurant = restaurant

    if not nearest_restaurant:
        print("Kein anderes Restaurant mit Koordinaten gefunden.")
        return

    print("Nearest Restaurant")
    print(f"Name: {nearest_restaurant.get('name', 'Unknown')}")
    print(f"Distance to Le Perigord: {nearest_distance:.3f} km")


def build_search_query(name: str, cuisine: str) -> dict:
    query: dict[str, object] = {}
    conditions = []

    if name:
        conditions.append({"name": {"$regex": name, "$options": "i"}})
    if cuisine:
        conditions.append({"cuisine": {"$regex": cuisine, "$options": "i"}})

    if not conditions:
        return query
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def search_restaurants(collection) -> list[dict]:
    name = input("Name (leer lassen, um zu ignorieren): ").strip()
    cuisine = input("Küche (leer lassen, um zu ignorieren): ").strip()

    query = build_search_query(name, cuisine)
    results = list(collection.find(query))

    if not results:
        print("Keine Restaurants gefunden.")
        return []

    print("Search Results")
    for restaurant in results:
        print(
            f" - ID: {restaurant.get('_id')} | Name: {restaurant.get('name', 'Unknown')} | "
            f"Küche: {restaurant.get('cuisine', 'Unknown')} | Borough: {restaurant.get('borough', 'Unknown')}"
        )

    return results


def choose_restaurant(collection, results: list[dict]) -> dict | None:
    if not results:
        return None

    if len(results) == 1:
        return results[0]

    allowed_ids = [str(result.get("_id")) for result in results]
    selected_id = prompt_choice("Select Restaurant ID: ", allowed_ids)

    for result in results:
        if str(result.get("_id")) == selected_id:
            return result

    try:
        return collection.find_one({"_id": ObjectId(selected_id)})
    except Exception:
        return None


def add_rating(collection) -> None:
    results = search_restaurants(collection)
    if not results:
        return

    selected_restaurant = choose_restaurant(collection, results)
    if not selected_restaurant:
        print("Restaurant nicht gefunden.")
        return

    while True:
        rating_input = input("Bewertung (Score): ").strip()
        try:
            score = float(rating_input)
            break
        except ValueError:
            print("Bitte eine Zahl eingeben.")

    rating_entry = {
        "date": datetime.now(),
        "score": score,
    }

    collection.update_one(
        {"_id": selected_restaurant["_id"]},
        {"$push": {"grades": rating_entry}},
    )
    print("Bewertung gespeichert.")


def menu() -> None:
    collection = get_collection()

    while True:
        print_separator()
        print("CRUD Menu")
        print("1 - Alle Stadtbezirke anzeigen")
        print("2 - Top 3 Restaurants nach Durchschnitt")
        print("3 - Restaurant mit Le Perigord vergleichen")
        print("4 - Restaurant suchen")
        print("5 - Restaurant suchen und bewerten")
        print("0 - Beenden")

        choice = input("Choice: ").strip()

        if choice == "1":
            show_boroughs(collection)
        elif choice == "2":
            show_top_restaurants(collection)
        elif choice == "3":
            find_nearest_to_le_perigord(collection)
        elif choice == "4":
            search_restaurants(collection)
        elif choice == "5":
            add_rating(collection)
        elif choice == "0":
            break
        else:
            print("Ungültige Auswahl.")


def main() -> None:
    menu()


if __name__ == "__main__":
    main()