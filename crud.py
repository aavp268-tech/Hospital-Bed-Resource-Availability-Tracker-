from config.db import get_db, HOSPITALS
from datetime import datetime, timezone
hospitals_collection = get_db()[HOSPITALS]
#add hospital
def add_hospital(
    hospital_name,
    location,
    contact,
    latitude,
    longitude,
    total_beds,
    available_beds,
    total_icu_beds,
    available_icu_beds,
    total_ventilators,
    available_ventilators,
    oxygen_available
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
        "updated_at": datetime.now(timezone.utc)
    }

    hospitals_collection.insert_one(hospital)

    return hospital
#read by hospital name
def get_hospital(hospital_name):
    hospital = hospitals_collection.find_one({
        "hospital_name": hospital_name
    })

    return hospital

#update hospital resources
def update_resources(
    hospital_name,
    available_beds,
    available_icu_beds,
    available_ventilators,
    oxygen_available
):
    result = hospitals_collection.update_one(
        {"hospital_name": hospital_name},
        {
            "$set": {
                "available_beds": available_beds,
                "available_icu_beds": available_icu_beds,
                "available_ventilators": available_ventilators,
                "oxygen_available": oxygen_available,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    return result.modified_count > 0

print(update_resources(
    "Test Hospital",
    35,
    6,
    3,
    15
))


 