"""Audit logging helper."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db import models


def log(
    db: Session,
    action: str,
    user: models.User | None = None,
    resource: str | None = None,
    detail: str | None = None,
) -> None:
    entry = models.AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else None,
        action=action,
        resource=resource,
        detail=detail,
    )
    db.add(entry)
    db.commit()
