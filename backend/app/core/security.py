"""Authentication & authorization: password hashing, JWT, RBAC."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, role: str, expires_minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# Role hierarchy: admin can do everything an analyst can, analyst everything a viewer can.
ROLE_LEVELS = {"viewer": 1, "analyst": 2, "admin": 3}


def role_allows(user_role: str, required_role: str) -> bool:
    return ROLE_LEVELS.get(user_role, 0) >= ROLE_LEVELS.get(required_role, 99)


def roles_at_least(required_role: str) -> Iterable[str]:
    level = ROLE_LEVELS.get(required_role, 99)
    return [r for r, lv in ROLE_LEVELS.items() if lv >= level]
