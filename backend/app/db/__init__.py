"""Database package: engine, session factory, and init."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base

# SQLite in project; can switch to postgres via env
_db_path = os.environ.get("DATABASE_URL", "sqlite:///./pcbuilder.db")
if _db_path.startswith("sqlite"):
    engine = create_engine(_db_path, connect_args={"check_same_thread": False})
else:
    engine = create_engine(_db_path)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
