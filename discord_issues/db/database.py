import logging

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///db.sqlite3"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initializes the database by applying all Alembic migrations.
    This ensures the database schema is up-to-date with the models.
    """
    logging.info("Checking database migrations...")

    # Path to your alembic.ini file
    alembic_cfg = Config("alembic.ini")

    # Programmatically run 'alembic upgrade head'
    command.upgrade(alembic_cfg, "head")

    logging.info("Database migrations are up to date.")
