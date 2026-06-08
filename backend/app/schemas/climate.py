"""Pydantic schemas for climate records and analytics responses."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class ClimateRecordOut(BaseModel):
    record_id: int
    country: str
    region: str | None
    date: date
    temperature: float | None
    rainfall: float | None
    humidity: float | None
    source: str

    model_config = {"from_attributes": True}


class ClimateRecordPage(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ClimateRecordOut]


class DatasetOut(BaseModel):
    id: int
    name: str
    source: str
    fmt: str
    description: str | None
    raw_record_count: int
    loaded_record_count: int
    ingested_at: datetime

    model_config = {"from_attributes": True}


class HomeStats(BaseModel):
    total_records: int
    total_countries: int
    total_datasets: int
    average_temperature: float | None
    average_rainfall: float | None
    average_humidity: float | None
    overall_quality_score: float
    accessibility_score: float
    interoperability_score: float
