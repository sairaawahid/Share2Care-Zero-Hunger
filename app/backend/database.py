from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
import os

# Load .env if it exists (safe even if missing)
load_dotenv()

# Try to read DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL")

# If no .env or env variable found, fallback to SQLite
if not database_url:
    database_url = "sqlite:///./share2care_local.db"

# Engine setup
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, echo=True, connect_args=connect_args)

# Initialize database models
def init_db():
    SQLModel.metadata.create_all(engine)
