"""Data quality layer: missing values, duplicates, outliers, validation, scoring."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# Physically plausible ranges for validation (after harmonization to metric units)
VALID_RANGES = {
    "temperature": (-60.0, 60.0),  # Celsius
    "rainfall": (0.0, 2000.0),  # mm per observation window
    "humidity": (0.0, 100.0),  # percent
}

NUMERIC_COLS = ["temperature", "rainfall", "humidity"]


@dataclass
class QualityReport:
    rows_in: int = 0
    rows_out: int = 0
    duplicates_removed: int = 0
    outliers_detected: int = 0
    missing_before: int = 0
    missing_imputed: int = 0
    invalid_removed: int = 0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    validity_score: float = 0.0
    accuracy_score: float = 0.0
    timeliness_score: float = 0.0
    overall_score: float = 0.0
    per_column_missing: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return self.__dict__


def detect_missing(df: pd.DataFrame) -> dict[str, int]:
    """Count nulls and empty strings per numeric column."""
    counts: dict[str, int] = {}
    for col in NUMERIC_COLS:
        if col in df.columns:
            null_count = int(df[col].isna().sum())
            counts[col] = null_count
    return counts


def impute_missing(df: pd.DataFrame, strategy: str = "median") -> tuple[pd.DataFrame, int]:
    """Impute missing numeric values.

    strategy: 'mean', 'median', or 'ffill' (forward fill within country/source).
    Returns (df, number_of_values_imputed).
    """
    df = df.copy()
    imputed = 0
    for col in NUMERIC_COLS:
        if col not in df.columns:
            continue
        before = int(df[col].isna().sum())
        if before == 0:
            continue
        if strategy == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif strategy == "ffill":
            df[col] = df.groupby("source")[col].transform(
                lambda s: s.ffill().bfill()
            )
            df[col] = df[col].fillna(df[col].median())
        else:  # median
            df[col] = df[col].fillna(df[col].median())
        imputed += before
    return df, imputed


def drop_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    keys = [c for c in ["country", "region", "date", "source"] if c in df.columns]
    before = len(df)
    out = df.drop_duplicates(subset=keys or None).reset_index(drop=True)
    return out, before - len(out)


def detect_outliers_iqr(series: pd.Series, k: float = 1.5) -> pd.Series:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return (series < lower) | (series > upper)


def detect_outliers_zscore(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    mean, std = series.mean(), series.std(ddof=0)
    if std == 0 or np.isnan(std):
        return pd.Series(False, index=series.index)
    z = (series - mean) / std
    return z.abs() > threshold


def remove_invalid(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Drop records that violate validation ranges or have unparseable dates."""
    df = df.copy()
    mask = pd.Series(True, index=df.index)
    for col, (lo, hi) in VALID_RANGES.items():
        if col in df.columns:
            col_ok = df[col].isna() | df[col].between(lo, hi)
            mask &= col_ok
    if "date" in df.columns:
        mask &= df["date"].notna()
    if "country" in df.columns:
        mask &= df["country"].notna()
    removed = int((~mask).sum())
    return df[mask].reset_index(drop=True), removed


def clean(df: pd.DataFrame, impute_strategy: str = "median") -> tuple[pd.DataFrame, QualityReport]:
    """Run the full data-quality pipeline and produce a scored report."""
    report = QualityReport(rows_in=len(df))
    report.per_column_missing = detect_missing(df)
    report.missing_before = int(sum(report.per_column_missing.values()))

    # 1. Remove invalid / out-of-range first (e.g. impossible 580C outlier)
    df, invalid_removed = remove_invalid(df)
    report.invalid_removed = invalid_removed

    # 2. Outlier detection (statistical) flagged per numeric column
    outlier_mask = pd.Series(False, index=df.index)
    for col in NUMERIC_COLS:
        if col in df.columns and df[col].notna().sum() > 4:
            outlier_mask |= detect_outliers_iqr(df[col].dropna().reindex(df.index))
    report.outliers_detected = int(outlier_mask.fillna(False).sum())

    # 3. Duplicate removal
    df, dups = drop_duplicates(df)
    report.duplicates_removed = dups

    # 4. Missing value imputation
    df, imputed = impute_missing(df, strategy=impute_strategy)
    report.missing_imputed = imputed

    report.rows_out = len(df)
    _score(df, report)
    return df, report


def _score(df: pd.DataFrame, report: QualityReport) -> None:
    n = max(len(df), 1)
    total_cells = n * len([c for c in NUMERIC_COLS if c in df.columns])

    # Completeness: non-missing fraction after cleaning
    non_missing = sum(int(df[c].notna().sum()) for c in NUMERIC_COLS if c in df.columns)
    report.completeness_score = round(non_missing / max(total_cells, 1) * 100, 2)

    # Validity: fraction within valid ranges
    valid_cells, checked = 0, 0
    for col, (lo, hi) in VALID_RANGES.items():
        if col in df.columns:
            s = df[col].dropna()
            checked += len(s)
            valid_cells += int(s.between(lo, hi).sum())
    report.validity_score = round((valid_cells / checked * 100) if checked else 100.0, 2)

    # Consistency: penalize duplicates relative to input
    dedup_ratio = 1 - (report.duplicates_removed / max(report.rows_in, 1))
    report.consistency_score = round(dedup_ratio * 100, 2)

    # Accuracy: penalize outliers + invalid removals
    bad = report.outliers_detected + report.invalid_removed
    report.accuracy_score = round(max(0.0, 1 - bad / max(report.rows_in, 1)) * 100, 2)

    # Timeliness: fraction of records with a valid recent date
    if "date" in df.columns and len(df):
        report.timeliness_score = round(df["date"].notna().mean() * 100, 2)
    else:
        report.timeliness_score = 100.0

    report.overall_score = round(
        np.mean(
            [
                report.completeness_score,
                report.consistency_score,
                report.validity_score,
                report.accuracy_score,
                report.timeliness_score,
            ]
        ),
        2,
    )
