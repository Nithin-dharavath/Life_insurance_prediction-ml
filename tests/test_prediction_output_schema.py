"""Tests for the `Output` Pydantic schema used by the prediction endpoint."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from schema.prediction_validation import Output


def test_output_accepts_valid_payload():
    out = Output(
        predicted_category="High",
        confidence=0.9,
        class_probabilities={"High": 0.9, "Low": 0.05, "Medium": 0.05},
    )
    assert out.predicted_category == "High"
    assert out.confidence == 0.9
    assert out.class_probabilities == {"High": 0.9, "Low": 0.05, "Medium": 0.05}


def test_output_missing_predicted_category():
    with pytest.raises(ValidationError):
        Output(confidence=0.9, class_probabilities={"High": 0.9})


def test_output_missing_confidence():
    with pytest.raises(ValidationError):
        Output(predicted_category="High", class_probabilities={"High": 0.9})


def test_output_missing_class_probabilities():
    with pytest.raises(ValidationError):
        Output(predicted_category="High", confidence=0.9)


def test_output_accepts_class_probabilities_with_any_keys():
    # The schema does not constrain the dict keys today — it accepts
    # any string->float mapping. Locking this in so future tightening
    # of the schema is detected.
    out = Output(
        predicted_category="High",
        confidence=0.5,
        class_probabilities={"foo": 0.5, "bar": 0.5},
    )
    assert out.class_probabilities == {"foo": 0.5, "bar": 0.5}