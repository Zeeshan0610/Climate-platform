"""Climate data endpoints: records, datasets, home stats, ETL integration."""
from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db import models
from app.db.session import get_db
from app.etl import data_quality, harmonization, pipeline
from app.schemas.climate import (
    ClimateRecordOut,
    ClimateRecordPage,
    DatasetOut,
    HomeStats,
)
from app.services import accessibility, audit

router = APIRouter(tags=["climate"])


@router.get("/climate-data", response_model=ClimateRecordPage)
def get_climate_data(
    country: str | None = None,
    source: str | None = None,
    year: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    q = db.query(models.ClimateRecord)
    if country:
        q = q.filter(models.ClimateRecord.country == country)
    if source:
        q = q.filter(models.ClimateRecord.source == source)
    if year:
        q = q.filter(func.extract("year", models.ClimateRecord.date) == year)
    total = q.count()
    items = (
        q.order_by(models.ClimateRecord.date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ClimateRecordPage(
        total=total,
        page=page,
        page_size=page_size,
        items=[ClimateRecordOut.model_validate(i) for i in items],
    )


@router.get("/datasets", response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Dataset).order_by(models.Dataset.name).all()


@router.get("/countries", response_model=list[str])
def list_countries(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = db.query(models.ClimateRecord.country).distinct().all()
    return sorted(r[0] for r in rows if r[0])


@router.get("/stats/home", response_model=HomeStats)
def home_stats(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    total_records = db.query(func.count(models.ClimateRecord.record_id)).scalar() or 0
    total_countries = (
        db.query(func.count(func.distinct(models.ClimateRecord.country))).scalar() or 0
    )
    total_datasets = db.query(func.count(models.Dataset.id)).scalar() or 0
    avg_temp = db.query(func.avg(models.ClimateRecord.temperature)).scalar()
    avg_rain = db.query(func.avg(models.ClimateRecord.rainfall)).scalar()
    avg_hum = db.query(func.avg(models.ClimateRecord.humidity)).scalar()
    overall_quality = db.query(func.avg(models.DataQualityMetric.overall_score)).scalar() or 0
    interop = db.query(func.avg(models.InteroperabilityMetric.integration_score)).scalar() or 0

    return HomeStats(
        total_records=int(total_records),
        total_countries=int(total_countries),
        total_datasets=int(total_datasets),
        average_temperature=round(float(avg_temp), 2) if avg_temp is not None else None,
        average_rainfall=round(float(avg_rain), 2) if avg_rain is not None else None,
        average_humidity=round(float(avg_hum), 2) if avg_hum is not None else None,
        overall_quality_score=round(float(overall_quality), 2),
        accessibility_score=accessibility.accessibility_score(),
        interoperability_score=round(float(interop), 2),
    )


@router.post("/integrate-data")
def integrate_data(
    db: Session = Depends(get_db), user: models.User = Depends(require_role("analyst"))
):
    """Re-run the full ETL pipeline over the registered sources."""
    summary = pipeline.run_etl(db, regenerate=True)
    audit.log(db, action="run_etl", user=user, resource="pipeline", detail=str(summary))
    return {"status": "ok", "summary": summary}


@router.post("/upload-dataset")
async def upload_dataset(
    source: str = Query(..., description="Known source schema: NOAA, NASA, or WorldBank"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role("analyst")),
):
    """Upload a CSV/JSON file, harmonize + quality-check it, and load it."""
    if source not in harmonization.SCHEMA_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown source schema. Use one of {list(harmonization.SCHEMA_MAP)}",
        )
    content = await file.read()
    name = (file.filename or "").lower()
    try:
        if name.endswith(".json"):
            raw = pd.read_json(io.BytesIO(content))
        else:
            raw = pd.read_csv(io.BytesIO(content))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Could not parse file: {exc}") from exc

    harmonized = harmonization.harmonize(raw, source)
    cleaned, report = data_quality.clean(harmonized)

    dataset = pipeline._upsert_dataset(db, source, "csv", len(raw), len(cleaned))
    pipeline._replace_records(db, dataset, cleaned)
    pipeline._store_quality(db, dataset, report)
    db.commit()
    audit.log(db, action="upload_dataset", user=user, resource=f"dataset:{source}")
    return {
        "status": "ok",
        "source": source,
        "raw_records": len(raw),
        "loaded_records": len(cleaned),
        "quality": report.as_dict(),
    }


@router.get("/audit-logs")
def audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_role("admin")),
):
    rows = (
        db.query(models.AuditLog)
        .order_by(models.AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "username": r.username,
            "action": r.action,
            "resource": r.resource,
            "detail": r.detail,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
