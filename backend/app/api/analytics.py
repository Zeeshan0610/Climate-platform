"""Analytics endpoints: trends, distributions, statistics, ML training."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models
from app.db.session import get_db
from app.ml import prediction
from app.services import analytics
from app.services.dataframe import records_to_df

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("")
def get_analytics(
    country: str | None = None,
    source: str | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    df = records_to_df(db, country=country, source=source, year=year)
    return {
        "trends": analytics.monthly_trends(df),
        "distribution": analytics.country_distribution(df),
        "statistics": analytics.statistics(df),
    }


@router.get("/trends")
def get_trends(
    country: str | None = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    df = records_to_df(db, country=country)
    return analytics.monthly_trends(df)


@router.get("/ml")
def get_ml(
    target: str = "temperature",
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    df = records_to_df(db)
    return prediction.train_and_evaluate(df, target=target)
