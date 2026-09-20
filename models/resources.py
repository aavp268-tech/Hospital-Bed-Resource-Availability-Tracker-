"""Resource availability: current numbers on the hospital + a history row per update.

Typical use (admin dashboard):
    from models.resources import record_update, ValidationError
    try:
        record_update("KEM Hospital", {"available_beds": 12, "oxygen_available": True}, "kem_admin")
    except ValidationError as error:
        show_error(str(error))
"""
from __future__ import annotations

from datetime import datetime, timezone
from numbers import Integral
from typing import Any

from pymongo import DESCENDING, ReturnDocument

from config.db import HOSPITALS, RESOURCE_UPDATES, get_db

# available_* field -> the total_* field that caps it
COUNT_FIELDS = {
    "available_beds": "total_beds",
    "available_icu_beds": "total_icu_beds",
    "available_ventilators": "total_ventilators",
}
FLAG_FIELDS = ("oxygen_available",)


class ValidationError(ValueError):
    """The submitted numbers are not acceptable. The message is safe to show to the admin."""


def validate_update(values: dict[str, Any], hospital: dict[str, Any]) -> dict[str, Any]:
    """Check `values` against the hospital's totals and return a cleaned copy."""
    if not values:
        raise ValidationError("Nothing to update.")

    unknown = set(values) - set(COUNT_FIELDS) - set(FLAG_FIELDS)
    if unknown:
        raise ValidationError(f"Unknown field(s): {', '.join(sorted(unknown))}")

    clean: dict[str, Any] = {}
    for field, value in values.items():
        if field in COUNT_FIELDS:
            # bool is a subclass of int in Python, so reject it explicitly.
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise ValidationError(f"{field} must be a whole number.")
            value = int(value)
            if value < 0:
                raise ValidationError(f"{field} cannot be negative.")
            total_field = COUNT_FIELDS[field]
            total = hospital.get(total_field)
            if total is not None and value > total:
                raise ValidationError(f"{field} ({value}) cannot be more than {total_field} ({total}).")
            clean[field] = value
        else:
            if not isinstance(value, bool):
                raise ValidationError(f"{field} must be True or False.")
            clean[field] = value
    return clean


def record_update(hospital_name: str, values: dict[str, Any], admin_username: str) -> dict[str, Any]:
    """Validate and save new availability numbers.

    1. Updates the hospital's current numbers and `updated_at`.
    2. Adds a snapshot row to `resource_updates`, so history is never lost.
    Returns the updated hospital document.
    """
    db = get_db()
    hospital = db[HOSPITALS].find_one({"hospital_name": hospital_name})
    if hospital is None:
        raise LookupError(f"Unknown hospital: {hospital_name}")

    clean = validate_update(values, hospital)
    now = datetime.now(timezone.utc)

    updated = db[HOSPITALS].find_one_and_update(
        {"_id": hospital["_id"]},
        {"$set": {**clean, "updated_at": now}},
        return_document=ReturnDocument.AFTER,
    )
    db[RESOURCE_UPDATES].insert_one(
        {
            "hospital_id": hospital["_id"],
            "hospital_name": hospital_name,
            "admin": admin_username,
            "updated_at": now,
            **{field: updated.get(field) for field in (*COUNT_FIELDS, *FLAG_FIELDS)},
        }
    )
    return updated


def get_history(hospital_name: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """Newest-first update history for one hospital, or for all hospitals if no name is given."""
    db = get_db()
    query: dict[str, Any] = {}
    if hospital_name:
        hospital = db[HOSPITALS].find_one({"hospital_name": hospital_name}, {"_id": 1})
        if hospital is None:
            raise LookupError(f"Unknown hospital: {hospital_name}")
        query["hospital_id"] = hospital["_id"]
    return list(db[RESOURCE_UPDATES].find(query, {"_id": 0}).sort("updated_at", DESCENDING).limit(limit))