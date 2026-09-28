"""Hospital admin registration, login, and resource updates."""
from __future__ import annotations

import streamlit as st

from models.auth import authenticate, register_admin
from models.hospital_crud import get_hospital, list_hospitals, update_resources

st.set_page_config(page_title="Hospital Admin · CareMap", page_icon="🏥", layout="wide")

st.markdown("<style>.stApp{background:#f7f9fc}.admin-title{color:#102a43;font-size:2.4rem;font-weight:800;letter-spacing:-.04em}.eyebrow{color:#e16f4e;font-weight:800;letter-spacing:.12em;text-transform:uppercase;font-size:.73rem}</style>", unsafe_allow_html=True)
st.markdown('<div class="eyebrow">Partner portal</div>', unsafe_allow_html=True)
st.markdown('<div class="admin-title">Keep your availability current.</div>', unsafe_allow_html=True)
st.write("Hospital teams can register, sign in, and update resources in a few seconds.")

hospitals = list_hospitals()
if "admin" not in st.session_state:
    st.session_state.admin = None

if st.session_state.admin is None:
    register, login = st.tabs(["Register hospital", "Sign in"])
    with register:
        with st.form("register"):
            hospital = st.selectbox("Hospital", [item["name"] for item in hospitals])
            username = st.text_input("Choose username")
            password = st.text_input("Create password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            if st.form_submit_button("Create admin account", type="primary"):
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, message = register_admin(username, password, hospital)
                    (st.success if ok else st.error)(message)
    with login:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", type="primary"):
                admin = authenticate(username, password)
                if admin:
                    st.session_state.admin = admin
                    st.rerun()
                st.error("We could not verify those details.")
else:
    admin = st.session_state.admin
    hospital = get_hospital(admin["hospital_name"])
    st.success(f"Signed in as {admin['hospital_name']}")
    if hospital is None:
        st.error("This hospital is no longer in the directory.")
    else:
        st.markdown(f"### {hospital['name']}")
        st.caption(hospital["address"])
        with st.form("resources"):
            a, b, c = st.columns(3)
            with a:
                beds = st.number_input("Available beds", min_value=0, value=int(hospital.get("beds", 0)), step=1)
            with b:
                icu = st.number_input("Available ICU beds", min_value=0, value=int(hospital.get("icu_beds", 0)), step=1)
            with c:
                ventilators = st.number_input("Available ventilators", min_value=0, value=int(hospital.get("ventilators", 0)), step=1)
            if st.form_submit_button("Save availability", type="primary"):
                update_resources(hospital["name"], {"beds": beds, "icu_beds": icu, "ventilators": ventilators})
                st.success("Availability updated for patients.")
        if st.button("Sign out"):
            st.session_state.admin = None
            st.rerun()
