from geopy.distance import geodesic

from config.db import get_db, HOSPITALS


def find_nearby_hospitals(patient_lat, patient_lon, resource_type):

    # Get hospital data from MongoDB
    hospitals = get_db()[HOSPITALS].find({})

    patient_location = (patient_lat, patient_lon)

    results = []

    for hospital in hospitals:

        # Check whether the requested resource is available
        if resource_type == "ICU bed":
            if hospital.get("available_icu_beds", 0) <= 0:
                continue

        elif resource_type == "General bed":
            if hospital.get("available_beds", 0) <= 0:
                continue

        elif resource_type == "Ventilator":
            if hospital.get("available_ventilators", 0) <= 0:
                continue

        elif resource_type == "Any":
            if not (
                hospital.get("available_beds", 0) > 0
                or hospital.get("available_icu_beds", 0) > 0
                or hospital.get("available_ventilators", 0) > 0
                or hospital.get("oxygen_available", False)
            ):
                continue

        # Skip hospitals that do not have location data
        if hospital.get("latitude") is None or hospital.get("longitude") is None:
            continue

        hospital_location = (
            hospital["latitude"],
            hospital["longitude"]
        )

        # Calculate distance between patient and hospital
        distance = geodesic(
            patient_location,
            hospital_location
        ).km

        # Keep the same output structure as before
        results.append({
            "hospital_name": hospital.get("hospital_name"),
            "location": hospital.get("location"),
            "available_beds": hospital.get("available_beds", 0),
            "icu_beds": hospital.get("available_icu_beds", 0),
            "ventilators": hospital.get("available_ventilators", 0),
            "oxygen_available": hospital.get("oxygen_available", False),
            "contact": hospital.get("contact"),
            "distance": distance
        })

    # Sort hospitals from nearest to farthest
    results.sort(key=lambda x: x["distance"])

    return results


# Test
if __name__ == "__main__":

    results = find_nearby_hospitals(
        19.1000,
        72.9000,
        "Any"
    )

    for result in results:
        print(
            result["hospital_name"],
            result["distance"]
        )