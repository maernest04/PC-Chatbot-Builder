"""Build tools: compute total with tax, replace part in build."""

from sqlalchemy.orm import Session

from app.db.parts import get_part_by_id

# State abbreviation -> sales tax rate (decimal). Subset of US states; no tax = 0.
US_STATE_TAX_RATES: dict[str, float] = {
    "AL": 0.04, "AZ": 0.056, "AR": 0.065, "CA": 0.0725, "CO": 0.029,
    "CT": 0.0635, "DE": 0.0, "FL": 0.06, "GA": 0.04, "HI": 0.04,
    "ID": 0.06, "IL": 0.0625, "IN": 0.07, "IA": 0.06, "KS": 0.065,
    "KY": 0.06, "LA": 0.0445, "ME": 0.055, "MD": 0.06, "MA": 0.0625,
    "MI": 0.06, "MN": 0.065, "MS": 0.05, "MO": 0.04225, "MT": 0.0,
    "NE": 0.055, "NV": 0.0685, "NH": 0.0, "NJ": 0.06625, "NM": 0.05125,
    "NY": 0.04, "NC": 0.03, "ND": 0.05, "OH": 0.0575, "OK": 0.045,
    "OR": 0.0, "PA": 0.06, "RI": 0.07, "SC": 0.06, "SD": 0.045,
    "TN": 0.07, "TX": 0.0625, "UT": 0.061, "VT": 0.06, "VA": 0.053,
    "WA": 0.065, "WV": 0.06, "WI": 0.05, "WY": 0.04, "DC": 0.06,
}


def get_tax_rate(region: str) -> float:
    """Return tax rate for US state/region (e.g. CA, California)."""
    region = (region or "").strip().upper()
    if len(region) == 2:
        return US_STATE_TAX_RATES.get(region, 0.0)
    # Map full name to abbrev
    state_names: dict[str, str] = {
        "ALABAMA": "AL", "ARIZONA": "AZ", "ARKANSAS": "AR", "CALIFORNIA": "CA",
        "COLORADO": "CO", "CONNECTICUT": "CT", "DELAWARE": "DE", "FLORIDA": "FL",
        "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID", "ILLINOIS": "IL",
        "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS", "KENTUCKY": "KY",
        "LOUISIANA": "LA", "MAINE": "ME", "MARYLAND": "MD", "MASSACHUSETTS": "MA",
        "MICHIGAN": "MI", "MINNESOTA": "MN", "MISSISSIPPI": "MS", "MISSOURI": "MO",
        "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV", "NEW HAMPSHIRE": "NH",
        "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY", "NORTH CAROLINA": "NC",
        "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK", "OREGON": "OR",
        "PENNSYLVANIA": "PA", "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC",
        "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX", "UTAH": "UT",
        "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
        "WISCONSIN": "WI", "WYOMING": "WY", "DISTRICT OF COLUMBIA": "DC",
    }
    return US_STATE_TAX_RATES.get(state_names.get(region, ""), 0.0)


def get_build_total(
    db: Session,
    part_ids: list[str],
    region: str,
) -> dict:
    """
    Compute subtotal, tax rate, and total for a list of part IDs and a US region.
    Returns dict: subtotal, tax_rate, total, parts (list of part snapshots).
    """
    parts_snapshots: list[dict] = []
    subtotal = 0.0
    for pid in part_ids:
        part = get_part_by_id(db, pid)
        if part:
            snap = {"id": part.id, "category": part.category, "name": part.name, "price_usd": part.price_usd, "link": part.link}
            parts_snapshots.append(snap)
            subtotal += part.price_usd
    tax_rate = get_tax_rate(region)
    total = round(subtotal * (1 + tax_rate), 2)
    return {
        "subtotal": round(subtotal, 2),
        "tax_rate": tax_rate,
        "total": total,
        "parts": parts_snapshots,
    }


def replace_part_in_build(
    db: Session,
    current_parts: list[dict],
    category: str,
    new_part_id: str,
) -> list[dict]:
    """
    Replace the part in current_parts for the given category with the part identified by new_part_id.
    current_parts and return value are lists of part snapshots (dict with id, category, name, price_usd, link).
    """
    part = get_part_by_id(db, new_part_id)
    if not part:
        return current_parts
    snap = {"id": part.id, "category": part.category, "name": part.name, "price_usd": part.price_usd, "link": part.link}
    out = []
    replaced = False
    for p in current_parts:
        if p.get("category") == category:
            if not replaced:
                out.append(snap)
                replaced = True
        else:
            out.append(p)
    if not replaced:
        out.append(snap)
    return out
