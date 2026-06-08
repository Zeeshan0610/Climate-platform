"""Shared API dependencies: current user resolution and RBAC guards."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, role_allows
from app.db import models
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exc
    user = db.query(models.User).filter_by(username=payload["sub"]).one_or_none()
    if user is None or not user.is_active:
        raise credentials_exc
    return user


def require_role(required_role: str):
    """Dependency factory enforcing a minimum role."""

    def _guard(user: models.User = Depends(get_current_user)) -> models.User:
        if not role_allows(user.role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role '{required_role}' or higher",
            )
        return user

    return _guard
