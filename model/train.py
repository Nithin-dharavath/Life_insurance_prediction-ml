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
from sklearn.metrics import classification_report, accuracy_score

from features import compute_bmi, compute_age_group, compute_lifestyle_risk, compute_city_tier


# -----------------------------
# 1. Load Dataset
# -----------------------------
df = pd.read_csv("https://raw.githubusercontent.com/campusx-official/fastapi-demo-api/refs/heads/main/insurance.csv")

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

print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))


# -----------------------------
# 9. Save Model
# -----------------------------
with open("model.pkl", "wb") as f:
    pickle.dump(pipeline, f)

metadata = {
    "model_version": "1.1.0",
    "trained_at": datetime.now(timezone.utc).isoformat(),
    "features": ["income_lpa", "occupation", "bmi", "age_group", "lifestyle_risk", "city_tier"],
    "algorithm": "RandomForestClassifier",
}

metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_metadata.json")
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)

print("Model saved successfully as model.pkl")
print(f"Metadata saved to {metadata_path}")