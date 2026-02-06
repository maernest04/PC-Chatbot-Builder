"""CRUD for parts table."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Part


def search_parts(
    db: Session,
    category: str | None = None,
    max_price: float | None = None,
    limit: int = 20,
) -> list[Part]:
    """Return parts filtered by category and optional max price."""
    q = select(Part).order_by(Part.price_usd)
    if category:
        q = q.where(Part.category == category)
    if max_price is not None:
        q = q.where(Part.price_usd <= max_price)
    q = q.limit(limit)
    return list(db.execute(q).scalars().all())


def get_part_by_id(db: Session, part_id: str) -> Part | None:
    """Return a part by id or None."""
    return db.get(Part, part_id)


def upsert_parts(db: Session, parts: list[dict]) -> int:
    """Insert or update parts from list of dicts (category, name, price_usd, link, specs). Returns count."""
    count = 0
    for p in parts:
        existing = db.execute(
            select(Part).where(Part.category == p["category"]).where(Part.name == p["name"])
        ).scalars().first()
        if existing:
            existing.price_usd = float(p["price_usd"])
            existing.link = p.get("link")
            existing.specs = p.get("specs")
        else:
            db.add(
                Part(
                    category=p["category"],
                    name=p["name"],
                    price_usd=float(p["price_usd"]),
                    link=p.get("link"),
                    specs=p.get("specs"),
                )
            )
            count += 1
    db.commit()
    return count
