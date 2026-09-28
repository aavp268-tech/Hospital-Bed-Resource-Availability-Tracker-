"""F-1: Patient search & filter page, now using the shared F-3 theme and states.

Shared with the map page via st.session_state:
    st.session_state["search_results"]  hospitals inside the radius, nearest first
    st.session_state["search_all"]      every hospital that has the resource (any distance)
    st.session_state["search_meta"]     {"area", "resource", "radius_km", "lat", "lon"}
"""
import streamlit as st

from models.search_log import save_search_log
from utils.distance import find_nearby_hospitals
from utils.geo import list_areas, resolve_area
from utils.ui import apply_theme, page_header, render_empty_state, render_error, render_not_available

RESOURCE_OPTIONS = ["ICU bed", "General bed", "Ventilator", "Any"]

st.set_page_config(page_title="Find a Hospital", page_icon="🏥", layout="centered")
apply_theme()
page_header("Mumbai care network", "Find available beds", "Nearest hospitals with the resource you need.")


def render_hospital_card(hospital: dict) -> None:
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


with st.form("search_form"):
    areas = list_areas()
    area = st.selectbox("Your area", areas, index=areas.index("Andheri West"))
    resource = st.selectbox("Resource needed", RESOURCE_OPTIONS)
    radius_km = st.slider("Search radius (km)", min_value=1, max_value=50, value=10)
    submitted = st.form_submit_button("Search", use_container_width=True)

if submitted:
    lat, lon = resolve_area(area)
    try:
        with st.spinner("Searching hospitals..."):
            everything = find_nearby_hospitals(lat, lon, resource)
    except Exception as error:
        render_error(str(error))
        st.stop()

    within = [h for h in everything if h["distance"] <= radius_km]

    try:
        save_search_log(lat, lon, resource, len(within))
    except Exception:
        pass  # logging must never break the search

    st.session_state["search_all"] = everything
    st.session_state["search_results"] = within
    st.session_state["search_meta"] = {
        "area": area, "resource": resource, "radius_km": radius_km, "lat": lat, "lon": lon,
    }

meta = st.session_state.get("search_meta")
if not meta:
    render_empty_state()
else:
    st.divider()
    st.markdown(f"**{meta['resource']}** near **{meta['area']}**")
    results = st.session_state["search_results"]
    if results:
        st.success(f"{len(results)} hospital(s) with {meta['resource'].lower()} available within {meta['radius_km']} km")
        for hospital in results:
            render_hospital_card(hospital)
    else:
        render_not_available(st.session_state["search_all"], meta["resource"], meta["radius_km"], render_hospital_card)