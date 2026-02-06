"""CRUD for sessions, messages, and builds."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Build, Message, Session as SessionModel


def create_session(db: Session, title: str | None = None) -> SessionModel:
    """Create a new chat session."""
    s = SessionModel(title=title or "New build")
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def get_session(db: Session, session_id: str) -> SessionModel | None:
    """Get session by id."""
    return db.get(SessionModel, session_id)


def list_sessions(db: Session, limit: int = 50) -> list[SessionModel]:
    """List sessions by updated_at desc."""
    q = select(SessionModel).order_by(SessionModel.updated_at.desc()).limit(limit)
    return list(db.execute(q).scalars().all())


def add_message(db: Session, session_id: str, role: str, content: str) -> Message:
    """Append a message to a session."""
    m = Message(session_id=session_id, role=role, content=content)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def get_messages(db: Session, session_id: str) -> list[Message]:
    """Get all messages for a session in order."""
    q = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    return list(db.execute(q).scalars().all())


def update_session_title(db: Session, session_id: str, title: str) -> None:
    """Set session title (e.g. from first user message)."""
    s = db.get(SessionModel, session_id)
    if s:
        s.title = title[:256] if len(title) > 256 else title
        db.commit()


def create_build(
    db: Session,
    session_id: str,
    parts: list[dict],
    subtotal: float,
    tax_rate: float,
    total: float,
) -> Build:
    """Save a build for a session."""
    b = Build(
        session_id=session_id,
        parts=parts,
        subtotal=subtotal,
        tax_rate=tax_rate,
        total=total,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def get_latest_build(db: Session, session_id: str) -> Build | None:
    """Get the most recent build for a session."""
    q = (
        select(Build)
        .where(Build.session_id == session_id)
        .order_by(Build.created_at.desc())
        .limit(1)
    )
    return db.execute(q).scalars().first()


def get_build(db: Session, build_id: str) -> Build | None:
    """Get build by id."""
    return db.get(Build, build_id)
