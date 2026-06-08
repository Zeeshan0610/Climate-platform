# Test Cases

## Automated tests

### Backend (PyTest) — `backend/tests/`
| ID | Test | Type | Expected |
|----|------|------|----------|
| BE-01 | `test_unit_conversions` | Unit | 32°F→0°C, 212°F→100°C, 1in→25.4mm, 1mi→1.609km |
| BE-02 | `test_country_normalization` | Unit | `IND`/`INDIA`/`brazil` → canonical names |
| BE-03 | `test_harmonize_noaa_schema_and_units` | Unit | NOAA columns mapped; units converted |
| BE-04 | `test_iso_dates_parsed_correctly` | Unit | ISO dates not corrupted by day-first parsing |
| BE-05 | `test_data_quality_removes_outlier_and_dedupes` | Unit | 580°C removed, dup removed, missing imputed |
| BE-06 | `test_health` | Integration | `/health` returns ok |
| BE-07 | `test_login_and_me` | Integration | JWT issued; `/auth/me` returns admin |
| BE-08 | `test_requires_auth` | Integration | Protected route → 401 without token |
| BE-09 | `test_climate_data_pagination` | Integration | Paginated records returned |
| BE-10 | `test_home_stats` | Integration | KPIs computed |
| BE-11 | `test_analytics` | Integration | trends/distribution/statistics present |
| BE-12 | `test_forecast` | Integration | forecast length == requested periods |
| BE-13 | `test_quality_metrics` | Integration | 3 dataset metric rows |
| BE-14 | `test_interoperability` | Integration | 3 source pairs |
| BE-15 | `test_accessibility` | Integration | overall score > 0 |
| BE-16 | `test_rbac_viewer_cannot_integrate` | Integration | viewer → 403 on ETL |
| BE-17 | `test_admin_audit_logs` | Integration | audit list returned |

Run: `cd backend && pytest`

### Frontend (Vitest) — `frontend/src/test/`
| ID | Test | Expected |
|----|------|----------|
| FE-01 | light theme default | `palette.mode === "light"` |
| FE-02 | dark theme | `palette.mode === "dark"` |
| FE-03 | high-contrast theme | black bg, yellow primary |
| FE-04 | font scaling | `fontSize ≈ 21` at 1.5x |
| FE-05 | color-blind palette enabled | returns Okabe–Ito palette |
| FE-06 | default palette | differs from color-blind palette |

Run: `cd frontend && npm test`

## Manual / Acceptance tests
| ID | Scenario | Steps | Expected |
|----|----------|-------|----------|
| M-01 | Login | Sign in as viewer | Redirect to Home with KPIs |
| M-02 | RBAC | Viewer hits ETL endpoint | 403 Forbidden |
| M-03 | Keyboard nav | Press `Alt+2` | Navigates to Analytics |
| M-04 | High contrast | Press `Alt+T` twice | High-contrast theme applied |
| M-05 | Font scaling | Press `Alt+=` several times | Text enlarges, layout intact |
| M-06 | Color-blind charts | Toggle palette icon | Chart colors switch to Okabe–Ito |
| M-07 | Voice narration | Enable TTS, open Home | Summary spoken aloud |
| M-08 | Forecast | Select rainfall, 24 months | Historical vs predicted chart renders |
| M-09 | Skip link | Tab on page load, Enter | Focus jumps to main content |

## Accessibility testing
Validate with browser DevTools Lighthouse / axe: target contrast ≥ 4.5:1,
all interactive elements keyboard-reachable, ARIA labels present, single `<h1>`
per page with logical heading order.
