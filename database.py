from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Use SQLite instead of PostgreSQL for easier setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Check if using SQLite and add connect_args if needed
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=True  # Enable SQL logging
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        echo=True  # Enable SQL logging
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency to get a database session that will be used throughout the request
    and closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()