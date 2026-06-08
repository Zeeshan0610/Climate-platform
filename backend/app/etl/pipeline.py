"""ETL orchestration: ingest -> harmonize -> quality -> load + metrics."""
from __future__ import annotations

from itertools import combinations

import pandas as pd
from sqlalchemy.orm import Session

from app.db import models
from app.etl import data_quality, generate_sources, harmonization, ingestion

# Registered sources: name -> (relative file, format)
SOURCES = {
    "NOAA": ("noaa_climate.csv", "csv"),
    "NASA": ("nasa_climate.json", "json"),
    "WorldBank": ("worldbank_climate.csv", "csv"),
}

SOURCE_DESCRIPTIONS = {
    "NOAA": "US NOAA observations (imperial units: Fahrenheit/inches).",
    "NASA": "NASA climate JSON feed (metric units, DD/MM/YYYY dates).",
    "WorldBank": "World Bank climate indicators (country codes, metric units).",
}


def run_etl(db: Session, regenerate: bool = True, impute_strategy: str = "median") -> dict:
    """Run the full ETL pipeline and persist results. Returns a summary dict."""
    if regenerate:
        generate_sources.generate()

    data_dir = generate_sources.DATA_DIR
    summary: dict = {"datasets": [], "total_loaded": 0}
    harmonized_frames: dict[str, pd.DataFrame] = {}

    for name, (filename, fmt) in SOURCES.items():
        raw = ingestion.ingest(data_dir / filename, fmt)
        raw_count = len(raw)
        harmonized = harmonization.harmonize(raw, name)
        cleaned, report = data_quality.clean(harmonized, impute_strategy=impute_strategy)
        harmonized_frames[name] = cleaned

        dataset = _upsert_dataset(db, name, fmt, raw_count, len(cleaned))
        _replace_records(db, dataset, cleaned)
        _store_quality(db, dataset, report)
        _store_reliability(db, name, report)

        summary["datasets"].append(
            {
                "name": name,
                "raw": raw_count,
                "loaded": len(cleaned),
                "quality": report.overall_score,
            }
        )
        summary["total_loaded"] += len(cleaned)

    _store_interoperability(db, harmonized_frames)
    db.commit()
    return summary


def _upsert_dataset(
    db: Session, name: str, fmt: str, raw_count: int, loaded: int
) -> models.Dataset:
    dataset = db.query(models.Dataset).filter_by(name=name).one_or_none()
    if dataset is None:
        dataset = models.Dataset(name=name)
        db.add(dataset)
    dataset.source = name
    dataset.fmt = fmt
    dataset.description = SOURCE_DESCRIPTIONS.get(name)
    dataset.raw_record_count = raw_count
    dataset.loaded_record_count = loaded
    db.flush()
    return dataset


def _replace_records(db: Session, dataset: models.Dataset, df: pd.DataFrame) -> None:
    db.query(models.ClimateRecord).filter_by(dataset_id=dataset.id).delete()
    db.flush()
    objects = [
        models.ClimateRecord(
            dataset_id=dataset.id,
            country=row.get("country"),
            region=(row.get("region") if pd.notna(row.get("region")) else None),
            date=row.get("date"),
            temperature=_nan_to_none(row.get("temperature")),
            rainfall=_nan_to_none(row.get("rainfall")),
            humidity=_nan_to_none(row.get("humidity")),
            source=dataset.name,
        )
        for row in df.to_dict(orient="records")
        if row.get("date") is not None and row.get("country") is not None
    ]
    db.bulk_save_objects(objects)
    db.flush()


def _store_quality(db: Session, dataset: models.Dataset, report) -> None:
    db.query(models.DataQualityMetric).filter_by(dataset_id=dataset.id).delete()
    db.add(
        models.DataQualityMetric(
            dataset_id=dataset.id,
            dataset_name=dataset.name,
            completeness_score=report.completeness_score,
            consistency_score=report.consistency_score,
            validity_score=report.validity_score,
            accuracy_score=report.accuracy_score,
            timeliness_score=report.timeliness_score,
            overall_score=report.overall_score,
            duplicates_removed=report.duplicates_removed,
            outliers_detected=report.outliers_detected,
            missing_imputed=report.missing_imputed,
        )
    )


def _store_reliability(db: Session, name: str, report) -> None:
    db.query(models.ReliabilityMetric).filter_by(dataset_name=name).delete()
    availability = 100.0  # sources successfully ingested this run
    score = round(
        (
            report.completeness_score
            + report.consistency_score
            + report.accuracy_score
            + availability
        )
        / 4,
        2,
    )
    db.add(
        models.ReliabilityMetric(
            dataset_name=name,
            completeness=report.completeness_score,
            consistency=report.consistency_score,
            accuracy=report.accuracy_score,
            availability=availability,
            reliability_score=score,
        )
    )


def _store_interoperability(db: Session, frames: dict[str, pd.DataFrame]) -> None:
    db.query(models.InteroperabilityMetric).delete()
    names = list(frames.keys())
    for a, b in combinations(names, 2):
        schema_compat = harmonization.schema_compatibility(a, b)
        semantic = _semantic_compatibility(frames[a], frames[b])
        mapping_success = _mapping_success(frames[a], frames[b])
        integration = round((schema_compat + semantic + mapping_success) / 3, 2)
        db.add(
            models.InteroperabilityMetric(
                source_a=a,
                source_b=b,
                schema_compatibility=schema_compat,
                semantic_compatibility=semantic,
                mapping_success_rate=mapping_success,
                integration_score=integration,
            )
        )


def _semantic_compatibility(df_a: pd.DataFrame, df_b: pd.DataFrame) -> float:
    """Overlap of shared countries between two harmonized sources."""
    a = set(df_a.get("country", pd.Series(dtype=str)).dropna().unique())
    b = set(df_b.get("country", pd.Series(dtype=str)).dropna().unique())
    if not a or not b:
        return 0.0
    return round(len(a & b) / len(a | b) * 100, 2)


def _mapping_success(df_a: pd.DataFrame, df_b: pd.DataFrame) -> float:
    """Fraction of canonical numeric fields populated in both frames."""
    fields = ["temperature", "rainfall", "humidity"]
    ok = 0
    for f in fields:
        if f in df_a.columns and f in df_b.columns:
            if df_a[f].notna().any() and df_b[f].notna().any():
                ok += 1
    return round(ok / len(fields) * 100, 2)


def _nan_to_none(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        return value
    return float(value)
