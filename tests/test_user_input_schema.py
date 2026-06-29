"""Pydantic validation tests for the `UserInput` schema."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from schema.user_input import UserInput


# --- happy path ---------------------------------------------------------


def test_user_input_accepts_valid_payload(sample_payload):
    user = UserInput(**sample_payload)
    assert user.age == 30
    assert user.weight == 70.0
    assert user.height == 1.75
    assert user.income_lpa == 10.0
    assert user.occupation == "private_job"
    assert user.smoker is False
    assert user.city == "Mumbai"


def test_user_input_computes_bmi(sample_payload):
    user = UserInput(**sample_payload)
    # 70 / 1.75^2 == 22.857...
    assert user.bmi == pytest.approx(22.857, rel=1e-3)


def test_user_input_computes_age_group(sample_payload):
    user = UserInput(**sample_payload)
    assert user.age_group == "adult"


def test_user_input_computes_lifestyle_risk(sample_payload):
    user = UserInput(**sample_payload)
    # 70kg / 1.75m = BMI 22.86, non-smoker → low
    assert user.lifestyle_risk == "low"


def test_user_input_computes_city_tier(sample_payload):
    user = UserInput(**sample_payload)
    assert user.city_tier == 1


# --- field rejections ---------------------------------------------------


@pytest.mark.parametrize("bad_age", [0, -1, 120, 121, -100])
def test_user_input_rejects_bad_age(sample_payload, bad_age):
    sample_payload["age"] = bad_age
    with pytest.raises(ValidationError):
        UserInput(**sample_payload)


@pytest.mark.parametrize("bad_weight", [0, -1, -70])
def test_user_input_rejects_nonpositive_weight(sample_payload, bad_weight):
    sample_payload["weight"] = bad_weight
    with pytest.raises(ValidationError):
        UserInput(**sample_payload)


@pytest.mark.parametrize("bad_height", [0, -1])
def test_user_input_rejects_nonpositive_height(sample_payload, bad_height):
    sample_payload["height"] = bad_height
    with pytest.raises(ValidationError):
        UserInput(**sample_payload)


@pytest.mark.parametrize("bad_income", [0, -1, -10.0])
def test_user_input_rejects_nonpositive_income(sample_payload, bad_income):
    sample_payload["income_lpa"] = bad_income
    with pytest.raises(ValidationError):
        UserInput(**sample_payload)


def test_user_input_rejects_unknown_occupation(sample_payload):
    sample_payload["occupation"] = "pirate"
    with pytest.raises(ValidationError):
        UserInput(**sample_payload)


def test_user_input_rejects_unsupported_city(sample_payload):
    sample_payload["city"] = "Atlantis"
    with pytest.raises(ValidationError):
        UserInput(**sample_payload)


def test_user_input_coerces_truthy_strings_to_smoker_true(sample_payload):
    # Documents Pydantic v2's bool_parsing behavior: the strings "true",
    # "True", "TRUE", and "yes" (and variants) coerce to True.
    for raw in ("yes", "Yes", "YES", "true", "True", "TRUE"):
        sample_payload["smoker"] = raw
        user = UserInput(**sample_payload)
        assert user.smoker is True, f"failed for {raw!r}"


def test_user_input_coerces_falsy_strings_to_smoker_false(sample_payload):
    # Symmetric: "false"/"no" coerce to False.
    for raw in ("no", "No", "NO", "false", "False", "FALSE"):
        sample_payload["smoker"] = raw
        user = UserInput(**sample_payload)
        assert user.smoker is False, f"failed for {raw!r}"


def test_user_input_rejects_unparseable_smoker(sample_payload):
    # Strings that aren't recognized by Pydantic's bool_parsing are rejected.
    sample_payload["smoker"] = "not_a_bool_at_all"
    with pytest.raises(ValidationError):
        UserInput(**sample_payload)


# --- city normalization -------------------------------------------------


@pytest.mark.parametrize(
    "raw,normalized",
    [
        ("mumbai", "Mumbai"),
        ("MUMBAI", "Mumbai"),
        ("  mumbai  ", "Mumbai"),
        ("  Delhi  ", "Delhi"),
    ],
)
def test_user_input_normalizes_city(sample_payload, raw, normalized):
    sample_payload["city"] = raw
    user = UserInput(**sample_payload)
    assert user.city == normalized


def test_user_input_normalizes_then_rejects_unknown(sample_payload):
    # "atlantis" normalized to "Atlantis" — still not in the supported list
    sample_payload["city"] = "atlantis"
    with pytest.raises(ValidationError):
        UserInput(**sample_payload)


# --- every Literal occupation is accepted -------------------------------


@pytest.mark.parametrize(
    "occupation",
    [
        "retired",
        "freelancer",
        "student",
        "government_job",
        "business_owner",
        "unemployed",
        "private_job",
    ],
)
def test_user_input_accepts_every_literal_occupation(sample_payload, occupation):
    sample_payload["occupation"] = occupation
    user = UserInput(**sample_payload)
    assert user.occupation == occupation