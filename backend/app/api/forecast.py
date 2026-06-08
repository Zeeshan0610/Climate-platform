"""Forecasting endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models
from app.db.session import get_db
from app.ml import forecasting
from app.services.dataframe import records_to_df

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("")
def get_forecast(
    metric: str = Query("temperature", pattern="^(temperature|rainfall|humidity)$"),
    periods: int = Query(12, ge=1, le=36),
    country: str | None = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    df = records_to_df(db, country=country)
    return forecasting.forecast_metric(df, metric=metric, periods=periods)
