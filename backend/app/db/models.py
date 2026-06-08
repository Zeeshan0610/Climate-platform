"""ORM models for the climate data platform.

Schema overview (also see docs/ER_DIAGRAM.md):
  - users               : authentication & RBAC
  - audit_logs          : audit trail of user/system actions
  - datasets            : registered source datasets and ingestion metadata
  - climate_records     : unified, harmonized climate observations
  - data_quality_metrics: per-dataset data quality scores
  - interoperability_metrics : pairwise/source schema & semantic compatibility
  - reliability_metrics : per-dataset reliability scores
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), default="viewer", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource: Mapped[str | None] = mapped_column(String(128), nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, index=True)


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    fmt: Mapped[str] = mapped_column(String(16), default="csv")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_record_count: Mapped[int] = mapped_column(Integer, default=0)
    loaded_record_count: Mapped[int] = mapped_column(Integer, default=0)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    records: Mapped[list["ClimateRecord"]] = relationship(back_populates="dataset")
    quality_metrics: Mapped[list["DataQualityMetric"]] = relationship(back_populates="dataset")


class ClimateRecord(Base):
    __tablename__ = "climate_records"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int | None] = mapped_column(ForeignKey("datasets.id"), index=True)
    country: Mapped[str] = mapped_column(String(128), index=True)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)  # Celsius
    rainfall: Mapped[float | None] = mapped_column(Float, nullable=True)  # millimeters
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)  # percent
    source: Mapped[str] = mapped_column(String(128), index=True)

    dataset: Mapped["Dataset"] = relationship(back_populates="records")


class DataQualityMetric(Base):
    __tablename__ = "data_quality_metrics"

    metric_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int | None] = mapped_column(ForeignKey("datasets.id"), index=True)
    dataset_name: Mapped[str] = mapped_column(String(128))
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0)
    consistency_score: Mapped[float] = mapped_column(Float, default=0.0)
    validity_score: Mapped[float] = mapped_column(Float, default=0.0)
    accuracy_score: Mapped[float] = mapped_column(Float, default=0.0)
    timeliness_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    duplicates_removed: Mapped[int] = mapped_column(Integer, default=0)
    outliers_detected: Mapped[int] = mapped_column(Integer, default=0)
    missing_imputed: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="quality_metrics")


class InteroperabilityMetric(Base):
    __tablename__ = "interoperability_metrics"

    metric_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_a: Mapped[str] = mapped_column(String(128))
    source_b: Mapped[str] = mapped_column(String(128))
    schema_compatibility: Mapped[float] = mapped_column(Float, default=0.0)
    semantic_compatibility: Mapped[float] = mapped_column(Float, default=0.0)
    mapping_success_rate: Mapped[float] = mapped_column(Float, default=0.0)
    integration_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class ReliabilityMetric(Base):
    __tablename__ = "reliability_metrics"

    metric_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(128))
    completeness: Mapped[float] = mapped_column(Float, default=0.0)
    consistency: Mapped[float] = mapped_column(Float, default=0.0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    availability: Mapped[float] = mapped_column(Float, default=0.0)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
