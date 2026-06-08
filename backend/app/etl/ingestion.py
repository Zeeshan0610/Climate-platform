"""Data ingestion layer: batch (CSV/JSON), API, and incremental loading."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests


def ingest_csv(path: str | Path) -> pd.DataFrame:
    """Batch ingest a CSV file."""
    return pd.read_csv(path)


def ingest_json(path: str | Path) -> pd.DataFrame:
    """Batch ingest a JSON file (array of records)."""
    return pd.read_json(path)


def ingest_api(url: str, params: dict | None = None, timeout: int = 30) -> pd.DataFrame:
    """API ingestion. Expects the endpoint to return a JSON array of records."""
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    payload = resp.json()
    if isinstance(payload, dict) and "data" in payload:
        payload = payload["data"]
    return pd.DataFrame(payload)


def ingest(path_or_url: str | Path, fmt: str) -> pd.DataFrame:
    """Dispatch ingestion based on declared format."""
    fmt = fmt.lower()
    if fmt == "csv":
        return ingest_csv(path_or_url)
    if fmt == "json":
        return ingest_json(path_or_url)
    if fmt == "api":
        return ingest_api(str(path_or_url))
    raise ValueError(f"Unsupported ingestion format: {fmt}")


def incremental_filter(df: pd.DataFrame, date_col: str, since: str | None) -> pd.DataFrame:
    """Incremental loading helper: keep only rows newer than ``since``."""
    if since is None or date_col not in df.columns:
        return df
    parsed = pd.to_datetime(df[date_col], errors="coerce")
    return df[parsed > pd.to_datetime(since)]
