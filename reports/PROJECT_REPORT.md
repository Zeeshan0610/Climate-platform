# Accessible Climate Data Integration Platform — Project Report

*An Accessibility-Aware Climate Data Harmonization and Analytics Framework*

**Programme:** M.Tech — Data Engineering (Capstone Project)
**Repository:** https://github.com/Zeeshan0610/Climate-platform

---

## 1. Abstract

Climate data is published by many independent repositories (NOAA, NASA, World
Bank, etc.) in incompatible schemas, formats, and units, and most analytics
dashboards are not accessible to users with disabilities. This project delivers a
production-style, end-to-end **data-engineering platform** that ingests
heterogeneous climate datasets, harmonizes them into a single canonical schema,
validates and scores their quality, measures interoperability and reliability,
and exposes the results through an **accessibility-first (WCAG 2.1 AA)** analytics
dashboard with statistical analytics, time-series forecasting, and machine-learning
prediction. The system is secured with JWT authentication and role-based access
control and is fully containerized with Docker Compose.

---

## 2. Objectives

1. Collect climate datasets from multiple heterogeneous repositories.
2. Harmonize differing schemas, units, country names, and date formats.
3. Clean and validate records (missing values, duplicates, outliers, range rules).
4. Integrate everything into one unified relational repository.
5. Provide accessible dashboards compliant with WCAG 2.1.
6. Evaluate interoperability between datasets.
7. Measure data reliability and quality.
8. Generate climate insights, trends, forecasts, and ML predictions.
9. Allow easy future integration of additional sources.

---

## 3. Technology Stack (Summary Table)

| Layer | Technology / Tool | Version | Purpose |
|-------|-------------------|---------|---------|
| **Programming languages** | Python | 3.12 | Backend, ETL, ML |
| | JavaScript (ES2022, JSX) | — | Frontend (React) |
| | SQL | — | Relational queries / schema |
| | HTML5 + CSS3 | — | Markup & styling |
| | YAML | — | Docker Compose config |
| | Dockerfile | — | Container build scripts |
| **Frontend framework** | React | 18.3 | SPA UI |
| | Vite | 6.0 | Dev server + build tool |
| | Material UI (MUI) | 6.3 | Component library / theming |
| | Emotion | 11.13 | CSS-in-JS styling engine |
| | Recharts | 2.15 | Accessible data visualizations |
| | React Router | 6.28 | Client-side routing |
| | Axios | 1.7 | HTTP client |
| **Backend framework** | FastAPI | 0.115 | REST API framework |
| | Uvicorn | 0.34 | ASGI server |
| | Pydantic / pydantic-settings | 2.10 / 2.7 | Validation & config |
| **ORM / DB driver** | SQLAlchemy | 2.0 | ORM |
| | psycopg2-binary | 2.9 | PostgreSQL driver |
| **Database** | PostgreSQL | 16 | Production datastore |
| | SQLite | bundled | Local-dev datastore |
| **ETL / data processing** | Pandas | 2.2 | Ingestion & transformation |
| | NumPy | 2.2 | Numerical operations |
| | Requests | 2.32 | API ingestion |
| | openpyxl | 3.1 | Excel I/O |
| **Machine learning** | scikit-learn | 1.6 | Random Forest, metrics, encoding |
| | (optional) XGBoost | — | Gradient-boosted comparison model |
| **Forecasting** | statsmodels | 0.14 | ARIMA time-series model |
| **Security / auth** | python-jose[cryptography] | 3.3 | JWT (HS256) |
| | passlib[bcrypt] + bcrypt | 1.7 / 4.2 | Password hashing |
| | python-multipart | 0.0.20 | Form / file uploads |
| **Reporting** | reportlab | 4.2 | PDF generation |
| **Testing (backend)** | PyTest | 8.3 | Unit + integration tests |
| | httpx | 0.28 | API test client |
| | Ruff | latest | Linting |
| **Testing (frontend)** | Vitest | 2.1 | Component/logic tests |
| | Testing Library | 16 | React testing utilities |
| | jsdom | 25 | DOM environment |
| | ESLint | 8.57 | Linting |
| **DevOps** | Docker + Docker Compose | — | Containerization & orchestration |
| | Nginx | 1.27-alpine | Serves built frontend + proxies API |
| **Accessibility standard** | WCAG 2.1 AA + ARIA | — | Accessibility compliance |
| **Version control** | Git + GitHub | — | Source control |
| **IDE / tooling** | VS Code (tasks.json) | — | Development environment |

---

## 4. System Architecture (Layered)

```
 Layer 1  Data Sources        NOAA CSV · NASA JSON · World Bank CSV
 Layer 2  Ingestion           Pandas / Requests  (batch · API · incremental)
 Layer 4  Harmonization       schema mapping · unit conversion · normalization
 Layer 3  Data Quality        missing/dup/outlier · validation · scoring
 Layer 5  Storage             PostgreSQL (SQLite for dev) via SQLAlchemy
 Layer 6  Analytics & ML      trends/statistics · ARIMA forecast · RF/XGBoost
 Layer 7  Accessibility       WCAG 2.1 engine (themes, TTS, keyboard, ARIA)
 Layer 8  Dashboard           React + MUI + Recharts (6 pages)
 Cross    Security            FastAPI · JWT · RBAC · audit logs
 Cross    DevOps              Docker Compose (db + backend + frontend)
```

Data flow: **Sources → Ingest → Harmonize → Validate/Clean/Score → Load to DB →
Analytics/Forecast/ML → REST API (JWT/RBAC) → Accessible React dashboard.**

---

## 5. Data Engineering Components

### 5.1 Ingestion
- Reads **CSV** (NOAA, World Bank) and **JSON** (NASA) into Pandas DataFrames.
- Supports batch loading, simulated API ingestion, and incremental filtering.

### 5.2 Harmonization
- **Schema mapping** (`SCHEMA_MAP`): source columns → canonical fields
  `country, region, date, temperature, rainfall, humidity, source`.
- **Unit conversion** (`SOURCE_UNITS`): Fahrenheit→Celsius, inches→millimetres,
  miles→kilometres.
- **Country normalization:** codes/aliases (`IND`, `INDIA`) → canonical names.
- **Date normalization** (`SOURCE_DATE_FORMAT`): per-source date formats
  (e.g. NASA `DD/MM/YYYY`, NOAA/World Bank ISO `YYYY-MM-DD`).

### 5.3 Data Quality
- **Missing values:** detection + imputation (mean / median / forward-fill).
- **Duplicates:** detection and removal.
- **Outliers:** IQR and Z-score methods.
- **Validation rules:** valid ranges for temperature, rainfall, humidity.
- **Quality scoring (5 dimensions):** completeness, consistency, validity,
  accuracy, timeliness → overall score.

### 5.4 Interoperability Evaluation
For each pair of sources: **schema compatibility** (Jaccard of canonical fields),
**semantic compatibility** (country overlap), **mapping success rate**, and an
overall **integration score**.

### 5.5 Reliability Evaluation
Per dataset: completeness, consistency, accuracy, availability → reliability score.

---

## 6. Database Schema (7 tables)

| Table | Purpose |
|-------|---------|
| `users` | Accounts with role (`viewer`/`analyst`/`admin`), hashed password |
| `audit_logs` | Audit trail of sensitive actions |
| `datasets` | Registered sources + lineage (raw vs loaded counts, ingested_at) |
| `climate_records` | Unified, harmonized climate observations |
| `data_quality_metrics` | Per-dataset quality dimension scores |
| `interoperability_metrics` | Pairwise source compatibility scores |
| `reliability_metrics` | Per-dataset reliability scores |

(Implemented with SQLAlchemy ORM; full ER diagram in `docs/er-diagram.md`.)

---

## 7. Analytics, Forecasting & Machine Learning

- **Analytics:** temperature/rainfall/humidity trends, average-by-country,
  distributions, and statistical summary (mean, median, std-dev, variance).
- **Forecasting:** `ARIMA(1,1,1)` (statsmodels) on monthly-resampled series, with
  a NumPy linear-trend fallback for robustness.
- **Machine learning:** feature engineering (month, day-of-year, year, encoded
  country, humidity, rainfall) → **Random Forest** regressor (and **XGBoost** if
  installed) → evaluated by **MAE, RMSE, R²**, plus feature importance; best model
  chosen by RMSE. (Measured result: RandomForest R² ≈ 0.90.)

---

## 8. Accessibility Engineering (Unique Contribution)

WCAG 2.1 POUR principles with an in-app scoring dashboard:

- **Perceivable:** ≥4.5:1 contrast, scalable fonts, color-blind-safe (Okabe–Ito)
  chart palettes.
- **Operable:** full keyboard navigation, shortcuts (Alt+1..6, Alt+T, Alt+±),
  skip links, visible focus indicators.
- **Understandable:** consistent navigation, labelled forms, predictable layout.
- **Robust:** semantic HTML landmarks + ARIA roles for screen readers.

**14 implemented features:** High-Contrast / Dark / Light modes, Large-Text mode,
Color-Blind-Friendly charts, Font Scaling, Text-to-Speech narration, Speech-
Recognition search, Accessible data tables, ARIA labels, Skip-navigation links,
Keyboard shortcuts, Visible focus indicators, Semantic HTML landmarks.

---

## 9. REST API (selected endpoints)

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | public | Obtain JWT token |
| GET | `/api/auth/me` | any | Current user |
| POST | `/api/auth/users` | admin | Create user |
| GET | `/api/climate-data` | viewer | Paginated records (country/source/year) |
| GET | `/api/stats/home` | viewer | Home KPIs |
| GET | `/api/analytics` | viewer | Trends, distribution, statistics |
| GET | `/api/analytics/ml` | viewer | ML model comparison |
| GET | `/api/forecast` | viewer | ARIMA forecast |
| GET | `/api/quality-metrics` | viewer | Data-quality scores |
| GET | `/api/interoperability-score` | viewer | Interoperability matrix |
| GET | `/api/reliability-score` | viewer | Reliability scores |
| GET | `/api/accessibility-score` | viewer | WCAG report |
| POST | `/api/integrate-data` | analyst | Re-run ETL |
| POST | `/api/upload-dataset` | analyst | Upload + integrate a file |
| GET | `/api/audit-logs` | admin | Audit trail |

---

## 10. Security

- **JWT** bearer authentication (HS256) via python-jose.
- **Password hashing** with bcrypt (passlib).
- **Role-Based Access Control:** hierarchical `viewer < analyst < admin`, enforced
  by FastAPI dependencies.
- **Audit logging** of login, user creation, ETL runs, and uploads.

---

## 11. Dashboard Pages (Frontend)

1. **Home** — KPI cards (records, countries, datasets, averages, quality,
   accessibility, interoperability).
2. **Climate Analytics** — trend charts, average-by-country, statistics, ML
   comparison; filters by country/year.
3. **Accessibility** — WCAG score, POUR breakdown, live controls, feature list.
4. **Data Quality** — overall/per-dataset scores, dimension bars, radar heatmap,
   metrics table.
5. **Interoperability** — integration score, compatibility bars, source matrix.
6. **Forecast** — historical-vs-predicted chart with selectable metric/horizon.

---

## 12. Testing & Quality Assurance

| Suite | Tool | Result |
|-------|------|--------|
| Backend unit + integration | PyTest + httpx | 17 tests passing |
| Backend lint | Ruff | clean |
| Frontend component/logic | Vitest + Testing Library | 6 tests passing |
| Frontend lint | ESLint | clean |
| Frontend build | Vite | succeeds |
| End-to-end | Manual browser walkthrough | all 6 pages verified |

(Test catalogue in `docs/test-cases.md`.)

---

## 13. Deployment / DevOps

- **Docker Compose** orchestrates three services:
  - `db` — PostgreSQL 16 (with health-check + persistent volume),
  - `backend` — FastAPI/Uvicorn (auto-creates schema, seeds users, runs ETL),
  - `frontend` — multi-stage build (Vite → Nginx) serving the SPA and proxying `/api`.
- One-command start: `docker compose up --build` → UI at `:3000`, API at `:8000`.
- Local dev convenience: `start.bat` / `start.ps1` and a VS Code **Run Project** task.

---

## 14. Project Metrics

- **Backend:** ~2,000 lines of Python across 33 modules.
- **Frontend:** ~1,560 lines of JavaScript/JSX across 20 files.
- **Database:** 7 relational tables.
- **Data volume:** ~2,160 harmonized records (3 sources × ~720 each).
- **Demo accounts:** `admin/admin123`, `analyst/analyst123`, `viewer/viewer123`.

---

## 15. Project Structure

```
climate-platform/
├── backend/
│   ├── app/
│   │   ├── api/        # FastAPI routers (auth, climate, analytics, forecast, quality)
│   │   ├── core/       # config + security (JWT, hashing, RBAC)
│   │   ├── db/         # SQLAlchemy models, session, init/seed
│   │   ├── etl/        # ingestion, harmonization, data_quality, pipeline, generators
│   │   ├── ml/         # forecasting (ARIMA), prediction (RF/XGBoost)
│   │   ├── schemas/    # Pydantic schemas
│   │   └── services/   # analytics, accessibility, audit, helpers
│   └── tests/          # PyTest suites
├── frontend/           # React + MUI + Recharts (accessibility engine + 6 pages)
├── docs/               # architecture, ER, DFD, user manual, test cases, viva Q&A
├── reports/            # this report
├── docker-compose.yml
├── start.bat / start.ps1
└── README.md
```

---

## 16. Future Enhancements

- Live API ingestion from real NOAA/NASA/World Bank endpoints.
- Orchestration with Airflow/Celery and partitioned `climate_records`.
- Interactive maps and PDF/Excel report export (reportlab/openpyxl already included).
- Prophet-based forecasting and deep-learning models.
- Cloud deployment (AWS EC2/ECS) and CI/CD pipelines.

---

*Supporting diagrams: `docs/architecture.md`, `docs/er-diagram.md`,
`docs/data-flow.md`. Test catalogue: `docs/test-cases.md`. Viva preparation:
`docs/viva-qa.md`.*
