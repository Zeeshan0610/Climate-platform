# Accessible Climate Data Integration Platform

*An Accessibility-Aware Climate Data Harmonization and Analytics Framework*

An M.Tech Data Engineering capstone that ingests heterogeneous climate datasets
(NOAA, NASA, World Bank), harmonizes them into a unified canonical schema,
validates data quality, measures interoperability & reliability, and serves an
**accessibility-first** (WCAG 2.1 AA) analytics dashboard with forecasting and ML.

---

## Features

**Data Engineering**
- Multi-source ingestion (CSV, JSON, API) with batch & incremental loading
- Schema-mapping & harmonization engine (column standardization, unit conversion
  Fahrenheit→Celsius / inches→mm / miles→km, country & date normalization)
- Data quality layer: missing-value detection + imputation (mean/median/ffill),
  duplicate removal, outlier detection (IQR + z-score), validation rules, scoring
- Interoperability metrics (schema, semantic, mapping success, integration score)
- Reliability metrics (completeness, consistency, accuracy, availability)

**Analytics & ML**
- Temperature / rainfall / humidity trend analysis + statistical summaries
- Forecasting with ARIMA (statsmodels) and a robust linear-trend fallback
- ML prediction (Random Forest, optional XGBoost) with MAE / RMSE / R² and
  feature importance

**Accessibility (the unique contribution)**
- Light / Dark / **High-Contrast** themes, font scaling, color-blind-safe chart
  palettes (Okabe–Ito), text-to-speech narration
- Keyboard shortcuts (Alt+1..6 nav, Alt+T theme, Alt+± font), skip links,
  visible focus indicators, ARIA labels, semantic landmarks
- WCAG 2.1 POUR scoring dashboard

**Platform**
- FastAPI REST API, JWT auth, role-based access (admin / analyst / viewer),
  audit logs
- React + Material UI frontend (Recharts visualizations)
- PostgreSQL storage (SQLite for local dev), Dockerized with Docker Compose

---

## Architecture

```
 Sources (NOAA CSV · NASA JSON · World Bank CSV)
        │  ingestion (pandas/requests)
        ▼
 Harmonization  →  Data Quality  →  PostgreSQL  →  FastAPI  →  React Dashboard
 (schema/units)    (clean/score)     (storage)      (REST/JWT)   (WCAG 2.1)
                                         │
                          Analytics · Forecasting (ARIMA) · ML (RF/XGB)
```

See [docs/architecture.md](docs/architecture.md), [docs/er-diagram.md](docs/er-diagram.md),
and [docs/data-flow.md](docs/data-flow.md) for diagrams.

---

## Quick Start (Docker)

```bash
cp .env.example .env          # adjust SECRET_KEY for production
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API + docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432 (climate/climate)

On first boot the backend creates tables, seeds demo users, and runs the ETL
pipeline to load ~2,160 harmonized climate records.

**Demo accounts:** `admin/admin123` · `analyst/analyst123` · `viewer/viewer123`

---

## Local Development

### Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload          # http://localhost:8000
pytest                                 # run tests
ruff check app tests                   # lint
```
Defaults to SQLite (`climate.db`). Set `DATABASE_URL` to use PostgreSQL.

### Frontend
```bash
cd frontend
npm install
npm run dev                            # http://localhost:5173 (proxies /api -> :8000)
npm test                               # vitest
npm run lint
```

---

## Running in VS Code

1. **Open the project:** `File ▸ Open Folder…` → select the `climate-platform`
   folder. (Recommended extensions: *Python*, *Pylance*, *ESLint*, *Docker*.)
2. **Backend terminal** (Terminal ▸ New Terminal):
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload      # http://localhost:8000  (docs: /docs)
   ```
   On first run it auto-creates the SQLite DB, seeds demo users, and loads ETL data.
3. **Frontend terminal** (split terminal, `+` icon):
   ```bash
   cd frontend
   npm install
   npm run dev                        # http://localhost:5173
   ```
4. Open http://localhost:5173 and sign in with `admin` / `admin123`.

**After the one-time setup, start everything with one click:** double-click
`start.bat` (or run `.\start.ps1`) in the project root — it launches the backend
and frontend in two windows automatically.

**Run everything with Docker instead** (needs Docker Desktop): open the folder in
VS Code and run `docker compose up --build`, then open http://localhost:3000.

> Tip: press **F5** with the Python extension to debug the backend (select the
> `uvicorn` / FastAPI module), or set breakpoints and use *Run and Debug*.

---

## Running from GitHub

```bash
git clone https://github.com/<your-username>/climate-platform.git
cd climate-platform
```

Then either:

- **Docker (one command):**
  ```bash
  cp .env.example .env
  docker compose up --build
  # frontend http://localhost:3000 · API http://localhost:8000/docs
  ```
- **Manual:** follow the *Running in VS Code* steps above (backend venv +
  `uvicorn`, frontend `npm run dev`).

To push this project to a new GitHub repo for the first time:
```bash
# create an EMPTY repo at https://github.com/new (no README/.gitignore/license)
git remote add origin https://github.com/<your-username>/climate-platform.git
git branch -M main
git push -u origin main
```

---

## API Overview

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/login` | public | Obtain JWT |
| GET | `/api/auth/me` | any | Current user |
| POST | `/api/auth/users` | admin | Create user |
| GET | `/api/climate-data` | viewer | Paginated records (filters: country/source/year) |
| GET | `/api/stats/home` | viewer | Home KPIs |
| GET | `/api/analytics` | viewer | Trends, distribution, statistics |
| GET | `/api/analytics/ml` | viewer | ML model comparison |
| GET | `/api/forecast` | viewer | ARIMA forecast |
| GET | `/api/quality-metrics` | viewer | Data quality scores |
| GET | `/api/interoperability-score` | viewer | Interoperability matrix |
| GET | `/api/reliability-score` | viewer | Reliability scores |
| GET | `/api/accessibility-score` | viewer | WCAG report |
| POST | `/api/integrate-data` | analyst | Re-run ETL |
| POST | `/api/upload-dataset` | analyst | Upload + integrate a file |
| GET | `/api/audit-logs` | admin | Audit trail |

---

## Project Structure

```
climate-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routers (auth, climate, analytics, forecast, quality)
│   │   ├── core/         # config + security (JWT, hashing, RBAC)
│   │   ├── db/           # SQLAlchemy models, session, init/seed
│   │   ├── etl/          # ingestion, harmonization, data_quality, pipeline, generators
│   │   ├── ml/           # forecasting (ARIMA), prediction (RF/XGB)
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # analytics, accessibility, audit, dataframe helpers
│   └── tests/            # pytest (ETL unit + API integration)
├── frontend/             # React + MUI + Recharts (accessibility engine + 6 pages)
├── docs/                 # architecture, ER, DFD, user manual, test cases, viva Q&A
├── docker-compose.yml
└── README.md
```

---

## Documentation

- [Architecture](docs/architecture.md)
- [ER Diagram](docs/er-diagram.md)
- [Data Flow Diagram](docs/data-flow.md)
- [User Manual](docs/user-manual.md)
- [Test Cases](docs/test-cases.md)
- [Viva Questions & Answers](docs/viva-qa.md)

---

## Tech Stack

React · Material UI · Recharts · FastAPI · SQLAlchemy · Pandas · NumPy ·
scikit-learn · statsmodels · PostgreSQL · JWT · Docker · PyTest · Vitest
