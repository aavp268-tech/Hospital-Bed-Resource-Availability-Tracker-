"""Location helpers: known Mumbai areas and distances. Works offline (no geocoding service)."""
from __future__ import annotations

from geopy.distance import geodesic

# Approximate centre points of common Mumbai areas as (latitude, longitude).
# Good enough for a demo search; add more areas as needed.
MUMBAI_AREAS: dict[str, tuple[float, float]] = {
    "Andheri East": (19.1136, 72.8697),
    "Andheri West": (19.1364, 72.8296),
    "Bandra East": (19.0596, 72.8656),
    "Bandra West": (19.0596, 72.8295),
    "Borivali": (19.2307, 72.8567),
    "Byculla": (18.9760, 72.8330),
    "Chembur": (19.0522, 72.9005),
    "Churchgate": (18.9322, 72.8264),
    "Colaba": (18.9067, 72.8147),
    "Dadar": (19.0178, 72.8478),
    "Fort": (18.9340, 72.8350),
    "Ghatkopar": (19.0860, 72.9080),
    "Goregaon": (19.1663, 72.8526),
    "Grant Road": (18.9640, 72.8150),
    "Jogeshwari": (19.1361, 72.8493),
    "Kandivali": (19.2043, 72.8478),
    "Khar": (19.0700, 72.8360),
    "Kurla": (19.0728, 72.8826),
    "Lower Parel": (18.9930, 72.8300),
    "Mahim": (19.0330, 72.8407),
    "Malad": (19.1874, 72.8484),
    "Marine Lines": (18.9440, 72.8230),
    "Matunga": (19.0270, 72.8570),
    "Mulund": (19.1726, 72.9560),
    "Mumbai Central": (18.9690, 72.8205),
    "Parel": (19.0027, 72.8410),
    "Powai": (19.1176, 72.9060),
    "Santacruz": (19.0810, 72.8410),
    "Sion": (19.0390, 72.8619),
    "Vikhroli": (19.1110, 72.9270),
    "Vile Parle": (19.0990, 72.8440),
    "Worli": (19.0176, 72.8153),
}

_LOOKUP = {name.lower(): name for name in MUMBAI_AREAS}


def list_areas() -> list[str]:
    """Area names in alphabetical order, ready for a dropdown."""
    return sorted(MUMBAI_AREAS)


def resolve_area(name: str) -> tuple[float, float] | None:
    """Return (lat, lon) for an area name (case-insensitive), or None if unknown."""
    canonical = _LOOKUP.get(name.strip().lower())
    return MUMBAI_AREAS[canonical] if canonical else None


def distance_km(origin: tuple[float, float], destination: tuple[float, float]) -> float:
    """Distance in kilometres between two (lat, lon) points, using geopy's geodesic."""
    return geodesic(origin, destination).km