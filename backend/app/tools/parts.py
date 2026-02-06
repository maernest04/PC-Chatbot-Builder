"""Part search tool: query parts from DB by category and max price."""

from sqlalchemy.orm import Session

from app.db.parts import search_parts as db_search_parts


def search_parts(
    db: Session,
    category: str,
    max_price: float | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search parts by category and optional max price.
    Returns list of dicts with id, category, name, price_usd, link.
    """
    parts = db_search_parts(db, category=category, max_price=max_price, limit=limit)
    return [
        {
            "id": p.id,
            "category": p.category,
            "name": p.name,
            "price_usd": p.price_usd,
            "link": p.link,
        }
        for p in parts
    ]
