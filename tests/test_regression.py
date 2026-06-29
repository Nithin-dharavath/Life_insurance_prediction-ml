"""Regression tests migrated from `model/regression_test.py`.

The original script ran as `python model/regression_test.py` and only
checked the response shape contract. This version uses pytest
parametrization, locks down the exact predicted category for each case
(so a model regression is caught), and asserts an accuracy floor
matching `MIN_ACCURACY = 0.5` defined in `model/train.py`.

If you intentionally retrain the model and the predicted_category for
one or more cases changes, update the `EXPECTED_CATEGORY` mapping below
after verifying the new outputs are correct.
"""

from __future__ import annotations

import pytest

from model.predict import class_labels, predict_output


MIN_ACCURACY = 0.5  # mirrors MIN_ACCURACY in model/train.py


TEST_CASES = [
    {
        "name": "typical high-risk",
        "input": {
            "income_lpa": 5.0,
            "occupation": "private_job",
            "bmi": 32.0,
            "age_group": "adult",
            "lifestyle_risk": "high",
            "city_tier": 1,
        },
    },
    {
        "name": "typical low-risk",
        "input": {
            "income_lpa": 15.0,
            "occupation": "government_job",
            "bmi": 22.0,
            "age_group": "middle-aged",
            "lifestyle_risk": "low",
            "city_tier": 2,
        },
    },
    {
        "name": "senior freelancer",
        "input": {
            "income_lpa": 3.0,
            "occupation": "freelancer",
            "bmi": 28.0,
            "age_group": "senior",
            "lifestyle_risk": "medium",
            "city_tier": 3,
        },
    },
    {
        "name": "student low-bmi",
        "input": {
            "income_lpa": 0.5,
            "occupation": "student",
            "bmi": 18.5,
            "age_group": "young",
            "lifestyle_risk": "low",
            "city_tier": 1,
        },
    },
    {
        "name": "unemployed high-risk",
        "input": {
            "income_lpa": 0.0,
            "occupation": "unemployed",
            "bmi": 35.0,
            "age_group": "adult",
            "lifestyle_risk": "high",
            "city_tier": 2,
        },
    },
]


# Categories captured from the trained model. If a deliberate retrain
# changes any of these, update here after validating the new output.
EXPECTED_CATEGORY = {
    "typical high-risk": "Medium",
    "typical low-risk": "Low",
    "senior freelancer": "High",
    "student low-bmi": "Low",
    "unemployed high-risk": "High",
}


@pytest.mark.parametrize(
    "case",
    TEST_CASES,
    ids=[c["name"] for c in TEST_CASES],
)
def test_regression_case_contract(case):
    """Each case returns a dict with the expected shape and labels."""
    result = predict_output(case["input"])

    assert isinstance(result, dict)
    assert set(result.keys()) == {
        "predicted_category",
        "confidence",
        "class_probabilities",
    }
    assert result["predicted_category"] in class_labels
    assert 0.0 <= result["confidence"] <= 1.0
    assert set(result["class_probabilities"].keys()) == set(class_labels)
    assert sum(result["class_probabilities"].values()) == pytest.approx(1.0, abs=1e-2)


@pytest.mark.parametrize(
    "case",
    TEST_CASES,
    ids=[c["name"] for c in TEST_CASES],
)
def test_regression_case_predicted_category_pinned(case):
    """The predicted category for each case is locked to its expected value.

    If this test fails after a retrain, it means the model's output for
    one of the canonical cases changed — verify the new behavior is
    intentional and update EXPECTED_CATEGORY.
    """
    result = predict_output(case["input"])
    assert result["predicted_category"] == EXPECTED_CATEGORY[case["name"]]


def test_minimum_accuracy_against_pinned_expectations():
    """Across all cases, the pinned-prediction match-rate must hold above
    the MIN_ACCURACY floor defined in model/train.py.

    Today this is 5/5 = 1.0 (every case is pinned). The floor is here
    so that if someone removes a pin or adds new cases without pinning,
    the floor catches silent accuracy drift below the threshold.
    """
    matches = sum(
        1
        for case in TEST_CASES
        if predict_output(case["input"])["predicted_category"]
        == EXPECTED_CATEGORY[case["name"]]
    )
    rate = matches / len(TEST_CASES)
    assert rate >= MIN_ACCURACY, (
        f"Regression accuracy {rate:.2%} below floor "
        f"{MIN_ACCURACY:.0%} ({matches}/{len(TEST_CASES)} cases matched)"
    )