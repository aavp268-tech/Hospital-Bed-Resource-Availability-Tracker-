
"""Hospital Bed Tracker — home page (Streamlit entry point).

Run with: streamlit run Home.py
"""

from __future__ import annotations

import streamlit as st

from config.db import HOSPITALS, get_db
from utils.ui import apply_theme, page_header, render_error


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Hospital Bed Tracker",
    page_icon="🏥",
    layout="wide"
)

apply_theme()

page_header(
    "Mumbai care network",
    "Find care with confidence.",
    "A live view of hospital beds, ICU beds, ventilators and oxygen near you.",
)


# --------------------------------------------------
# FETCH HOSPITAL DATA
# --------------------------------------------------

try:
    hospitals = list(get_db()[HOSPITALS].find({}))

except Exception as error:
    render_error(str(error))
    st.stop()


# --------------------------------------------------
# CALCULATE STATISTICS
# --------------------------------------------------

total_beds = sum(h.get("available_beds", 0) for h in hospitals)

total_icu = sum(h.get("available_icu_beds", 0) for h in hospitals)

total_vent = sum(h.get("available_ventilators", 0) for h in hospitals)

oxygen_count = sum(
    1 for h in hospitals if h.get("oxygen_available")
)


# --------------------------------------------------
# DISPLAY STATISTICS
# --------------------------------------------------

cols = st.columns(4)

cols[0].metric("Hospitals tracked", len(hospitals))
cols[1].metric("Beds available", total_beds)
cols[2].metric("ICU beds available", total_icu)
cols[3].metric("Ventilators available", total_vent)

st.caption(
    f"{oxygen_count} of {len(hospitals)} hospitals currently report oxygen available."
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main application background */
    .stApp {
        background-color: #f5f8fc;
    }

    /* Navigation cards */
    .st-key-find_hospital,
    .st-key-view_map {
        background-color: #e8f2fb !important;
        border: 1px solid #b9d6ee !important;
        border-left: 5px solid #1f6fb5 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        transition: all 0.3s ease;
    }

    /* Card hover effect */
    .st-key-find_hospital:hover,
    .st-key-view_map:hover {
        background-color: #dcecf9 !important;
        border-color: #1f6fb5 !important;
        box-shadow: 0 5px 15px rgba(31, 111, 181, 0.12);
    }

    /* Card headings */
    .st-key-find_hospital h3,
    .st-key-view_map h3 {
        color: #0f4c81 !important;
        font-weight: 700 !important;
    }

    /* Card descriptions */
    .st-key-find_hospital p,
    .st-key-view_map p {
        color: #263b50 !important;
    }

    /* Navigation links */
    .st-key-find_hospital a[data-testid="stPageLink-NavLink"],
    .st-key-view_map a[data-testid="stPageLink-NavLink"] {
        background-color: #1f6fb5 !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        width: fit-content !important;
        text-decoration: none !important;
        transition: background-color 0.2s ease;
    }

    /* Navigation link text */
    .st-key-find_hospital a[data-testid="stPageLink-NavLink"] *,
    .st-key-view_map a[data-testid="stPageLink-NavLink"] * {
        color: #ffffff !important;
    }

    /* Navigation link hover */
    .st-key-find_hospital a[data-testid="stPageLink-NavLink"]:hover,
    .st-key-view_map a[data-testid="stPageLink-NavLink"]:hover {
        background-color: #175a96 !important;
    }

    /* Divider */
    hr {
        border-color: #d5e0eb !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# NAVIGATION SECTION
# --------------------------------------------------

st.divider()

left, right = st.columns(2, gap="large")


# FIND A HOSPITAL
with left:

    with st.container(border=True, key="find_hospital"):

        st.markdown("### 🔎 Find a hospital")

        st.write(
            "Search by area, resource and distance, "
            "with tap-to-call numbers."
        )

        st.page_link(
            "pages/1_Search.py",
            label="Go to Search",
            icon="🔎"
        )


# VIEW ON THE MAP
with right:

    with st.container(border=True, key="view_map"):

        st.markdown("### 🗺️ View on the map")

        st.write(
            "See your latest search on a map, "
            "colour-coded by availability."
        )

        st.page_link(
            "pages/2_Map.py",
            label="Go to Map",
            icon="🗺️"
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Hospital availability shown here is reported by hospital staff "
    "and may not always be current. For medical emergencies, "
    "call local emergency services directly."
)
