"""Data quality, interoperability, reliability, accessibility endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db import models
from app.db.session import get_db
from app.services import accessibility

router = APIRouter(tags=["metrics"])


@router.get("/quality-metrics")
def quality_metrics(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = db.query(models.DataQualityMetric).all()
    datasets = [
        {
            "dataset_name": r.dataset_name,
            "completeness": r.completeness_score,
            "consistency": r.consistency_score,
            "validity": r.validity_score,
            "accuracy": r.accuracy_score,
            "timeliness": r.timeliness_score,
            "overall": r.overall_score,
            "duplicates_removed": r.duplicates_removed,
            "outliers_detected": r.outliers_detected,
            "missing_imputed": r.missing_imputed,
        }
        for r in rows
    ]
    overall = db.query(func.avg(models.DataQualityMetric.overall_score)).scalar() or 0
    return {"overall_score": round(float(overall), 2), "datasets": datasets}


@router.get("/interoperability-score")
def interoperability(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = db.query(models.InteroperabilityMetric).all()
    pairs = [
        {
            "source_a": r.source_a,
            "source_b": r.source_b,
            "schema_compatibility": r.schema_compatibility,
            "semantic_compatibility": r.semantic_compatibility,
            "mapping_success_rate": r.mapping_success_rate,
            "integration_score": r.integration_score,
        }
        for r in rows
    ]
    overall = db.query(func.avg(models.InteroperabilityMetric.integration_score)).scalar() or 0
    return {"overall_score": round(float(overall), 2), "pairs": pairs}


@router.get("/reliability-score")
def reliability(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    rows = db.query(models.ReliabilityMetric).all()
    datasets = [
        {
            "dataset_name": r.dataset_name,
            "completeness": r.completeness,
            "consistency": r.consistency,
            "accuracy": r.accuracy,
            "availability": r.availability,
            "reliability_score": r.reliability_score,
        }
        for r in rows
    ]
    overall = db.query(func.avg(models.ReliabilityMetric.reliability_score)).scalar() or 0
    return {"overall_score": round(float(overall), 2), "datasets": datasets}


@router.get("/accessibility-score")
def accessibility_score(user: models.User = Depends(get_current_user)):
    return accessibility.accessibility_report()
