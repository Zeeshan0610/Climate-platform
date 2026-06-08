"""Unit tests for the ETL layers: harmonization and data quality."""
from __future__ import annotations

import pandas as pd

from app.etl import data_quality, harmonization


def test_unit_conversions():
    assert round(harmonization.fahrenheit_to_celsius(32), 2) == 0.0
    assert round(harmonization.fahrenheit_to_celsius(212), 2) == 100.0
    assert round(harmonization.inches_to_mm(1), 2) == 25.4
    assert round(harmonization.miles_to_km(1), 3) == 1.609


def test_country_normalization():
    assert harmonization.normalize_country("IND") == "India"
    assert harmonization.normalize_country("INDIA") == "India"
    assert harmonization.normalize_country("brazil") == "Brazil"


def test_harmonize_noaa_schema_and_units():
    raw = pd.DataFrame(
        {
            "station_country": ["USA"],
            "us_state": ["Texas"],
            "obs_date": ["2022-03-15"],
            "temp_f": [212.0],
            "precip_in": [1.0],
            "rel_humidity": [50.0],
        }
    )
    out = harmonization.harmonize(raw, "NOAA")
    assert list(out.columns) >= ["country", "region", "date", "temperature", "rainfall"]
    assert out.loc[0, "country"] == "United States"
    assert round(out.loc[0, "temperature"], 1) == 100.0  # 212F -> 100C
    assert round(out.loc[0, "rainfall"], 1) == 25.4  # 1in -> 25.4mm
    assert str(out.loc[0, "date"]) == "2022-03-15"


def test_iso_dates_parsed_correctly():
    raw = pd.DataFrame(
        {
            "country_code": ["IND", "IND"],
            "area": ["Delhi", "Delhi"],
            "record_day": ["2022-01-25", "2022-12-30"],
            "avg_temperature_c": [20.0, 18.0],
            "rainfall_millimeters": [10.0, 5.0],
            "moisture": [60.0, 55.0],
        }
    )
    out = harmonization.harmonize(raw, "WorldBank")
    assert out["date"].notna().all()
    assert str(out.loc[0, "date"]) == "2022-01-25"


def test_data_quality_removes_outlier_and_dedupes():
    dates = [
        pd.Timestamp(d).date()
        for d in [
            "2022-01-01",
            "2022-01-02",
            "2022-01-03",
            "2022-01-04",
            "2022-01-05",
            "2022-01-05",  # duplicate of previous
        ]
    ]
    df = pd.DataFrame(
        {
            "country": ["India"] * 6,
            "region": ["Delhi"] * 6,
            "date": dates,
            "temperature": [25, 26, 27, 580, 24, 24],  # 580 invalid
            "rainfall": [10, 12, 11, 9, 8, 8],
            "humidity": [60, None, 62, 61, 59, 59],  # one missing
            "source": ["NOAA"] * 6,
        }
    )
    cleaned, report = data_quality.clean(df)
    assert report.invalid_removed >= 1  # 580C dropped
    assert report.duplicates_removed >= 1  # duplicate last row
    assert report.missing_imputed >= 1  # humidity filled
    assert cleaned["humidity"].isna().sum() == 0
    assert 0 <= report.overall_score <= 100
