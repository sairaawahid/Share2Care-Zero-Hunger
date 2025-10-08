from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from app.backend.config import PROJECT_DIR

# DB file placed under app/backend/data/share2care.db
DB_DIR = Path(PROJECT_DIR) / "app" / "backend" / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DB_DIR / "share2care.db"

DATABASE_URL = f"sqlite:///{DB_FILE}"

# SQLite engine (check_same_thread False required for FastAPI concurrency)
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db() -> None:
    """
    Create tables (SQLModel models must be imported before calling this).
    Call on startup.
    """
    SQLModel.metadata.create_all(engine)

# Dependency to use in routes
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

