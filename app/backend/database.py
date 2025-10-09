from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
import os

# Database configuration
DB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'share2care.db')}"

engine = create_engine(DATABASE_URL, echo=False)

# Initialize DB
def init_db():
    """Creates all tables if they don’t exist."""
    from app.backend import models  # local import to avoid circular dependency
    SQLModel.metadata.create_all(engine)
    print("✅ Database initialized and tables created.")

# Session Dependency
@contextmanager
def get_session():
    """Yields a new SQLAlchemy session (used by FastAPI Depends)."""
    with Session(engine) as session:
        yield session
