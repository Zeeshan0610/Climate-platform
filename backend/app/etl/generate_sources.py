"""Generate heterogeneous raw climate source files.

This simulates real-world repositories that publish climate data in
different formats, units, schemas and quality levels:

  * NOAA      -> CSV, imperial units (Fahrenheit, inches), US-style columns
  * NASA      -> JSON, metric units (Celsius, mm), nested-ish records
  * WorldBank -> CSV, metric units, different column names + country codes

The generator deliberately injects data quality problems (missing values,
duplicates, outliers, inconsistent country names) so the data-quality and
harmonization layers have something meaningful to fix.
"""
from __future__ import annotations

import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

COUNTRIES = [
    ("India", "IND", ["Maharashtra", "Karnataka", "Delhi"]),
    ("United States", "USA", ["California", "Texas", "New York"]),
    ("Brazil", "BRA", ["Sao Paulo", "Amazonas", "Bahia"]),
    ("Germany", "DEU", ["Bavaria", "Berlin", "Hesse"]),
    ("Australia", "AUS", ["Queensland", "Victoria", "New South Wales"]),
]

# Rough mean temperature (Celsius) per country for realistic seasonality
BASE_TEMP_C = {"India": 27, "United States": 14, "Brazil": 25, "Germany": 9, "Australia": 21}


def _seasonal_temp_c(country: str, d: date) -> float:
    base = BASE_TEMP_C[country]
    # Northern vs southern hemisphere phase
    southern = country in {"Brazil", "Australia"}
    day_of_year = d.timetuple().tm_yday
    phase = (day_of_year / 365.0) * 2 * math.pi
    swing = 8 * math.sin(phase + (math.pi if southern else 0))
    return base + swing + random.uniform(-2.5, 2.5)


def _c_to_f(c: float) -> float:
    return c * 9 / 5 + 32


def _mm_to_inches(mm: float) -> float:
    return mm / 25.4


def generate(seed: int = 42, months: int = 24) -> dict[str, Path]:
    """Generate raw source files and return mapping of source name -> path."""
    random.seed(seed)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    start = date(2022, 1, 1)
    days = months * 30
    dates = [start + timedelta(days=i * 5) for i in range(days // 5)]

    paths: dict[str, Path] = {}

    # ---- NOAA: CSV, Fahrenheit + inches ----
    noaa_rows = ["station_country,us_state,obs_date,temp_f,precip_in,rel_humidity"]
    for country, _code, regions in COUNTRIES:
        for d in dates:
            region = random.choice(regions)
            temp_c = _seasonal_temp_c(country, d)
            rain_mm = max(0, random.gauss(60, 40))
            hum = min(100, max(10, random.gauss(65, 15)))
            temp_f = round(_c_to_f(temp_c), 1)
            precip_in = round(_mm_to_inches(rain_mm), 3)
            # inject missing values (~5%)
            hum_s = "" if random.random() < 0.05 else round(hum, 1)
            noaa_rows.append(
                f"{country},{region},{d.isoformat()},{temp_f},{precip_in},{hum_s}"
            )
    # inject a few duplicates and an outlier
    noaa_rows.append(noaa_rows[1])
    noaa_rows.append(noaa_rows[2])
    noaa_rows.append("India,Delhi,2022-06-15,580.0,2.0,55.0")  # impossible temp outlier
    noaa_path = DATA_DIR / "noaa_climate.csv"
    noaa_path.write_text("\n".join(noaa_rows) + "\n")
    paths["NOAA"] = noaa_path

    # ---- NASA: JSON, Celsius + mm, different field names ----
    nasa_records = []
    for country, _code, regions in COUNTRIES:
        for d in dates:
            region = random.choice(regions)
            temp_c = round(_seasonal_temp_c(country, d), 2)
            rain_mm = round(max(0, random.gauss(60, 40)), 2)
            hum = round(min(100, max(10, random.gauss(65, 15))), 1)
            rec = {
                "nation": country.upper() if random.random() < 0.3 else country,
                "province": region,
                "timestamp": d.strftime("%d/%m/%Y"),  # different date format
                "air_temp_celsius": temp_c if random.random() > 0.04 else None,
                "precipitation_mm": rain_mm,
                "humidity_pct": hum,
            }
            nasa_records.append(rec)
    nasa_records.append(nasa_records[0])  # duplicate
    nasa_path = DATA_DIR / "nasa_climate.json"
    nasa_path.write_text(json.dumps(nasa_records, indent=2))
    paths["NASA"] = nasa_path

    # ---- World Bank: CSV, metric, country codes + yet another schema ----
    wb_rows = ["country_code,area,record_day,avg_temperature_c,rainfall_millimeters,moisture"]
    code_map = {c: code for c, code, _ in COUNTRIES}
    for country, code, regions in COUNTRIES:
        for d in dates:
            region = random.choice(regions)
            temp_c = round(_seasonal_temp_c(country, d), 2)
            rain_mm = round(max(0, random.gauss(60, 40)), 2)
            hum = round(min(100, max(10, random.gauss(65, 15))), 1)
            wb_rows.append(
                f"{code_map[country]},{region},{d.isoformat()},{temp_c},{rain_mm},{hum}"
            )
    wb_path = DATA_DIR / "worldbank_climate.csv"
    wb_path.write_text("\n".join(wb_rows) + "\n")
    paths["WorldBank"] = wb_path

    return paths


if __name__ == "__main__":
    out = generate()
    for name, path in out.items():
        print(f"{name}: {path}")
