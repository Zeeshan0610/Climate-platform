"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, auth, climate, forecast, quality
from app.core.config import settings
from app.db.init_db import init

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("climate-platform")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=(
        "Accessibility-aware climate data harmonization & analytics framework. "
        "Demonstrates data ingestion, ETL, data quality, harmonization, "
        "interoperability, analytics, forecasting, ML, and WCAG accessibility."
    ),
)

origins = ["*"] if settings.CORS_ORIGINS == "*" else settings.CORS_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("Initializing database and ETL seed ...")
    init()
    logger.info("Startup complete.")


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok", "service": settings.PROJECT_NAME}


# Routers (prefixed under /api)
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(climate.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(forecast.router, prefix=settings.API_V1_PREFIX)
app.include_router(quality.router, prefix=settings.API_V1_PREFIX)
