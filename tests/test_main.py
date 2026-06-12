"""Unit tests for AI/ML Q&A Agent."""
import os
import pytest
from fastapi.testclient import TestClient

# Set env vars before importing app
os.environ["AGENT_API_KEY"] = "test-key-123"
os.environ["ENVIRONMENT"] = "test"
os.environ["RATE_LIMIT_PER_MINUTE"] = "100"

from app.main import app

client = TestClient(app)
API_KEY = "test-key-123"


# ─────────────────────────────────────────────────────────
# Health & Readiness
# ─────────────────────────────────────────────────────────

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "uptime_seconds" in data
    assert "version" in data


def test_ready_returns_true():
    # Use lifespan context so startup sets _is_ready = True
    with TestClient(app) as c:
        response = c.get("/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_root_returns_info():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "endpoints" in data


# ─────────────────────────────────────────────────────────
# Authentication
# ─────────────────────────────────────────────────────────

def test_ask_without_api_key_returns_401():
    response = client.post("/ask", json={"question": "what is ML?"})
    assert response.status_code == 401


def test_ask_with_wrong_api_key_returns_401():
    response = client.post(
        "/ask",
        json={"question": "what is ML?"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401


def test_ask_with_valid_api_key_returns_200():
    response = client.post(
        "/ask",
        json={"question": "what is machine learning?"},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "question" in data
    assert "model" in data
    assert "timestamp" in data


# ─────────────────────────────────────────────────────────
# Input Validation
# ─────────────────────────────────────────────────────────

def test_ask_empty_question_returns_422():
    response = client.post(
        "/ask",
        json={"question": ""},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 422


def test_ask_missing_question_returns_422():
    response = client.post(
        "/ask",
        json={},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 422


# ─────────────────────────────────────────────────────────
# Mock LLM responses
# ─────────────────────────────────────────────────────────

def test_ask_about_ml_returns_answer():
    response = client.post(
        "/ask",
        json={"question": "what is machine learning?"},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 200
    assert len(response.json()["answer"]) > 0


def test_ask_about_deep_learning_returns_answer():
    response = client.post(
        "/ask",
        json={"question": "explain deep learning"},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 200
    assert len(response.json()["answer"]) > 0


# ─────────────────────────────────────────────────────────
# Metrics (protected)
# ─────────────────────────────────────────────────────────

def test_metrics_without_key_returns_401():
    response = client.get("/metrics")
    assert response.status_code == 401


def test_metrics_with_key_returns_200():
    response = client.get("/metrics", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "daily_cost_usd" in data
