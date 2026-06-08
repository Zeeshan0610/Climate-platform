"""Climate analytics: trends, distributions, and statistical summaries."""
from __future__ import annotations

import numpy as np
import pandas as pd


def monthly_trends(df: pd.DataFrame) -> dict:
    """Average temperature/rainfall/humidity per month across the dataset."""
    if df.empty:
        return {"series": []}
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"], errors="coerce")
    d = d.dropna(subset=["date"])
    d["month"] = d["date"].dt.to_period("M").dt.to_timestamp()
    grouped = (
        d.groupby("month")[["temperature", "rainfall", "humidity"]]
        .mean()
        .round(2)
        .reset_index()
    )
    series = [
        {
            "month": row["month"].strftime("%Y-%m"),
            "temperature": _clean(row["temperature"]),
            "rainfall": _clean(row["rainfall"]),
            "humidity": _clean(row["humidity"]),
        }
        for _, row in grouped.iterrows()
    ]
    return {"series": series}


def country_distribution(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"distribution": []}
    grouped = (
        df.groupby("country")[["temperature", "rainfall", "humidity"]]
        .mean()
        .round(2)
        .reset_index()
    )
    counts = df.groupby("country").size()
    dist = [
        {
            "country": row["country"],
            "avg_temperature": _clean(row["temperature"]),
            "avg_rainfall": _clean(row["rainfall"]),
            "avg_humidity": _clean(row["humidity"]),
            "records": int(counts.get(row["country"], 0)),
        }
        for _, row in grouped.iterrows()
    ]
    return {"distribution": dist}


def statistics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"stats": {}}
    stats = {}
    for col in ["temperature", "rainfall", "humidity"]:
        if col in df.columns:
            s = df[col].dropna()
            if len(s):
                stats[col] = {
                    "mean": round(float(s.mean()), 2),
                    "median": round(float(s.median()), 2),
                    "variance": round(float(s.var()), 2),
                    "std": round(float(s.std()), 2),
                    "min": round(float(s.min()), 2),
                    "max": round(float(s.max()), 2),
                }
    return {"stats": stats}


def _clean(value) -> float | None:
    if value is None or (isinstance(value, float) and (np.isnan(value))):
        return None
    return round(float(value), 2)
