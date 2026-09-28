"""F-2: Map view of the latest search, now using the shared F-3 theme.

Reads what pages/1_Search.py stored in st.session_state:
    "search_results"  hospitals inside the radius that have the resource
    "search_all"      every hospital that has the resource, at any distance
    "search_meta"     {"area", "resource", "radius_km", "lat", "lon"}

Marker colours:
    green   has the resource and is inside the search radius
    orange  has the resource but is outside the radius
    red     does not currently have the resource
    blue    the patient's chosen area
"""
import folium
import streamlit as st
from geopy.distance import geodesic
from streamlit_folium import st_folium

from config.db import HOSPITALS, get_db
from utils.ui import apply_theme, page_header, render_empty_state, render_error

st.set_page_config(page_title="Hospital Map", page_icon="🗺️", layout="centered")
apply_theme()
page_header("Mumbai care network", "Hospital map", "Your search results, plotted by distance and availability.")

meta = st.session_state.get("search_meta")
if not meta:
    render_empty_state()
    st.page_link("pages/1_Search.py", label="Go to Search", icon="🔎")
    st.stop()

within = st.session_state.get("search_results", [])
has_resource = st.session_state.get("search_all", [])
within_names = {h["hospital_name"] for h in within}
has_resource_names = {h["hospital_name"] for h in has_resource}
by_name = {h["hospital_name"]: h for h in has_resource}

origin = (meta["lat"], meta["lon"])
resource, radius_km = meta["resource"], meta["radius_km"]

st.markdown(f"**{resource}** near **{meta['area']}**, radius {radius_km} km")


def popup_html(name, distance, lines, contact=None):
    body = "".join(f"<div>{line}</div>" for line in lines)
    call = f'<div><a href="tel:{contact}">📞 {contact}</a></div>' if contact else ""
    return f"<b>{name}</b><div>{distance} km away</div>{body}{call}"


try:
    all_hospitals = list(get_db()[HOSPITALS].find({}))
except Exception as error:
    render_error(str(error))
    all_hospitals = list(by_name.values())  # fall back to what the search already found

m = folium.Map(location=origin, zoom_start=12, tiles="OpenStreetMap")

folium.Marker(origin, tooltip=f"You: {meta['area']}", icon=folium.Icon(color="blue", icon="user", prefix="fa")).add_to(m)
folium.Circle(origin, radius=radius_km * 1000, color="#2a6fdb", fill=True, fill_opacity=0.06, weight=1).add_to(m)

bounds = [origin]
for hospital in all_hospitals:
    lat, lon = hospital.get("latitude"), hospital.get("longitude")
    if lat is None or lon is None:
        continue
    name = hospital.get("hospital_name", "Unknown hospital")

    if name in within_names:
        color, status = "green", f"{resource} available"
    elif name in has_resource_names:
        color, status = "orange", f"{resource} available, outside radius"
    else:
        color, status = "red", f"No {resource.lower()} available"

    found = by_name.get(name)
    distance = found["distance"] if found else round(geodesic(origin, (lat, lon)).km, 1)

    lines = [
        status,
        f"Beds: {hospital.get('available_beds', 0)} &nbsp; ICU: {hospital.get('available_icu_beds', 0)} "
        f"&nbsp; Ventilators: {hospital.get('available_ventilators', 0)}",
        "Oxygen: " + ("yes" if hospital.get("oxygen_available") else "no"),
    ]
    folium.Marker(
        (lat, lon),
        tooltip=f"{name} ({distance} km)",
        popup=folium.Popup(popup_html(name, distance, lines, hospital.get("contact")), max_width=260),
        icon=folium.Icon(color=color, icon="plus-sign"),
    ).add_to(m)
    if color == "green":
        bounds.append((lat, lon))

if len(bounds) > 1:
    m.fit_bounds(bounds, padding=(30, 30))

st_folium(m, use_container_width=True, height=520, returned_objects=[])

st.markdown(
    "🟢 available within radius &nbsp; 🟠 available but farther away &nbsp; "
    "🔴 not available &nbsp; 🔵 your area"
)
if not within:
    st.warning(f"No {resource.lower()} available within {radius_km} km. Orange markers show the nearest hospitals that have it.")
st.caption("Availability can change quickly. Please call the hospital to confirm before travelling.")