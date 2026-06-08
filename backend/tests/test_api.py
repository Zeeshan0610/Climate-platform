"""Integration tests for the FastAPI endpoints."""
from __future__ import annotations


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_login_and_me(client, admin_headers):
    resp = client.get("/api/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


def test_requires_auth(client):
    assert client.get("/api/climate-data").status_code == 401


def test_climate_data_pagination(client, viewer_headers):
    resp = client.get("/api/climate-data?page=1&page_size=10", headers=viewer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] > 0
    assert len(body["items"]) == 10


def test_home_stats(client, viewer_headers):
    resp = client.get("/api/stats/home", headers=viewer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_records"] > 0
    assert body["total_countries"] >= 1
    assert 0 <= body["overall_quality_score"] <= 100


def test_analytics(client, viewer_headers):
    resp = client.get("/api/analytics", headers=viewer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "trends" in body and "distribution" in body and "statistics" in body


def test_forecast(client, viewer_headers):
    resp = client.get("/api/forecast?metric=temperature&periods=6", headers=viewer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["forecast"]) == 6
    assert body["model"]


def test_quality_metrics(client, viewer_headers):
    resp = client.get("/api/quality-metrics", headers=viewer_headers)
    assert resp.status_code == 200
    assert len(resp.json()["datasets"]) == 3


def test_interoperability(client, viewer_headers):
    resp = client.get("/api/interoperability-score", headers=viewer_headers)
    assert resp.status_code == 200
    assert len(resp.json()["pairs"]) == 3  # 3 sources -> 3 pairs


def test_accessibility(client, viewer_headers):
    resp = client.get("/api/accessibility-score", headers=viewer_headers)
    assert resp.status_code == 200
    assert resp.json()["overall_score"] > 0


def test_rbac_viewer_cannot_integrate(client, viewer_headers):
    resp = client.post("/api/integrate-data", headers=viewer_headers)
    assert resp.status_code == 403


def test_admin_audit_logs(client, admin_headers):
    resp = client.get("/api/audit-logs", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
