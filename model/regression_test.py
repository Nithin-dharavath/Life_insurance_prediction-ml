import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from model.predict import predict_output, class_labels


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


def run_regression_tests():
    errors = []

    for case in TEST_CASES:
        name = case["name"]
        try:
            result = predict_output(case["input"])
        except Exception as e:
            errors.append(f"[{name}] Prediction raised exception: {e}")
            continue

        if not isinstance(result, dict):
            errors.append(f"[{name}] Result is not a dict")
            continue

        for key in ("predicted_category", "confidence", "class_probabilities"):
            if key not in result:
                errors.append(f"[{name}] Missing key '{key}' in result")
                continue

            if key == "predicted_category" and result[key] not in class_labels:
                errors.append(
                    f"[{name}] predicted_category '{result[key]}' not in known labels {class_labels}"
                )

        if "class_probabilities" in result:
            probas = result["class_probabilities"]
            missing_labels = [l for l in class_labels if l not in probas]
            if missing_labels:
                errors.append(
                    f"[{name}] class_probabilities missing expected labels: {missing_labels}"
                )

            total_prob = sum(probas.values())
            if abs(total_prob - 1.0) > 0.01:
                errors.append(
                    f"[{name}] class_probabilities sum to {total_prob:.4f}, expected ~1.0"
                )

    if errors:
        print("REGRESSION TEST FAILED")
        for err in errors:
            print(f"  FAIL: {err}")
        sys.exit(1)
    else:
        print(f"REGRESSION TEST PASSED ({len(TEST_CASES)} cases)")


if __name__ == "__main__":
    run_regression_tests()
