from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os

# Use environment variable DATABASE_URL (recommended)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://therapy:therapy123@localhost:5432/therapybot"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize tables (if they don’t exist)
def init_db():
    Base.metadata.create_all(bind=engine)
