"""Measure the numbers for the 'Performance metrics' table.

Run from the project root (needs your .env / Atlas connection):
    python measure_performance.py

What it does (all read-only except step 2, which re-saves one hospital's
CURRENT values, so the data stays the same but updated_at and one
resource_updates history row per run are added):
  1. 25 simulated searches  -> response time and accuracy
  2. admin update           -> update-to-visible latency
Accuracy = search returned exactly the hospitals that have the resource and
have coordinates (checked against a plain database query), sorted nearest-first.
"""
import random
import statistics
import time

from config.db import HOSPITALS, get_db
from crud import update_resources
from utils.distance import find_nearby_hospitals
from utils.geo import list_areas, resolve_area

RESOURCES = {
    "ICU bed": lambda h: h.get("available_icu_beds", 0) > 0,
    "General bed": lambda h: h.get("available_beds", 0) > 0,
    "Ventilator": lambda h: h.get("available_ventilators", 0) > 0,
    "Any": lambda h: (h.get("available_beds", 0) > 0 or h.get("available_icu_beds", 0) > 0
                      or h.get("available_ventilators", 0) > 0 or h.get("oxygen_available", False)),
}


def summary(label, values, unit):
    print(f"{label}: mean {statistics.mean(values):.3f} {unit}, "
          f"median {statistics.median(values):.3f}, max {max(values):.3f} (n={len(values)})")


def main():
    hospitals = list(get_db()[HOSPITALS].find({}))
    print(f"Hospitals in database: {len(hospitals)}")

    random.seed(1)
    areas, names = list_areas(), list(RESOURCES)
    times, correct = [], 0
    for _ in range(25):
        area, resource = random.choice(areas), random.choice(names)
        lat, lon = resolve_area(area)
        start = time.perf_counter()
        results = find_nearby_hospitals(lat, lon, resource)
        times.append(time.perf_counter() - start)

        expected = {h["hospital_name"] for h in hospitals
                    if RESOURCES[resource](h) and h.get("latitude") is not None
                    and h.get("longitude") is not None}
        returned = [r["hospital_name"] for r in results]
        distances = [r["distance"] for r in results]
        if set(returned) == expected and distances == sorted(distances):
            correct += 1
    summary("Search response time", times, "s")
    print(f"Search accuracy: {correct}/25 = {correct / 25:.0%}")

    target = hospitals[0]
    latencies = []
    for _ in range(10):
        start = time.perf_counter()
        ok, _ = update_resources(
            target["hospital_name"], target["available_beds"], target["available_icu_beds"],
            target["available_ventilators"], target["oxygen_available"])
        find_nearby_hospitals(target["latitude"], target["longitude"], "Any")  # visible to a patient
        latencies.append(time.perf_counter() - start)
        assert ok
    summary("Admin update -> visible in search", latencies, "s")


if __name__ == "__main__":
    main()