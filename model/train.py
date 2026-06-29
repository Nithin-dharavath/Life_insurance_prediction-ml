"""One-shot training script for the insurance premium prediction model.

Downloads the CSV dataset, engineers features, fits a
RandomForestClassifier pipeline with one-hot encoding, evaluates on a
test split, runs post-training validation, and persists the model
artifact along with training metadata.
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

from features import compute_bmi, compute_age_group, compute_lifestyle_risk, compute_city_tier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

EXPECTED_LABELS = ["High", "Low", "Medium"]
MIN_ACCURACY = 0.5


# -----------------------------
# 1. Load Dataset
# -----------------------------
_local_path = os.path.join(REPO_DIR, "data", "insurance.csv")
_remote_url = "https://raw.githubusercontent.com/campusx-official/fastapi-demo-api/refs/heads/main/insurance.csv"

if os.path.exists(_local_path):
    print(f"Loading dataset from {_local_path}")
    df = pd.read_csv(_local_path)
else:
    print(f"Local dataset not found at {_local_path}, falling back to remote URL")
    df = pd.read_csv(_remote_url)

# -----------------------------
# 2. Feature Engineering
# -----------------------------
df["bmi"] = df.apply(lambda row: compute_bmi(row["weight"], row["height"]), axis=1)
df["age_group"] = df["age"].apply(compute_age_group)
df["lifestyle_risk"] = df.apply(lambda row: compute_lifestyle_risk(row["smoker"], row["bmi"]), axis=1)
df["city_tier"] = df["city"].apply(compute_city_tier)

#remove the unwanted columns now
df = df.drop(columns=['age', 'weight', 'height', 'smoker', 'city'])[['income_lpa', 'occupation', 'bmi', 'age_group', 'lifestyle_risk', 'city_tier', 'insurance_premium_category']]

# -----------------------------
# 3. Define Features & Target
# -----------------------------
X = df.drop("insurance_premium_category", axis=1)
y = df["insurance_premium_category"]


# -----------------------------
# 4. Train-Test Split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# -----------------------------
# 5. Preprocessing
# -----------------------------
categorical_features = X.select_dtypes(include=["object", "string"]).columns

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
    ],
    remainder="passthrough"
)


# -----------------------------
# 6. Create Pipeline
# -----------------------------
pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier(random_state=42))
])


# -----------------------------
# 7. Train Model
# -----------------------------
pipeline.fit(X_train, y_train)


# -----------------------------
# 8. Evaluate Model
# -----------------------------
y_pred = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
cr = classification_report(y_test, y_pred, output_dict=True)
cm = confusion_matrix(y_test, y_pred).tolist()

print("Accuracy:", accuracy)
print(classification_report(y_test, y_pred))


# -----------------------------
# 9. Post-Training Validation
# -----------------------------
def _validate_model(pipeline, accuracy, y_pred_labels):
    """Run post-training checks on the fitted model.

    Validates that:
    - Learned class labels match ``EXPECTED_LABELS``.
    - Accuracy meets ``MIN_ACCURACY`` threshold.
    - All expected classes appear in predictions.

    Args:
        pipeline: Fitted sklearn Pipeline.
        accuracy: Accuracy score on the test set.
        y_pred_labels: Array of predicted labels from the test set.

    Raises:
        RuntimeError: If any validation check fails.
    """
    errors = []

    learned_labels = sorted(pipeline.classes_.tolist())
    expected_sorted = sorted(EXPECTED_LABELS)
    if learned_labels != expected_sorted:
        errors.append(
            f"Label mismatch: model learned {learned_labels}, expected {expected_sorted}"
        )

    if accuracy < MIN_ACCURACY:
        errors.append(
            f"Accuracy {accuracy:.4f} below minimum threshold {MIN_ACCURACY}"
        )

    unique_preds = set(y_pred_labels)
    missing = [label for label in EXPECTED_LABELS if label not in unique_preds]
    if missing:
        errors.append(f"Predictions missing expected classes: {missing}")

    if errors:
        raise RuntimeError("Model validation failed:\n" + "\n".join(errors))
    else:
        print("All post-training validation checks passed.")


_validate_model(pipeline, accuracy, y_pred)


# -----------------------------
# 10. Save Model
# -----------------------------
model_path = os.path.join(BASE_DIR, "model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(pipeline, f)

metadata = {
    "model_version": "1.1.0",
    "trained_at": datetime.now(timezone.utc).isoformat(),
    "features": ["income_lpa", "occupation", "bmi", "age_group", "lifestyle_risk", "city_tier"],
    "algorithm": "RandomForestClassifier",
    "accuracy": round(accuracy, 4),
    "classification_report": cr,
    "confusion_matrix": cm,
    "test_size": 0.2,
    "random_state": 42,
}

metadata_path = os.path.join(BASE_DIR, "model_metadata.json")
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)

print("Model saved successfully as model.pkl")
print(f"Metadata saved to {metadata_path}")