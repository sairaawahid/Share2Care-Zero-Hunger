# app/backend/database.py
from sqlmodel import SQLModel, create_engine, Session
import os

# SQLite database file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'share2care.db')}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

# Initialize DB schema
def init_db():
    SQLModel.metadata.create_all(engine)

# Dependency for FastAPI routes
def get_session():
    with Session(engine) as session:
        yield session
