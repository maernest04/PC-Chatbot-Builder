"""Seed or refresh parts table from data/parts_seed.json. Run from project root: python -m backend.scripts.refresh_parts or from backend: python scripts/refresh_parts.py."""

import json
import os
import sys

# Ensure backend (so app) is on path when run as script from project root or backend
_script_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_script_dir)
sys.path.insert(0, _backend_dir)
sys.path.insert(0, os.path.dirname(_backend_dir))

from app.db import init_db, SessionLocal
from app.db.parts import upsert_parts


def main() -> None:
    # Project root: parent of backend/
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_dir)
    seed_path = os.path.join(project_root, "data", "parts_seed.json")
    if not os.path.exists(seed_path):
        seed_path = os.path.join(backend_dir, "..", "data", "parts_seed.json")
    if not os.path.exists(seed_path):
        print("parts_seed.json not found in data/")
        sys.exit(1)

    init_db()
    with open(seed_path) as f:
        parts = json.load(f)
    db = SessionLocal()
    try:
        count = upsert_parts(db, parts)
        print(f"Upserted {count} new parts (existing ones updated in place). Total records in seed: {len(parts)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
