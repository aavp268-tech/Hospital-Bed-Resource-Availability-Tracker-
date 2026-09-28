"""Hospital admin: register, sign in, and update resource availability.

Uses the fixed auth.py (registration/login linked to a hospital) and
crud.py (update_resources with validation and history).
"""
import streamlit as st

from auth import login_admin, register_admin
from config.db import HOSPITALS, get_db
from crud import get_hospital, update_resources
from utils.ui import apply_theme, page_header

st.set_page_config(page_title="Hospital Admin", page_icon="🏥", layout="centered")
apply_theme()
page_header("Partner portal", "Keep your availability current", "Sign in to update your hospital's numbers.")

if "admin" not in st.session_state:
    st.session_state.admin = None

if st.session_state.admin is None:
    hospital_names = [h["hospital_name"] for h in get_db()[HOSPITALS].find({}, {"hospital_name": 1})]

    register_tab, login_tab = st.tabs(["Register", "Sign in"])
    with register_tab:
        with st.form("register"):
            hospital_name = st.selectbox("Hospital", sorted(hospital_names))
            username = st.text_input("Choose username")
            password = st.text_input("Create password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Create admin account", type="primary"):
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, message = register_admin(username, password, hospital_name)
                    (st.success if ok else st.error)(message)

    with login_tab:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", type="primary"):
                ok, result = login_admin(username, password)
                if ok:
                    st.session_state.admin = result
                    st.rerun()
                else:
                    st.error(result)

else:
    admin = st.session_state.admin
    hospital = get_hospital(admin["hospital_name"])
    st.success(f"Signed in as {admin['username']} · {admin['hospital_name']}")

    if hospital is None:
        st.error("This hospital is no longer in the directory.")
    else:
        st.caption(hospital.get("location", ""))
        with st.form("resources"):
            a, b, c = st.columns(3)
            beds = a.number_input("Available beds", min_value=0, value=int(hospital.get("available_beds", 0)), step=1)
            icu = b.number_input("Available ICU beds", min_value=0, value=int(hospital.get("available_icu_beds", 0)), step=1)
            vent = c.number_input("Available ventilators", min_value=0, value=int(hospital.get("available_ventilators", 0)), step=1)
            oxygen = st.checkbox("Oxygen available", value=bool(hospital.get("oxygen_available", False)))
            if st.form_submit_button("Save availability", type="primary"):
                ok, result = update_resources(admin["hospital_name"], beds, icu, vent, oxygen)
                if ok:
                    st.success("Availability updated for patients.")
                else:
                    st.error(result)

    if st.button("Sign out"):
        st.session_state.admin = None
        st.rerun()