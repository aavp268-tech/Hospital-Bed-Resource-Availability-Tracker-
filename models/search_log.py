from datetime import datetime, timezone

from config.db import get_db, SEARCH_LOGS


def save_search_log(patient_lat, patient_lng, resource_type, results_found):

    log = {
        "patient_lat": patient_lat,
        "patient_lng": patient_lng,
        "resource_type": resource_type,
        "results_found": results_found,
        "searched_at": datetime.now(timezone.utc)
    }

    collection = get_db()[SEARCH_LOGS]
    collection.insert_one(log)