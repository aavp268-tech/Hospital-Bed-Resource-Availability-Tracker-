"""Hospital Bed & Resource Availability Tracker — Streamlit entry point."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from config.db import load_local_state, mongo_database, storage_mode
from models.hospital_crud import list_hospitals
from models.search_log import get_search_logs, log_search
from utils.distance import search_hospitals

st.set_page_config(page_title="CareMap Mumbai", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

DATA_SOURCE = Path(__file__).resolve().parent / "data" / "hospitals.json"


def ensure_demo_data() -> None:
    if list_hospitals():
        return
    if DATA_SOURCE.exists():
        hospitals = json.loads(DATA_SOURCE.read_text(encoding="utf-8"))
        db = mongo_database()
        if db is not None:
            db.hospitals.insert_many(hospitals)
        else:
            state = load_local_state()
            state["hospitals"] = hospitals
            from config.db import save_local_state
            save_local_state(state)


def resource_label(key: str) -> str:
    return {"beds": "Beds", "icu_beds": "ICU beds", "ventilators": "Ventilators"}.get(key, key)


def inject_css() -> None:
    st.markdown("""
    <style>
      .stApp { background: #f7f9fc; }
      [data-testid="stSidebar"] { background: #102a43; }
      [data-testid="stSidebar"] * { color: #f4f7fb !important; }
      .brand { color: #0d6b68; font-size: 2.6rem; font-weight: 800; letter-spacing: -0.04em; margin: .3rem 0 0; }
      .subhead { color: #61758a; font-size: 1.05rem; margin: .2rem 0 1.8rem; }
      .eyebrow { color: #e16f4e; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; font-size: .73rem; }
      .metric-card { background: white; border: 1px solid #e3eaf1; border-radius: 12px; padding: 1.15rem 1.25rem; min-height: 112px; box-shadow: 0 3px 18px rgba(16,42,67,.04); }
      .metric-label { color: #61758a; font-size: .85rem; }
      .metric-value { color: #102a43; font-size: 2rem; font-weight: 800; line-height: 1.2; }
      .metric-note { color: #0d6b68; font-size: .76rem; margin-top: .25rem; }
      .hospital-card { background: white; border: 1px solid #e3eaf1; border-left: 4px solid #0d6b68; border-radius: 10px; padding: 1rem 1.1rem; margin-bottom: .8rem; }
      .hospital-name { color: #102a43; font-size: 1.07rem; font-weight: 750; }
      .hospital-address { color: #61758a; font-size: .84rem; margin: .2rem 0 .75rem; }
      .tag { display: inline-block; background: #e9f5f2; color: #0d6b68; border-radius: 99px; padding: .25rem .55rem; margin-right: .35rem; font-size: .75rem; font-weight: 700; }
      .empty { background: #fff; border: 1px dashed #b9c7d5; padding: 2rem; border-radius: 12px; text-align: center; color: #61758a; }
      div[data-testid="stMetricValue"] { color: #102a43; }
      .stButton > button { border-radius: 8px; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)


def metric(label: str, value: int | str, note: str) -> None:
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)


def home_page() -> None:
    hospitals = list_hospitals()
    logs = get_search_logs()
    st.markdown('<div class="eyebrow">Mumbai care network</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand">Find care with confidence.</div>', unsafe_allow_html=True)
    st.markdown('<div class="subhead">A live view of hospital beds, critical care, and emergency resources near you.</div>', unsafe_allow_html=True)

    total_beds = sum(item.get("beds", 0) for item in hospitals)
    total_icu = sum(item.get("icu_beds", 0) for item in hospitals)
    total_vent = sum(item.get("ventilators", 0) for item in hospitals)
    cols = st.columns(4)
    for col, args in zip(cols, [("Hospitals tracked", len(hospitals), "Across Mumbai"), ("Open beds", total_beds, "Updated by hospitals"), ("ICU beds", total_icu, "Currently available"), ("Ventilators", total_vent, "Ready for allocation")]):
        with col:
            metric(*args)

    st.markdown("### Search availability")
    with st.form("search_form"):
        left, mid, right = st.columns([2, 1.25, 1])
        with left:
            area = st.text_input("Area or hospital", placeholder="Try Andheri, Bandra, or Mumbai")
        with mid:
            resource = st.selectbox("Need", ["Any resource", "beds", "icu_beds", "ventilators"], format_func=resource_label)
        with right:
            radius = st.slider("Radius (km)", 1, 30, 20)
        submitted = st.form_submit_button("Search hospitals", type="primary", use_container_width=True)

    if submitted or "search_results" not in st.session_state:
        results = search_hospitals(hospitals, area if submitted else "", resource, radius)
        st.session_state["search_results"] = results
        if submitted:
            log_search(area or "Mumbai", resource, len(results))
    else:
        results = st.session_state["search_results"]

    st.markdown(f"### {len(results)} hospitals available")
    if not results:
        st.markdown('<div class="empty">No matching hospitals found. Try a wider area or choose “Any resource”.</div>', unsafe_allow_html=True)
        return
    left, right = st.columns([1.15, 1])
    with left:
        for hospital in results:
            st.markdown(f'''<div class="hospital-card"><div class="hospital-name">{hospital['name']}</div><div class="hospital-address">{hospital['address']} · {hospital.get('distance_km', 0):.1f} km away</div><span class="tag">{hospital.get('beds', 0)} beds</span><span class="tag">{hospital.get('icu_beds', 0)} ICU</span><span class="tag">{hospital.get('ventilators', 0)} ventilators</span></div>''', unsafe_allow_html=True)
            st.link_button(f"Call {hospital['name']}", f"tel:{hospital.get('phone', '')}")
    with right:
        st.markdown("#### Availability map")
        map_data = pd.DataFrame([{"lat": h["lat"], "lon": h["lon"]} for h in results])
        st.map(map_data, zoom=10, use_container_width=True)


def analytics_page() -> None:
    hospitals = list_hospitals()
    logs = get_search_logs()
    st.markdown('<div class="eyebrow">Operations overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand">Resource analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="subhead">Understand availability and the needs people are searching for.</div>', unsafe_allow_html=True)
    if not hospitals:
        st.info("Add hospitals to view analytics.")
        return
    frame = pd.DataFrame(hospitals)
    a, b = st.columns(2)
    with a:
        st.markdown("#### Inventory by resource")
        chart = frame[["name", "beds", "icu_beds", "ventilators"]].set_index("name")
        st.bar_chart(chart, color=["#0d6b68", "#e16f4e", "#f2b134"])
    with b:
        st.markdown("#### Availability snapshot")
        summary = pd.DataFrame({"Resource": ["Beds", "ICU beds", "Ventilators"], "Available": [frame.beds.sum(), frame.icu_beds.sum(), frame.ventilators.sum()]})
        st.dataframe(summary, hide_index=True, use_container_width=True)
        st.metric("Searches recorded", len(logs))
    st.markdown("#### Recent searches")
    if logs:
        log_frame = pd.DataFrame(logs)
        log_frame["Resource"] = log_frame["resource"].map(resource_label)
        log_frame = log_frame.rename(columns={"area": "Area", "result_count": "Matches", "searched_at": "Time"})
        st.dataframe(log_frame[["Area", "Resource", "Matches", "Time"]].head(10), hide_index=True, use_container_width=True)
    else:
        st.info("Search activity will appear here after patients use the search page.")


inject_css()
ensure_demo_data()
with st.sidebar:
    st.markdown("## 🏥 CareMap")
    st.caption("Hospital resource availability")
    page = st.radio("Navigate", ["Patient search", "Analytics"], label_visibility="collapsed")
    st.divider()
    st.caption(f"Storage: {storage_mode()}")
    st.caption("For urgent emergencies, call local emergency services.")

if page == "Patient search":
    home_page()
else:
    analytics_page()
