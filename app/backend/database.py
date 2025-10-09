# app/backend/database.py
import os
from pathlib import Path
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# Load .env in local dev (optional)
load_dotenv()

# Project paths — keep existing semantics
PROJECT_DIR = Path(__file__).resolve().parents[2]

# Local sqlite default DB file (safe fallback)
DB_DIR = PROJECT_DIR / "app" / "backend" / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_FILE = DB_DIR / "share2care.db"
DEFAULT_SQLITE_URL = f"sqlite:///{SQLITE_FILE}"

# Use DATABASE_URL env var if set, otherwise fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL).strip()

# sqlite needs connect_args; postgres does not
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create engine (pool_pre_ping keeps idle connections healthy)
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True
)

def init_db() -> None:
    """
    Create tables from SQLModel metadata. Call this on startup (you already do).
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Use as FastAPI dependency: Depends(get_session)
    """
    with Session(engine) as session:
        yield session
