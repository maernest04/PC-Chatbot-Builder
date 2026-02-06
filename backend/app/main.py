"""FastAPI application for PC Builder backend."""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env from project root so running from backend/ still finds it
# __file__ = backend/app/main.py -> parent.parent = backend, parent.parent.parent = project root
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from app.api.chat import router as chat_router
from app.db import init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PC Builder API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}
