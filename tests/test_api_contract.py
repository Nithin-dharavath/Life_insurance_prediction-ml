"""FastAPI contract tests for the prediction service.

These tests use a session-scoped `TestClient` (defined in conftest.py).
The `_metrics` dict in `app.py` is mutated under a lock, so tests in
this file need to snapshot/restore it to avoid order-dependent assertions.
"""

from __future__ import annotations

import pytest

from app import _metrics


@pytest.fixture(autouse=True)
def reset_metrics():
    """Snapshot `_metrics` before each test and restore after.

    We snapshot before and restore after — never zero — so the test
    suite can never accidentally pass against a zeroed counter while
    a real one is incrementing under it.
    """
    snapshot = dict(_metrics)
    yield
    _metrics.clear()
    _metrics.update(snapshot)


# --- GET / --------------------------------------------------------------


def test_home_returns_message(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "insurance premium"}


def test_home_increments_requests_total(client):
    before = _metrics["requests_total"]
    client.get("/")
    assert _metrics["requests_total"] == before + 1


# --- GET /health --------------------------------------------------------


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["version"], str)
    assert body["version"]  # non-empty


# --- GET /metrics -------------------------------------------------------


def test_metrics_shape(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {
        "requests_total",
        "predict_success_total",
        "predict_failure_total",
    }
    for v in body.values():
        assert isinstance(v, int)
        assert v >= 0


def test_health_and_metrics_do_not_increment_requests_total(client):
    # /health and /metrics deliberately do not bump requests_total —
    # only / and /predict do. Verify this so a future change is noticed.
    before = _metrics["requests_total"]
    client.get("/health")
    client.get("/metrics")
    assert _metrics["requests_total"] == before


# --- POST /predict: happy path -----------------------------------------


def test_predict_happy_path(client, sample_payload):
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    body = response.json()
    assert "Response" in body
    inner = body["Response"]
    assert inner["predicted_category"] in {"High", "Low", "Medium"}
    assert 0.0 <= inner["confidence"] <= 1.0
    # class_probabilities sums to ~1.0
    total = sum(inner["class_probabilities"].values())
    assert total == pytest.approx(1.0, abs=1e-2)


def test_predict_increments_predict_success_total(client, sample_payload):
    before = _metrics["predict_success_total"]
    client.post("/predict", json=sample_payload)
    assert _metrics["predict_success_total"] == before + 1


def test_predict_increments_requests_total(client, sample_payload):
    before = _metrics["requests_total"]
    client.post("/predict", json=sample_payload)
    assert _metrics["requests_total"] == before + 1


def test_predict_response_has_capital_response_key(client, sample_payload):
    # The wrapper key is "Response" (capital R), added by app.py line 86.
    # Locks this against accidental renaming.
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    body = response.json()
    assert "Response" in body
    assert "response" not in body


# --- POST /predict: validation errors ---------------------------------


def test_predict_rejects_age_above_limit(client, sample_payload):
    sample_payload["age"] = 200
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_predict_rejects_negative_weight(client, sample_payload):
    sample_payload["weight"] = -1
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 422


def test_predict_rejects_unknown_occupation(client, sample_payload):
    sample_payload["occupation"] = "pirate"
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 422


def test_predict_rejects_unsupported_city(client, sample_payload):
    sample_payload["city"] = "Atlantis"
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 422


def test_predict_validation_error_does_not_increment_failure_total(
    client, sample_payload
):
    # 422 happens in FastAPI's request-validation layer, BEFORE the
    # handler's try/except — so predict_failure_total must NOT move.
    before = _metrics["predict_failure_total"]
    sample_payload["age"] = 200
    client.post("/predict", json=sample_payload)
    assert _metrics["predict_failure_total"] == before


# --- POST /predict: server-error path ---------------------------------


def test_predict_returns_500_when_predict_output_raises(
    client, sample_payload, monkeypatch
):
    # Patch the symbol as imported into app.py (not the source module)
    # so the handler's reference resolves to the broken function.
    def boom(_payload):
        raise RuntimeError("intentional test failure")

    monkeypatch.setattr("app.predict_output", boom)

    before = _metrics["predict_failure_total"]
    response = client.post("/predict", json=sample_payload)
    assert response.status_code == 500
    assert response.json() == {"error": "Internal server error"}
    assert _metrics["predict_failure_total"] == before + 1


def test_predict_500_does_not_increment_success_total(
    client, sample_payload, monkeypatch
):
    def boom(_payload):
        raise RuntimeError("intentional test failure")

    monkeypatch.setattr("app.predict_output", boom)

    before = _metrics["predict_success_total"]
    client.post("/predict", json=sample_payload)
    assert _metrics["predict_success_total"] == before


# --- CORS ---------------------------------------------------------------


def test_predict_options_returns_cors_headers(client):
    # Lightweight CORS smoke check — full CORS spec coverage is out of
    # scope for Phase 6. Just verify the middleware emits the header.
    response = client.options(
        "/predict",
        headers={
            "Origin": "http://localhost",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" in {k.lower() for k in response.headers}