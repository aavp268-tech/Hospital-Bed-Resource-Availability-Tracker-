"""Hospital CRUD: create, read and update hospital records.

Fix over the previous version: update_resources() had no validation (a
negative number, or a number above the hospital's total, would be saved as
given) and never wrote to resource_updates, so no update history was kept.
"""
from datetime import datetime, timezone

from config.db import ADMINS, HOSPITALS, RESOURCE_UPDATES, get_db

hospitals_collection = get_db()[HOSPITALS]
resource_updates_collection = get_db()[RESOURCE_UPDATES]

COUNT_FIELDS = {
    "available_beds": "total_beds",
    "available_icu_beds": "total_icu_beds",
    "available_ventilators": "total_ventilators",
}


def add_hospital(
    hospital_name, location, contact, latitude, longitude,
    total_beds, available_beds,
    total_icu_beds, available_icu_beds,
    total_ventilators, available_ventilators,
    oxygen_available,
):
    hospital = {
        "hospital_name": hospital_name,
        "location": location,
        "contact": contact,
        "latitude": latitude,
        "longitude": longitude,
        "oxygen_available": oxygen_available,
        "total_beds": total_beds,
        "available_beds": available_beds,
        "total_icu_beds": total_icu_beds,
        "available_icu_beds": available_icu_beds,
        "total_ventilators": total_ventilators,
        "available_ventilators": available_ventilators,
        "updated_at": datetime.now(timezone.utc),
    }
    hospitals_collection.insert_one(hospital)
    return hospital


def get_hospital(hospital_name):
    return hospitals_collection.find_one({"hospital_name": hospital_name})


def update_resources(hospital_name, available_beds, available_icu_beds, available_ventilators, oxygen_available):
    """Validate and save new availability numbers for one hospital.

    Returns (True, hospital_doc) on success, (False, error_message) on failure.
    A failed validation changes nothing in the database.
    """
    hospital = get_hospital(hospital_name)
    if hospital is None:
        return False, f"Unknown hospital: {hospital_name}"

    values = {
        "available_beds": available_beds,
        "available_icu_beds": available_icu_beds,
        "available_ventilators": available_ventilators,
    }
    for field, value in values.items():
        if not isinstance(value, int) or isinstance(value, bool):
            return False, f"{field} must be a whole number"
        if value < 0:
            return False, f"{field} cannot be negative"
        total_field = COUNT_FIELDS[field]
        total = hospital.get(total_field)
        if total is not None and value > total:
            return False, f"{field} ({value}) cannot be more than {total_field} ({total})"

    if not isinstance(oxygen_available, bool):
        return False, "oxygen_available must be True or False"

    now = datetime.now(timezone.utc)
    hospitals_collection.update_one(
        {"hospital_name": hospital_name},
        {"$set": {**values, "oxygen_available": oxygen_available, "updated_at": now}},
    )
    resource_updates_collection.insert_one({
        "hospital_name": hospital_name,
        "updated_at": now,
        **values,
        "oxygen_available": oxygen_available,
    })

    return True, get_hospital(hospital_name)