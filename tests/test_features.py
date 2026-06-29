"""Unit tests for the pure functions in `features/__init__.py`.

These functions are the single source of truth for feature engineering
and are used by both training (`model/train.py`) and serving
(`schema/user_input.py`). They must stay in sync.
"""

from __future__ import annotations

import pytest

from features import (
    compute_age_group,
    compute_bmi,
    compute_city_tier,
    compute_lifestyle_risk,
)


# --- compute_bmi ---------------------------------------------------------


def test_compute_bmi_golden_value():
    # 70 kg / (1.75 m)^2 == 22.857142857...
    assert compute_bmi(70.0, 1.75) == pytest.approx(22.857, rel=1e-3)


def test_compute_bmi_returns_float():
    result = compute_bmi(70, 1.75)
    assert isinstance(result, float)


@pytest.mark.parametrize(
    "weight,height,expected",
    [
        (80.0, 2.0, 20.0),
        (50.0, 1.5, 22.222),
        (100.0, 1.0, 100.0),
    ],
)
def test_compute_bmi_parametrized(weight, height, expected):
    assert compute_bmi(weight, height) == pytest.approx(expected, rel=1e-3)


def test_compute_bmi_raises_on_zero_height():
    # Documents current behavior — `compute_bmi` does not guard against
    # zero/negative inputs and raises ZeroDivisionError. Validation is
    # the caller's responsibility (UserInput enforces height > 0).
    with pytest.raises(ZeroDivisionError):
        compute_bmi(70.0, 0.0)


# --- compute_age_group ---------------------------------------------------


@pytest.mark.parametrize(
    "age,expected",
    [
        (17, "young"),
        (18, "adult"),
        (44, "adult"),
        (45, "middle-aged"),
        (64, "middle-aged"),
        (65, "senior"),
        (100, "senior"),
        (1, "young"),
    ],
)
def test_compute_age_group_boundaries(age, expected):
    assert compute_age_group(age) == expected


# --- compute_lifestyle_risk ---------------------------------------------


@pytest.mark.parametrize(
    "smoker,bmi,expected",
    [
        # low: neither smoker nor BMI > 27
        (False, 20.0, "low"),
        (False, 27.0, "low"),  # boundary: 27 is NOT > 27
        # medium via smoker-only path
        (True, 25.0, "medium"),
        # medium via BMI-only path
        (False, 28.0, "medium"),
        (False, 30.0, "medium"),  # BMI exactly 30 still hits medium
        # medium: smoker AND BMI exactly 30 — high branch needs BMI > 30
        (True, 30.0, "medium"),
        # high: smoker AND BMI > 30
        (True, 31.0, "high"),
        (True, 35.0, "high"),
        (True, 30.01, "high"),
    ],
)
def test_compute_lifestyle_risk_truth_table(smoker, bmi, expected):
    assert compute_lifestyle_risk(smoker, bmi) == expected


# --- compute_city_tier ---------------------------------------------------


def test_compute_city_tier_tier_1():
    assert compute_city_tier("Mumbai") == 1
    assert compute_city_tier("Delhi") == 1
    assert compute_city_tier("Bangalore") == 1


def test_compute_city_tier_tier_2():
    assert compute_city_tier("Jaipur") == 2
    assert compute_city_tier("Chandigarh") == 2


def test_compute_city_tier_tier_3_fallback():
    # Unknown city → tier 3
    assert compute_city_tier("Springfield") == 3
    assert compute_city_tier("Atlantis") == 3


def test_compute_city_tier_case_sensitive():
    # The function does exact membership — caller (UserInput.city validator)
    # is responsible for normalization. This test documents that.
    assert compute_city_tier("mumbai") == 3