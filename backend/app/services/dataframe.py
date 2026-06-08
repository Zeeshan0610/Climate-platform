"""Helpers to load climate records from the DB into a pandas DataFrame."""
from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.db import models


def records_to_df(
    db: Session,
    country: str | None = None,
    source: str | None = None,
    year: int | None = None,
) -> pd.DataFrame:
    q = db.query(models.ClimateRecord)
    if country:
        q = q.filter(models.ClimateRecord.country == country)
    if source:
        q = q.filter(models.ClimateRecord.source == source)
    rows = q.all()
    data = [
        {
            "record_id": r.record_id,
            "country": r.country,
            "region": r.region,
            "date": r.date,
            "temperature": r.temperature,
            "rainfall": r.rainfall,
            "humidity": r.humidity,
            "source": r.source,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if year:
            df = df[df["date"].dt.year == year]
    return df
