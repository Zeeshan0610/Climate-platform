"""Forecasting module: ARIMA (statsmodels) with a linear-trend fallback.

Prophet is intentionally avoided as a hard dependency because it is heavy and
brittle to install; ARIMA from statsmodels provides comparable functionality
for this dataset. If statsmodels is unavailable, a deterministic linear
regression on the time index is used so the API never fails.
"""
from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

try:  # pragma: no cover - exercised indirectly
    from statsmodels.tsa.arima.model import ARIMA

    _HAS_STATSMODELS = True
except Exception:  # pragma: no cover
    _HAS_STATSMODELS = False


def _aggregate_monthly(df: pd.DataFrame, metric: str) -> pd.Series:
    s = df[["date", metric]].dropna().copy()
    s["date"] = pd.to_datetime(s["date"])
    s = s.set_index("date").sort_index()
    monthly = s[metric].resample("MS").mean().dropna()
    return monthly


def _linear_forecast(series: pd.Series, periods: int) -> np.ndarray:
    y = series.values.astype(float)
    x = np.arange(len(y))
    if len(y) < 2:
        return np.repeat(y[-1] if len(y) else 0.0, periods)
    coef = np.polyfit(x, y, 1)
    future_x = np.arange(len(y), len(y) + periods)
    return np.polyval(coef, future_x)


def forecast_metric(
    df: pd.DataFrame, metric: str = "temperature", periods: int = 12
) -> dict:
    """Forecast ``metric`` for ``periods`` future months.

    Returns dict with history, forecast points, model name.
    """
    if metric not in {"temperature", "rainfall", "humidity"}:
        raise ValueError("metric must be temperature, rainfall, or humidity")

    monthly = _aggregate_monthly(df, metric)
    history = [
        {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)}
        for d, v in monthly.items()
    ]

    model_name = "linear-trend"
    forecast_values: np.ndarray

    if _HAS_STATSMODELS and len(monthly) >= 8:
        try:
            model = ARIMA(monthly, order=(1, 1, 1))
            fitted = model.fit()
            forecast_values = np.asarray(fitted.forecast(steps=periods))
            model_name = "ARIMA(1,1,1)"
        except Exception:
            forecast_values = _linear_forecast(monthly, periods)
    else:
        forecast_values = _linear_forecast(monthly, periods)

    last_date = monthly.index[-1] if len(monthly) else pd.Timestamp.today()
    future_dates = pd.date_range(
        start=last_date + pd.offsets.MonthBegin(1), periods=periods, freq="MS"
    )
    forecast = [
        {"date": d.strftime("%Y-%m-%d"), "value": round(float(v), 2)}
        for d, v in zip(future_dates, forecast_values)
    ]

    return {
        "metric": metric,
        "model": model_name,
        "history": history,
        "forecast": forecast,
    }
