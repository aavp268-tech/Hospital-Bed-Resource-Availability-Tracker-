"""F-1: Patient search & filter page.

Flow: pick area + resource + radius -> Search -> nearest hospitals with that
resource available, each with distance, availability and a tap-to-call link.

Shared with the other frontend members via st.session_state:
    st.session_state["search_results"]  hospitals inside the radius, nearest first
    st.session_state["search_all"]      every hospital that has the resource (any distance)
    st.session_state["search_meta"]     {"area", "resource", "radius_km", "lat", "lon"}

Each result is a dict from utils.distance.find_nearby_hospitals():
    hospital_name, location, available_beds, icu_beds, ventilators,
    oxygen_available, contact, latitude, longitude, distance (km)

    F-2 (map) reads the lists above to draw markers.
    F-3 (fallback/UI) replaces render_not_available() below.
"""
import streamlit as st

from models.search_log import save_search_log
from utils.distance import find_nearby_hospitals
from utils.geo import list_areas, resolve_area

RESOURCE_OPTIONS = ["ICU bed", "General bed", "Ventilator", "Any"]

st.set_page_config(page_title="Find a Hospital", page_icon="🏥", layout="centered")
st.title("🏥 Find Available Beds")
st.caption("Nearest hospitals with the resource you need, updated by hospital staff.")


# ---------- result rendering ----------
def render_hospital_card(hospital: dict) -> None:
    """One result card. Uses the border container so it looks fine on mobile too."""
    with st.container(border=True):
        top_left, top_right = st.columns([3, 1])
        top_left.subheader(hospital["hospital_name"])
        top_right.metric("Distance", f"{hospital['distance']} km")

        if hospital.get("location"):
            st.caption(f"📍 {hospital['location']}")

        beds, icu, vent = st.columns(3)
        beds.metric("Beds", hospital.get("available_beds", 0))
        icu.metric("ICU beds", hospital.get("icu_beds", 0))
        vent.metric("Ventilators", hospital.get("ventilators", 0))

        st.write("Oxygen: " + ("✅ available" if hospital.get("oxygen_available") else "❌ not available"))

        contact = hospital.get("contact")
        if contact:
            digits = "".join(ch for ch in contact if ch.isdigit() or ch == "+")
            st.markdown(f"📞 [Call {contact}](tel:{digits})")
        st.caption("Availability can change quickly. Please call to confirm before travelling.")


def render_results(results: list, resource: str, radius_km: int) -> None:
    st.success(f"{len(results)} hospital(s) with {resource.lower()} available within {radius_km} km")
    for hospital in results:
        render_hospital_card(hospital)


def render_not_available(all_results: list, resource: str, radius_km: int) -> None:
    """PLACEHOLDER for F-3: replace with the proper 'not available' screen.

    all_results holds every hospital that has the resource at any distance,
    nearest first, so the nearest alternatives are simply all_results[:3].
    """
    st.warning(f"No {resource.lower()} available within {radius_km} km.")
    if all_results:
        st.write("Nearest hospitals that do have it:")
        for hospital in all_results[:3]:
            render_hospital_card(hospital)
    else:
        st.write("No hospital currently reports this resource available. Try 'Any' or call a hospital directly.")


# ---------- search form ----------
with st.form("search_form"):
    area = st.selectbox("Your area", list_areas(), index=list_areas().index("Andheri West"))
    resource = st.selectbox("Resource needed", RESOURCE_OPTIONS)
    radius_km = st.slider("Search radius (km)", min_value=1, max_value=50, value=10)
    submitted = st.form_submit_button("Search", use_container_width=True)

if submitted:
    lat, lon = resolve_area(area)
    try:
        with st.spinner("Searching hospitals..."):
            everything = find_nearby_hospitals(lat, lon, resource)
    except Exception as error:  # database unreachable, etc.
        st.error(f"Could not search right now: {error}")
        st.stop()

    within = [h for h in everything if h["distance"] <= radius_km]

    # Logging must never break the search, so failures here are ignored.
    try:
        save_search_log(lat, lon, resource, len(within))
    except Exception:
        pass

    st.session_state["search_all"] = everything
    st.session_state["search_results"] = within
    st.session_state["search_meta"] = {
        "area": area, "resource": resource, "radius_km": radius_km, "lat": lat, "lon": lon,
    }

# ---------- show the latest search (survives reruns) ----------
meta = st.session_state.get("search_meta")
if meta:
    st.divider()
    st.markdown(f"**{meta['resource']}** near **{meta['area']}**")
    if st.session_state["search_results"]:
        render_results(st.session_state["search_results"], meta["resource"], meta["radius_km"])
    else:
        render_not_available(st.session_state["search_all"], meta["resource"], meta["radius_km"])