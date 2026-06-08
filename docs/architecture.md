# System Architecture

The platform follows a layered data-engineering architecture.

```mermaid
flowchart TD
    subgraph Sources["Layer 1 · Data Sources"]
        A1[NOAA CSV<br/>Fahrenheit, inches]
        A2[NASA JSON<br/>Celsius, mm]
        A3[World Bank CSV<br/>country codes]
    end

    subgraph Ingest["Layer 2 · Ingestion"]
        B[Pandas / Requests<br/>batch · API · incremental]
    end

    subgraph Harmon["Layer 4 · Harmonization"]
        C[Schema mapping<br/>unit conversion<br/>country/date normalization]
    end

    subgraph Quality["Layer 3 · Data Quality"]
        D[Missing imputation<br/>dedup · outliers IQR/Z<br/>validation · scoring]
    end

    subgraph Store["Layer 5 · Storage"]
        E[(PostgreSQL<br/>records, metrics, users, audit)]
    end

    subgraph Analytics["Layer 6 · Analytics & ML"]
        F[Trends · Statistics]
        G[Forecast ARIMA]
        H[ML RF / XGBoost]
    end

    subgraph API["FastAPI · JWT · RBAC"]
        I[REST endpoints]
    end

    subgraph UI["Layer 7+8 · Accessible Dashboard"]
        J[React + MUI + Recharts<br/>WCAG 2.1 engine]
    end

    A1 & A2 & A3 --> B --> C --> D --> E
    E --> F & G & H --> I --> J
```

## Layer responsibilities

| Layer | Responsibility | Key modules |
|-------|----------------|-------------|
| Ingestion | Read CSV/JSON/API into DataFrames | `app/etl/ingestion.py` |
| Harmonization | Canonical schema + unit/value normalization | `app/etl/harmonization.py` |
| Data Quality | Clean, validate, score | `app/etl/data_quality.py` |
| Orchestration | Run ETL, persist records + metrics | `app/etl/pipeline.py` |
| Storage | Relational persistence | `app/db/models.py` |
| Analytics | Trends, distributions, statistics | `app/services/analytics.py` |
| Forecasting | ARIMA + linear fallback | `app/ml/forecasting.py` |
| ML | RF/XGBoost evaluation | `app/ml/prediction.py` |
| API | REST, auth, RBAC, audit | `app/api/*` |
| Accessibility | WCAG engine, themes, TTS | `frontend/src/context/AccessibilityContext.jsx` |

## Security
- JWT bearer tokens (HS256), bcrypt password hashing.
- Hierarchical RBAC: `viewer < analyst < admin` enforced via FastAPI dependencies.
- Audit logging of sensitive actions (login, user creation, ETL runs, uploads).

## Deployment
Three Docker services orchestrated by Docker Compose: `db` (PostgreSQL),
`backend` (FastAPI/uvicorn), `frontend` (nginx serving the built React SPA and
proxying `/api`).
