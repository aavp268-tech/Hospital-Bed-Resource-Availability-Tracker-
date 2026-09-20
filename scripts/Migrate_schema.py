"""One-time migration: make every hospital document follow the same schema.

Target fields on each hospital:
    hospital_name, location, contact, latitude, longitude, oxygen_available
    total_beds,        available_beds
    total_icu_beds,    available_icu_beds
    total_ventilators, available_ventilators
    updated_at

What it changes:
    icu_beds     -> available_icu_beds
    ventilators  -> available_ventilators
    adds total_icu_beds / total_ventilators if missing (PLACEHOLDER: twice the
    current available number; replace with real figures where you know them)
    adds updated_at if missing

By default it only PRINTS what it would do. Add --apply to write the changes.
It is safe to run more than once.

Run from the project root:
    python -m scripts.migrate_schema            # preview
    python -m scripts.migrate_schema --apply    # write
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone

from config.db import HOSPITALS, get_db

REQUIRED = ["hospital_name", "location", "latitude", "longitude", "total_beds", "available_beds"]


def plan_changes(doc: dict, now: datetime) -> tuple[dict, dict]:
    """Return ($set, $unset) needed to bring one document up to the target schema."""
    to_set: dict = {}
    to_unset: dict = {}

    if "icu_beds" in doc:
        to_set["available_icu_beds"] = doc["icu_beds"]
        to_unset["icu_beds"] = ""
    if "ventilators" in doc:
        to_set["available_ventilators"] = doc["ventilators"]
        to_unset["ventilators"] = ""

    available_icu = to_set.get("available_icu_beds", doc.get("available_icu_beds", 0))
    available_vent = to_set.get("available_ventilators", doc.get("available_ventilators", 0))

    if "total_icu_beds" not in doc:
        to_set["total_icu_beds"] = available_icu * 2
    if "total_ventilators" not in doc:
        to_set["total_ventilators"] = available_vent * 2
    if "updated_at" not in doc:
        to_set["updated_at"] = now

    return to_set, to_unset


def main() -> None:
    apply_changes = "--apply" in sys.argv
    hospitals = get_db()[HOSPITALS]
    now = datetime.now(timezone.utc)
    changed = 0

    for doc in hospitals.find({}):
        label = doc.get("hospital_name", f"<no hospital_name> {doc['_id']}")

        missing = [field for field in REQUIRED if field not in doc]
        if missing:
            print(f"WARNING {label}: missing required field(s): {', '.join(missing)}")

        to_set, to_unset = plan_changes(doc, now)
        if not to_set and not to_unset:
            continue

        changed += 1
        print(f"{label}: set {sorted(to_set)}  remove {sorted(to_unset)}")
        if apply_changes:
            update: dict = {"$set": to_set}
            if to_unset:
                update["$unset"] = to_unset
            hospitals.update_one({"_id": doc["_id"]}, update)

    mode = "Updated" if apply_changes else "Would update"
    print(f"\n{mode} {changed} document(s).")
    if not apply_changes and changed:
        print("Nothing was written. Run again with --apply to save the changes.")


if __name__ == "__main__":
    main()