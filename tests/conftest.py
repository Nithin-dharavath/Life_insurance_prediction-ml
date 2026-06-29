"""Shared pytest fixtures for the test suite."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import app
from schema.user_input import UserInput


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI TestClient. Session-scoped so the app + model load once."""
    return TestClient(app)


@pytest.fixture
def sample_payload() -> dict:
    """A payload that passes `UserInput` validation.

    BMI for these values: 70 / 1.75^2 == 22.8571...
    """
    return {
        "age": 30,
        "weight": 70.0,
        "height": 1.75,
        "income_lpa": 10.0,
        "occupation": "private_job",
        "smoker": False,
        "city": "Mumbai",
    }


@pytest.fixture
def predict_input(sample_payload: dict) -> dict:
    """The derived-feature dict that `app.py` passes to `predict_output`.

    Keys must match the training-time feature order defined in
    `model/train.py` (income_lpa, occupation, bmi, age_group,
    lifestyle_risk, city_tier).
    """
    user = UserInput(**sample_payload)
    return {
        "income_lpa": user.income_lpa,
        "occupation": user.occupation,
        "bmi": user.bmi,
        "age_group": user.age_group,
        "lifestyle_risk": user.lifestyle_risk,
        "city_tier": user.city_tier,
    }