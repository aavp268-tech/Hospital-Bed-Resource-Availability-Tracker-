"""F-3: Shared look and feel + the result-state screens (available / not available /
loading / error / empty) used across all patient-facing pages.

Import from any page:
    from utils.ui import apply_theme, page_header, render_not_available, render_error, render_empty_state

apply_theme() should be the first call after st.set_page_config() on every page,
so the whole app looks consistent instead of each page inventing its own style.
"""
from __future__ import annotations

import streamlit as st

BRAND = "#0d6b68"
ACCENT = "#e16f4e"
INK = "#102a43"
MUTED = "#61758a"
BORDER = "#e3eaf1"
BG = "#f7f9fc"


def apply_theme() -> None:
    """Consistent colours, cards and buttons across every page. Call once per page."""
    st.markdown(
        f"""
        <style>
          .stApp {{ background: {BG}; }}
          [data-testid="stSidebar"] {{ background: {INK}; }}
          [data-testid="stSidebar"] * {{ color: #f4f7fb !important; }}
          .eyebrow {{ color: {ACCENT}; font-weight: 800; letter-spacing: .12em;
                      text-transform: uppercase; font-size: .73rem; }}
          .brand {{ color: {BRAND}; font-size: 2.2rem; font-weight: 800;
                    letter-spacing: -0.03em; margin: .2rem 0 .1rem; }}
          .subhead {{ color: {MUTED}; font-size: 1rem; margin: 0 0 1.4rem; }}
          .state-card {{ background: white; border: 1px solid {BORDER}; border-radius: 12px;
                         padding: 1.4rem 1.4rem; text-align: center; }}
          .state-card.warn {{ border-left: 4px solid {ACCENT}; }}
          .state-card.error {{ border-left: 4px solid #c0392b; }}
          .stButton > button, .stFormSubmitButton > button {{ border-radius: 8px; font-weight: 700; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    """Consistent page title block: small eyebrow label, big brand-coloured title, subtitle."""
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="brand">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="subhead">{subtitle}</div>', unsafe_allow_html=True)


# ---------- result states ----------

def render_loading(message: str = "Searching hospitals...") -> None:
    """Use as: with st.spinner(""): render_loading() — or just call st.spinner(message) directly.
    Kept here so every page uses the same wording."""
    st.info(f"⏳ {message}")


def render_error(message: str) -> None:
    """The database is unreachable, or something else went wrong. Never show a raw traceback."""
    st.markdown(
        f'<div class="state-card error">'
        f'<h4>⚠️ Something went wrong</h4>'
        f'<p style="color:{MUTED}">{message}</p>'
        f'<p style="color:{MUTED}">Please try again in a moment. If this keeps happening, '
        f'tell whoever set up the database.</p>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    """Before the patient has searched at all."""
    st.markdown(
        f'<div class="state-card">'
        f'<h4>🔎 Start by searching</h4>'
        f'<p style="color:{MUTED}">Pick your area and the resource you need, then tap Search.</p>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_not_available(all_results: list[dict], resource: str, radius_km: int, render_card) -> None:
    """The 'not available' screen from the flowchart.

    all_results -- every hospital with the resource, at any distance, nearest first
                    (this is st.session_state["search_all"] from the search page)
    render_card -- a function(hospital) -> None that draws one result card;
                    passed in so this stays in sync with however F-1 styles a card
    """
    st.markdown(
        f'<div class="state-card warn">'
        f"<h4>😕 No {resource.lower()} available within {radius_km} km</h4>"
        f'<p style="color:{MUTED}">Availability changes quickly — try a wider radius, '
        f"a different resource, or call a hospital directly.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    if all_results:
        st.markdown("#### Nearest hospitals that do have it")
        for hospital in all_results[:3]:
            render_card(hospital)
    else:
        st.warning(
            "No hospital currently reports this resource available. "
            "Try 'Any' as the resource, or call a hospital directly for the latest status."
        )