"""Create the collections and indexes the app needs. Safe to run more than once.

Run from the project root:
    python -m scripts.setup_db
"""
from __future__ import annotations

from pymongo import ASCENDING, DESCENDING

from config.db import ADMINS, HOSPITALS, RESOURCE_UPDATES, SEARCH_LOGS, get_db


def find_duplicates(collection, field: str) -> list[dict]:
    """Return values of `field` that appear in more than one document."""
    pipeline = [
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
    ]
    return list(collection.aggregate(pipeline))


def main() -> None:
    db = get_db()

    # 1. Make sure every collection exists.
    existing = set(db.list_collection_names())
    for name in (HOSPITALS, ADMINS, SEARCH_LOGS, RESOURCE_UPDATES):
        if name not in existing:
            db.create_collection(name)
            print(f"Created collection: {name}")

    # 2. Unique indexes. These fail if duplicates already exist, so check first.
    problems = 0
    for collection_name, field in ((HOSPITALS, "hospital_name"), (ADMINS, "username")):
        duplicates = find_duplicates(db[collection_name], field)
        if duplicates:
            problems += 1
            print(f"\nCannot make {collection_name}.{field} unique, duplicates found:")
            for item in duplicates:
                if item["_id"] is None:
                    print(f"  {item['count']} documents have no '{field}' field at all")
                else:
                    print(f"  {item['_id']!r} appears {item['count']} times")
            print("  Fix or delete those documents in Atlas, then run this script again.")
            continue
        db[collection_name].create_index([(field, ASCENDING)], unique=True)
        print(f"Index ok: {collection_name}.{field} (unique)")

    # 3. Query-speed indexes.
    db[SEARCH_LOGS].create_index([("searched_at", DESCENDING)])
    print(f"Index ok: {SEARCH_LOGS}.searched_at")
    db[RESOURCE_UPDATES].create_index([("hospital_id", ASCENDING), ("updated_at", DESCENDING)])
    print(f"Index ok: {RESOURCE_UPDATES}.hospital_id + updated_at")

    if problems:
        raise SystemExit(f"\nFinished with {problems} problem(s). See messages above.")
    print("\nDatabase setup complete.")


if __name__ == "__main__":
    main()