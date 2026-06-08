# User Manual

## 1. Getting Started

### Run with Docker
```bash
cp .env.example .env
docker compose up --build
```
Open http://localhost:3000 and sign in.

| Role | Username | Password | Capabilities |
|------|----------|----------|--------------|
| Admin | `admin` | `admin123` | Everything + user management + audit logs |
| Analyst | `analyst` | `analyst123` | View + run ETL + upload datasets |
| Viewer | `viewer` | `viewer123` | View dashboards only |

## 2. Dashboard Pages

1. **Home** — KPI cards: total records, countries, datasets, average
   temperature/rainfall/humidity, data-quality, accessibility & interoperability
   scores.
2. **Climate Analytics** — temperature/humidity & rainfall trend lines, average
   by country, statistical summary, ML model comparison. Filter by country/year.
3. **Accessibility** — overall WCAG score, POUR principle breakdown, live
   controls (theme, font scale, color-blind palette, voice narration), feature
   list.
4. **Data Quality** — overall & per-dataset scores, dimension bar chart, radar
   "heatmap", and a metrics table (duplicates removed, outliers, imputed).
5. **Interoperability** — integration score, schema/semantic/mapping bars, and a
   compatibility matrix across source pairs.
6. **Forecast** — choose a metric and horizon; view historical vs. predicted
   line chart (model label shown).

## 3. Accessibility Controls

| Action | Shortcut | Where |
|--------|----------|-------|
| Navigate pages | `Alt+1` … `Alt+6` | global |
| Cycle theme (Light/Dark/High-Contrast) | `Alt+T` | toolbar |
| Increase font | `Alt+=` | toolbar |
| Decrease font | `Alt+-` | toolbar |
| Skip to content | `Tab` then `Enter` on "Skip to main content" | top of page |
| Toggle color-blind palette | toolbar palette icon | toolbar |
| Toggle voice narration | toolbar voice icon | toolbar |

Preferences persist in the browser via `localStorage`.

## 4. Re-running the ETL / Uploading Data
- **Re-run ETL:** as analyst/admin, `POST /api/integrate-data` (or via API docs).
- **Upload a dataset:** `POST /api/upload-dataset?source=NOAA` with a CSV/JSON
  file matching a known source schema; the file is harmonized, quality-checked,
  and loaded.

## 5. API Documentation
Interactive OpenAPI docs are available at http://localhost:8000/docs.
