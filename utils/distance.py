import json
from geopy.distance import geodesic

def find_nearby_hospitals(patient_lat, patient_lon, resource_type):import json
from geopy.distance import geodesic


def find_nearby_hospitals(patient_lat, patient_lon, resource_type):

    with open("data/hospitals.json", "r") as file:
        hospitals = json.load(file)

    patient_location = (patient_lat, patient_lon)

    results = []

    for hospital in hospitals:

        if resource_type == "ICU bed":
            if hospital["icu_beds"] <= 0:
                continue

        elif resource_type == "General bed":
            if hospital["available_beds"] <= 0:
                continue

        elif resource_type == "Ventilator":
            if hospital["ventilators"] <= 0:
                continue

        elif resource_type == "Any":
            if not (
                hospital["available_beds"] > 0
                or hospital["icu_beds"] > 0
                or hospital["ventilators"] > 0
                or hospital["oxygen_available"]
            ):
                continue

        hospital_location = (
            hospital["latitude"],
            hospital["longitude"]
        )

        distance = geodesic(
            patient_location,
            hospital_location
        ).km

        results.append({
    "hospital_name": hospital["hospital_name"],
    "location": hospital["location"],
    "available_beds": hospital["available_beds"],
    "icu_beds": hospital["icu_beds"],
    "ventilators": hospital["ventilators"],
    "oxygen_available": hospital["oxygen_available"],
    "contact": hospital["contact"],
    "distance": distance
})

    results.sort(key=lambda x: x["distance"])

    return results

results = find_nearby_hospitals(19.1000, 72.9000, "Any")

for result in results:
    print(result["hospital_name"], result["distance"])