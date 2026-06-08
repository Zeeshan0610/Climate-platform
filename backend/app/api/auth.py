"""Authentication & user management endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.security import create_access_token, hash_password, verify_password
from app.db import models
from app.db.session import get_db
from app.schemas.auth import Token, UserCreate, UserOut
from app.services import audit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=form.username).one_or_none()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password"
        )
    token = create_access_token(subject=user.username, role=user.role)
    audit.log(db, action="login", user=user, resource="auth")
    return Token(access_token=token, role=user.role, username=user.username)


@router.get("/me", response_model=UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_role("admin")),
):
    if payload.role not in {"viewer", "analyst", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    if db.query(models.User).filter_by(username=payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = models.User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    audit.log(db, action="create_user", user=admin, resource=f"user:{user.username}")
    return user


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db), admin: models.User = Depends(require_role("admin"))
):
    return db.query(models.User).order_by(models.User.id).all()
