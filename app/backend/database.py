from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from app.backend.config import PROJECT_DIR

# DB file: app/backend/data/share2care.db
DB_DIR = Path(PROJECT_DIR) / "app" / "backend" / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DB_DIR / "share2care.db"

DATABASE_URL = f"sqlite:///{DB_FILE}"

# create engine (check_same_thread False to work with FastAPI)
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db() -> None:
    """Create DB tables. Import models before calling this."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency: yield a SQLModel Session."""
    with Session(engine) as session:
        yield session
