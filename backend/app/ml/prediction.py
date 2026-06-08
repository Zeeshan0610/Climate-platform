"""Climate prediction models: Random Forest (and optional XGBoost) with metrics."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

try:  # pragma: no cover
    from xgboost import XGBRegressor

    _HAS_XGB = True
except Exception:  # pragma: no cover
    _HAS_XGB = False


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out = out.dropna(subset=["date", "temperature"])
    out["month"] = out["date"].dt.month
    out["day_of_year"] = out["date"].dt.dayofyear
    out["year"] = out["date"].dt.year
    out["country_code"] = out["country"].astype("category").cat.codes
    return out


def _rmse(y_true, y_pred) -> float:
    return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))


def train_and_evaluate(df: pd.DataFrame, target: str = "temperature") -> dict:
    """Train RF (+XGB if available) to predict ``target`` and compare metrics."""
    feats = _build_features(df)
    feature_cols = ["month", "day_of_year", "year", "country_code", "humidity", "rainfall"]
    feature_cols = [c for c in feature_cols if c in feats.columns and c != target]
    data = feats.dropna(subset=feature_cols + [target])
    if len(data) < 20:
        return {"error": "insufficient data for training", "models": []}

    X = data[feature_cols]
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    results = []

    rf = RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    results.append(
        {
            "model": "RandomForest",
            "mae": round(mean_absolute_error(y_test, rf_pred), 3),
            "rmse": round(_rmse(y_test, rf_pred), 3),
            "r2": round(r2_score(y_test, rf_pred), 3),
        }
    )

    if _HAS_XGB:
        xgb = XGBRegressor(
            n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42
        )
        xgb.fit(X_train, y_train)
        xgb_pred = xgb.predict(X_test)
        results.append(
            {
                "model": "XGBoost",
                "mae": round(mean_absolute_error(y_test, xgb_pred), 3),
                "rmse": round(_rmse(y_test, xgb_pred), 3),
                "r2": round(r2_score(y_test, xgb_pred), 3),
            }
        )

    importance = sorted(
        (
            {"feature": f, "importance": round(float(i), 4)}
            for f, i in zip(feature_cols, rf.feature_importances_)
        ),
        key=lambda d: d["importance"],
        reverse=True,
    )

    return {
        "target": target,
        "n_samples": len(data),
        "features": feature_cols,
        "models": results,
        "feature_importance": importance,
        "best_model": min(results, key=lambda r: r["rmse"])["model"],
    }
