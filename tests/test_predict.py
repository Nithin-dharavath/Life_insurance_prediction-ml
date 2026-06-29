"""Tests for `model.predict.predict_output`.

These tests require the trained `model/model.pkl` artifact and the
`model/model_metadata.json` metadata file. They exercise the function
that's the boundary between serving and the model itself.
"""

from __future__ import annotations

import pytest

from model.predict import (
    EXPECTED_LABELS,
    Model_version,
    class_labels,
    predict_output,
)


# --- module-level sanity checks ----------------------------------------


def test_class_labels_match_expected():
    # Imports from model.predict.py perform an import-time guard that
    # raises RuntimeError if learned labels diverge from EXPECTED_LABELS.
    # The fact that we got here means they match.
    assert sorted(class_labels) == sorted(EXPECTED_LABELS)


def test_expected_labels_set():
    # Locks the expected label set. If training ever produces a 4th
    # class, this will fail and force a deliberate update.
    assert set(EXPECTED_LABELS) == {"High", "Low", "Medium"}


def test_model_version_is_a_non_empty_string():
    assert isinstance(Model_version, str)
    assert Model_version  # non-empty


# --- predict_output shape ----------------------------------------------


def test_predict_output_returns_dict_with_three_keys(predict_input):
    result = predict_output(predict_input)
    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "predicted_category",
        "confidence",
        "class_probabilities",
    }


def test_predict_output_predicted_category_in_class_labels(predict_input):
    result = predict_output(predict_input)
    assert result["predicted_category"] in class_labels


def test_predict_output_confidence_in_unit_interval(predict_input):
    result = predict_output(predict_input)
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_output_class_probabilities_keys_match_labels(predict_input):
    result = predict_output(predict_input)
    assert set(result["class_probabilities"].keys()) == set(class_labels)


def test_predict_output_class_probabilities_sum_to_one(predict_input):
    result = predict_output(predict_input)
    total = sum(result["class_probabilities"].values())
    # Implementation should produce an exact (FP-epsilon) sum of 1.0;
    # the older hand-rolled script allowed 0.01 drift, but the new
    # tolerance should be much tighter.
    assert total == pytest.approx(1.0, abs=1e-6)


def test_predict_output_confidence_equals_max_probability(predict_input):
    # confidence is defined as the max of predict_proba; assert the
    # invariant so a future refactor doesn't break it silently.
    result = predict_output(predict_input)
    assert result["confidence"] == max(result["class_probabilities"].values())


# --- rounding ----------------------------------------------------------


def test_predict_output_confidence_rounded_to_four_decimals(predict_input):
    result = predict_output(predict_input)
    # 10000 * x must be a whole number (with possible FP noise)
    scaled = result["confidence"] * 10000
    assert scaled == pytest.approx(round(scaled), abs=1e-6)


def test_predict_output_class_probabilities_rounded_to_four_decimals(predict_input):
    result = predict_output(predict_input)
    for prob in result["class_probabilities"].values():
        scaled = prob * 10000
        assert scaled == pytest.approx(round(scaled), abs=1e-6)


# --- determinism -------------------------------------------------------


def test_predict_output_is_deterministic(predict_input):
    a = predict_output(predict_input)
    b = predict_output(predict_input)
    assert a == b


def test_predict_output_deterministic_with_high_risk_input():
    # Use the same "high-risk" shape used in the regression suite to
    # make sure that specific case is reproducible.
    risky = {
        "income_lpa": 5.0,
        "occupation": "private_job",
        "bmi": 32.0,
        "age_group": "adult",
        "lifestyle_risk": "high",
        "city_tier": 1,
    }
    a = predict_output(risky)
    b = predict_output(risky)
    assert a == b