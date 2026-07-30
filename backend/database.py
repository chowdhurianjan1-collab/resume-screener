"""
database.py — SQLAlchemy engine/session setup.

Defaults to a local SQLite file (zero setup). Swap DATABASE_URL in the
environment to point at Postgres/MySQL/etc. in production, e.g.:

    export DATABASE_URL="postgresql://user:pass@localhost:5432/resumes"
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_screener.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import models here so they register with Base before create_all runs.
    from models import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
