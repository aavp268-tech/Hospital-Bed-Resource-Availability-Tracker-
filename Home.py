"""Hospital Bed Tracker — home page (Streamlit entry point).

Run with:  streamlit run Home.py
"""
from __future__ import annotations

import streamlit as st

from config.db import HOSPITALS, get_db
from utils.ui import apply_theme, page_header, render_error

st.set_page_config(page_title="Hospital Bed Tracker", page_icon="🏥", layout="wide")
apply_theme()
page_header(
    "Mumbai care network",
    "Find care with confidence.",
    "A live view of hospital beds, ICU beds, ventilators and oxygen near you.",
)

try:
    hospitals = list(get_db()[HOSPITALS].find({}))
except Exception as error:
    render_error(str(error))
    st.stop()

total_beds = sum(h.get("available_beds", 0) for h in hospitals)
total_icu = sum(h.get("available_icu_beds", 0) for h in hospitals)
total_vent = sum(h.get("available_ventilators", 0) for h in hospitals)
oxygen_count = sum(1 for h in hospitals if h.get("oxygen_available"))

cols = st.columns(4)
cols[0].metric("Hospitals tracked", len(hospitals))
cols[1].metric("Beds available", total_beds)
cols[2].metric("ICU beds available", total_icu)
cols[3].metric("Ventilators available", total_vent)
st.caption(f"{oxygen_count} of {len(hospitals)} hospitals currently report oxygen available.")

st.divider()
left, right = st.columns(2)
with left:
    st.markdown("### 🔎 Find a hospital")
    st.write("Search by area, resource type and distance, with a tap-to-call number for every result.")
    st.page_link("pages/1_Search.py", label="Go to Search", icon="🔎")
with right:
    st.markdown("### 🗺️ View on the map")
    st.write("See your latest search plotted on a map, colour-coded by availability.")
    st.page_link("pages/2_Map.py", label="Go to Map", icon="🗺️")

st.divider()
st.caption(
    "Hospital availability shown here is reported by hospital staff and may not always be current. "
    "For medical emergencies, call local emergency services directly."
)