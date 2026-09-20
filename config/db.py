"""MongoDB connection for the Hospital Tracker.

Every other module gets its database through this file:

    from config.db import get_db, HOSPITALS
    hospitals = get_db()[HOSPITALS]

Settings come from environment variables (or a local .env file):
    MONGODB_URI       required, e.g. mongodb+srv://user:pass@cluster0.xxxx.mongodb.net/
    MONGODB_DATABASE  optional, defaults to "hospital_tracker"

Check your setup from the project root with:
    python -m config.db
"""
from __future__ import annotations

import os
from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

# Optional: read a .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Collection names live in one place so a typo can't create a stray collection.
HOSPITALS = "hospitals"
ADMINS = "admins"
SEARCH_LOGS = "search_logs"
RESOURCE_UPDATES = "resource_updates"

DEFAULT_DATABASE = "hospital_tracker"


class DatabaseError(RuntimeError):
    """Raised when MongoDB is not configured or cannot be reached."""


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    """Return one shared MongoClient, creating it on first use.

    MongoClient keeps its own connection pool and is thread-safe, so the whole
    app should share a single instance. lru_cache does not cache exceptions,
    so if the first attempt fails, the next call simply tries again.
    """
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        raise DatabaseError(
            "MONGODB_URI is not set. Put it in your environment or in a .env file."
        )
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000, appName="hospital-tracker")
        client.admin.command("ping")  # forces a real connection now, not on first query
    except PyMongoError as exc:
        raise DatabaseError(
            f"Could not connect to MongoDB: {exc}\n"
            "Check: 1) your IP is allowed in Atlas > Network Access, "
            "2) the username/password are correct (special characters must be URL-encoded), "
            "3) you installed pymongo[srv] for mongodb+srv:// links."
        ) from exc
    return client


def get_db() -> Database:
    """Return the application database."""
    return get_client()[os.getenv("MONGODB_DATABASE", DEFAULT_DATABASE)]


def get_collection(name: str) -> Collection:
    """Shortcut: get_collection(HOSPITALS) instead of get_db()[HOSPITALS]."""
    return get_db()[name]


if __name__ == "__main__":
    # Quick self-test: connect, list collections and document counts.
    database = get_db()
    print(f"Connected to database '{database.name}'")
    existing = set(database.list_collection_names())
    for collection_name in sorted(existing):
        print(f"  {collection_name}: {database[collection_name].count_documents({})} documents")

    expected = {HOSPITALS, ADMINS, SEARCH_LOGS}
    missing = expected - existing
    if missing:
        print(f"\nMissing collections: {', '.join(sorted(missing))}")
        if "searchlogs" in existing and SEARCH_LOGS in missing:
            print("Rename 'searchlogs' to 'search_logs' in Atlas so the code finds it.")