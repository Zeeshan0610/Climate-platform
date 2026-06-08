# Viva Questions & Answers

### 1. What is the core problem this project solves?
Climate data lives in many repositories (NOAA, NASA, World Bank) with different
schemas, formats, units, and quality issues, and analytics tools are often
inaccessible. The platform **integrates and standardizes** heterogeneous climate
data while making the resulting analytics **WCAG 2.1 accessible**.

### 2. Walk through the ETL pipeline.
`run_etl()` iterates over registered sources: **ingest** (CSV/JSON/API →
DataFrame) → **harmonize** (rename to canonical schema, convert units, normalize
country/date) → **clean** (remove invalid rows, flag outliers, drop duplicates,
impute missing, compute quality score) → **load** (replace dataset records, store
quality + reliability) and finally compute **pairwise interoperability**.

### 3. How do you harmonize heterogeneous schemas?
A per-source `SCHEMA_MAP` renames native columns to canonical fields
(`country, region, date, temperature, rainfall, humidity`). `SOURCE_UNITS` drives
unit conversion (e.g. NOAA Fahrenheit→Celsius, inches→mm). Country codes/aliases
map to canonical names, and `SOURCE_DATE_FORMAT` parses each source's date format.

### 4. Why was source-aware date parsing necessary?
A global `dayfirst=True` corrupted ISO `YYYY-MM-DD` dates (NOAA/World Bank),
turning `2022-01-13` into `NaT` and collapsing records. The fix parses each
source with its explicit format and only falls back to flexible parsing for
unmatched rows.

### 5. How is data quality scored?
Five dimensions in `_score()`: **completeness** (non-null fraction),
**validity** (within valid ranges), **consistency** (1 − duplicate ratio),
**accuracy** (1 − outlier/invalid ratio), **timeliness** (valid-date fraction).
The overall score is their mean. Outliers use **IQR** and **z-score**; missing
values are imputed by mean/median/forward-fill.

### 6. How do you measure interoperability?
For each source pair: **schema compatibility** (Jaccard similarity of canonical
fields), **semantic compatibility** (country overlap), **mapping success rate**
(fraction of numeric fields populated), and their average as the **integration
score**.

### 7. How does forecasting work and why ARIMA?
Daily data is resampled to monthly means; `ARIMA(1,1,1)` (statsmodels) predicts
future periods. If statsmodels fails or data is insufficient, a NumPy
linear-trend fallback guarantees a response. ARIMA captures autocorrelation/trend
without Prophet's heavier dependency footprint.

### 8. Describe the ML component.
`train_and_evaluate()` engineers features (month, day-of-year, year, encoded
country, humidity, rainfall), does an 80/20 split, trains **Random Forest**
(and **XGBoost** if installed), and reports **MAE, RMSE, R²** plus feature
importance, selecting the best model by RMSE.

### 9. How is security implemented?
JWT (HS256) bearer tokens, bcrypt password hashing, and hierarchical RBAC
(`viewer < analyst < admin`) enforced through FastAPI dependencies
(`require_role`). Sensitive actions are recorded in `audit_logs`.

### 10. What makes the dashboard accessible (WCAG 2.1)?
- **Perceivable:** ≥4.5:1 contrast, scalable fonts, color-blind-safe (Okabe–Ito)
  chart palettes.
- **Operable:** full keyboard navigation, shortcuts (Alt+1..6/T/±), skip links,
  visible focus rings.
- **Understandable:** consistent nav, labelled forms, predictable layout.
- **Robust:** semantic HTML landmarks + ARIA roles for screen readers.
Plus a High-Contrast theme and text-to-speech narration.

### 11. Why PostgreSQL, and how is portability handled?
PostgreSQL for a robust relational store with strong typing and concurrency.
SQLAlchemy ORM keeps it portable — local dev uses SQLite, production uses
PostgreSQL via `DATABASE_URL`. Numeric values are cast to native Python floats
before persistence so psycopg2 can adapt them.

### 12. How would you scale or extend this?
Add a new source by registering it in `SCHEMA_MAP`/`SOURCE_UNITS`/`SOURCES`.
For scale: move ETL to a scheduler/queue (Airflow/Celery), add incremental
loading (already supported via `incremental_filter`), partition `climate_records`
by date, and cache analytics responses.

### 13. What is data lineage here?
Every `climate_record` references its `dataset`, which retains `raw_record_count`
vs `loaded_record_count` and `ingested_at`; quality/reliability metrics are stored
per dataset, giving traceability from source file to loaded record to score.

### 14. How is the project tested?
17 backend tests (ETL unit + API integration incl. RBAC) and 6 frontend tests
(theme/accessibility logic), plus documented manual accessibility scenarios.
Linting via Ruff (backend) and ESLint (frontend).

### 15. How is it deployed?
Docker Compose orchestrates PostgreSQL, the FastAPI backend (auto-migrates and
seeds on startup), and an nginx-served React build that proxies `/api`.
