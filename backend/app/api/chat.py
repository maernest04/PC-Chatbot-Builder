"""Chat and sessions API."""

import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db, init_db
from app.db.sessions import (
    add_message,
    create_build,
    create_session,
    get_latest_build,
    get_messages,
    get_session,
    list_sessions,
    update_session_title,
)
from app.graph.graph import compile_graph

router = APIRouter(prefix="/api", tags=["chat"])

# Compile graph once at module load (checkpointer is shared)
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = compile_graph(use_checkpointer=True)
    return _graph


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    build: dict | None = None


def _db_messages_to_langchain(messages: list) -> list:
    out = []
    for m in messages:
        if m.role == "user":
            out.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            out.append(AIMessage(content=m.content))
    return out


@router.post("/chat", response_model=ChatResponse)
def post_chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Send a message and get the assistant reply. Creates a session if session_id is omitted."""
    init_db()

    if req.session_id:
        session = get_session(db, req.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = create_session(db)
        # First message: use a short title from the user message
        title = (req.message[:50] + "..." if len(req.message) > 50 else req.message) or "New build"
        update_session_title(db, session.id, title)

    session_id = session.id
    add_message(db, session_id, "user", req.message)

    # Load conversation from DB and append new user message
    db_messages = get_messages(db, session_id)
    lc_messages = _db_messages_to_langchain(db_messages)

    config = {"configurable": {"thread_id": session_id, "db": db}}
    graph = get_graph()

    try:
        result = graph.invoke({"messages": lc_messages}, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    messages = result.get("messages") or []
    # Last message from assistant (skip ToolMessages)
    reply = ""
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            reply = m.content or ""
            break

    add_message(db, session_id, "assistant", reply)

    # Optionally detect build in reply and save (e.g. if we add structured output later)
    build = None
    latest = get_latest_build(db, session_id)
    if latest:
        build = {
            "id": latest.id,
            "parts": latest.parts,
            "subtotal": latest.subtotal,
            "tax_rate": latest.tax_rate,
            "total": latest.total,
        }

    return ChatResponse(session_id=session_id, reply=reply, build=build)


@router.get("/sessions")
def get_sessions_list(db: Session = Depends(get_db)):
    """List recent sessions for chat history."""
    init_db()
    sessions = list_sessions(db)
    return [
        {"id": s.id, "title": s.title or "New build", "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat()}
        for s in sessions
    ]


@router.get("/sessions/{session_id}")
def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    """Get a session with its messages and latest build."""
    init_db()
    session = get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = get_messages(db, session_id)
    latest = get_latest_build(db, session_id)
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat(),
        "messages": [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages],
        "build": (
            {
                "id": latest.id,
                "parts": latest.parts,
                "subtotal": latest.subtotal,
                "tax_rate": latest.tax_rate,
                "total": latest.total,
            }
            if latest
            else None
        ),
    }


@router.get("/builds/{build_id}")
def get_build_detail(build_id: str, db: Session = Depends(get_db)):
    """Get a build by id."""
    init_db()
    from app.db.sessions import get_build
    build = get_build(db, build_id)
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return {
        "id": build.id,
        "session_id": build.session_id,
        "parts": build.parts,
        "subtotal": build.subtotal,
        "tax_rate": build.tax_rate,
        "total": build.total,
        "created_at": build.created_at.isoformat(),
    }
