# app/backend/database.py
import os
from pathlib import Path
from typing import Generator
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

# Load .env (if present)
load_dotenv()

# Read DATABASE_URL from env; fallback to local sqlite for dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/share2care.db")

# Ensure directory exists for SQLite fallback
if DATABASE_URL.startswith("sqlite"):
    # create folder for the sqlite file if necessary
    sqlite_path = Path(DATABASE_URL.replace("sqlite:///", ""))
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

# Sqlite requires connect_args; Postgres does not
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

def init_db() -> None:
    """Create tables from SQLModel models (call on startup)."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency to use in FastAPI routes."""
    with Session(engine) as session:
        yield session
