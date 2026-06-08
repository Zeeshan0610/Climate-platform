"""Database initialization: create tables, seed admin user, run ETL seed."""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db import models
from app.db.session import Base, SessionLocal, engine
from app.etl import pipeline

logger = logging.getLogger("init_db")


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def seed_admin(db: Session) -> None:
    existing = db.query(models.User).filter_by(username=settings.FIRST_ADMIN_USERNAME).first()
    if existing:
        return
    admin = models.User(
        username=settings.FIRST_ADMIN_USERNAME,
        email=settings.FIRST_ADMIN_EMAIL,
        hashed_password=hash_password(settings.FIRST_ADMIN_PASSWORD),
        role="admin",
    )
    db.add(admin)
    # Demo analyst & viewer accounts for RBAC demonstration
    db.add(
        models.User(
            username="analyst",
            email="analyst@climate.example.com",
            hashed_password=hash_password("analyst123"),
            role="analyst",
        )
    )
    db.add(
        models.User(
            username="viewer",
            email="viewer@climate.example.com",
            hashed_password=hash_password("viewer123"),
            role="viewer",
        )
    )
    db.commit()
    logger.info("Seeded default users (admin/analyst/viewer)")


def seed_data(db: Session) -> None:
    if db.query(models.ClimateRecord).count() > 0:
        return
    logger.info("Running ETL pipeline to seed climate data ...")
    summary = pipeline.run_etl(db, regenerate=True)
    logger.info("ETL seed complete: %s", summary)


def init() -> None:
    create_tables()
    db = SessionLocal()
    try:
        seed_admin(db)
        if settings.SEED_ON_STARTUP:
            seed_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init()
