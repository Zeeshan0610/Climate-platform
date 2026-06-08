"""Data harmonization layer: schema mapping, unit & value normalization.

Converts heterogeneous source schemas into the unified canonical schema:
    country, region, date, temperature(C), rainfall(mm), humidity(%), source
"""
from __future__ import annotations

import pandas as pd

# Per-source mapping of {source_column: canonical_column}
SCHEMA_MAP: dict[str, dict[str, str]] = {
    "NOAA": {
        "station_country": "country",
        "us_state": "region",
        "obs_date": "date",
        "temp_f": "temperature",
        "precip_in": "rainfall",
        "rel_humidity": "humidity",
    },
    "NASA": {
        "nation": "country",
        "province": "region",
        "timestamp": "date",
        "air_temp_celsius": "temperature",
        "precipitation_mm": "rainfall",
        "humidity_pct": "humidity",
    },
    "WorldBank": {
        "country_code": "country",
        "area": "region",
        "record_day": "date",
        "avg_temperature_c": "temperature",
        "rainfall_millimeters": "rainfall",
        "moisture": "humidity",
    },
}

# Units that need conversion per source
SOURCE_UNITS = {
    "NOAA": {"temperature": "fahrenheit", "rainfall": "inches"},
    "NASA": {"temperature": "celsius", "rainfall": "mm"},
    "WorldBank": {"temperature": "celsius", "rainfall": "mm"},
}

# Native date formats per source (None => let pandas infer)
SOURCE_DATE_FORMAT = {
    "NOAA": "%Y-%m-%d",
    "NASA": "%d/%m/%Y",
    "WorldBank": "%Y-%m-%d",
}

COUNTRY_CODE_TO_NAME = {
    "IND": "India",
    "USA": "United States",
    "BRA": "Brazil",
    "DEU": "Germany",
    "AUS": "Australia",
}

COUNTRY_ALIASES = {
    "INDIA": "India",
    "UNITED STATES": "United States",
    "BRAZIL": "Brazil",
    "GERMANY": "Germany",
    "AUSTRALIA": "Australia",
}


def fahrenheit_to_celsius(f: float) -> float:
    return (f - 32) * 5 / 9


def inches_to_mm(inches: float) -> float:
    return inches * 25.4


def miles_to_km(miles: float) -> float:
    return miles * 1.609344


def normalize_country(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    raw = str(value).strip()
    if raw.upper() in COUNTRY_CODE_TO_NAME:
        return COUNTRY_CODE_TO_NAME[raw.upper()]
    if raw.upper() in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[raw.upper()]
    return raw.title()


def normalize_date(series: pd.Series, fmt: str | None = None) -> pd.Series:
    """Parse dates into ISO date objects.

    If an explicit ``fmt`` is provided it is used first; rows that fail are
    retried with pandas' flexible parser so mixed-format inputs still resolve.
    """
    if fmt:
        parsed = pd.to_datetime(series, errors="coerce", format=fmt)
        if parsed.isna().any():
            fallback = pd.to_datetime(series, errors="coerce")
            parsed = parsed.fillna(fallback)
    else:
        parsed = pd.to_datetime(series, errors="coerce")
    return parsed.dt.date


def harmonize(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Map a source DataFrame to the canonical schema with normalized units."""
    if source not in SCHEMA_MAP:
        raise ValueError(f"No schema mapping registered for source '{source}'")

    mapping = SCHEMA_MAP[source]
    present = {src: canon for src, canon in mapping.items() if src in df.columns}
    out = df.rename(columns=present)[list(present.values())].copy()

    # Numeric coercion
    for col in ("temperature", "rainfall", "humidity"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # Unit conversions
    units = SOURCE_UNITS.get(source, {})
    if units.get("temperature") == "fahrenheit" and "temperature" in out.columns:
        out["temperature"] = out["temperature"].apply(
            lambda v: fahrenheit_to_celsius(v) if pd.notna(v) else v
        )
    if units.get("rainfall") == "inches" and "rainfall" in out.columns:
        out["rainfall"] = out["rainfall"].apply(lambda v: inches_to_mm(v) if pd.notna(v) else v)

    # Value normalization
    if "country" in out.columns:
        out["country"] = out["country"].apply(normalize_country)
    if "date" in out.columns:
        out["date"] = normalize_date(out["date"], SOURCE_DATE_FORMAT.get(source))
    if "region" in out.columns:
        out["region"] = out["region"].astype("string").str.strip()

    out["source"] = source

    # Round numeric for cleanliness
    for col in ("temperature", "rainfall", "humidity"):
        if col in out.columns:
            out[col] = out[col].round(2)

    return out


def schema_compatibility(source_a: str, source_b: str) -> float:
    """Fraction of canonical fields both sources can supply (Jaccard on canon targets)."""
    a = set(SCHEMA_MAP.get(source_a, {}).values())
    b = set(SCHEMA_MAP.get(source_b, {}).values())
    if not a or not b:
        return 0.0
    return round(len(a & b) / len(a | b) * 100, 2)
