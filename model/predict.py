import json
import os
import pickle
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "model.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

_metadata_path = os.path.join(BASE_DIR, "model_metadata.json")
if os.path.exists(_metadata_path):
    with open(_metadata_path) as _f:
        _metadata = json.load(_f)
    Model_version = _metadata.get("model_version", "unknown")
else:
    Model_version = "unknown"

class_labels = model.classes_.tolist()

EXPECTED_LABELS = ["High", "Low", "Medium"]
_sorted_learned = sorted(class_labels)
_sorted_expected = sorted(EXPECTED_LABELS)
if _sorted_learned != _sorted_expected:
    raise RuntimeError(
        f"Model labels {_sorted_learned} do not match expected labels {_sorted_expected}. "
        "Retrain the model or update EXPECTED_LABELS."
    )

def predict_output(user_input : dict):
    df = pd.DataFrame([user_input])
    predicted_class = model.predict(df)[0]

    probabilities = model.predict_proba(df)[0]
    confidence = max(probabilities)
    class_probas = dict(zip(class_labels, map(lambda p: round(p,4), probabilities)))

    return {
        "predicted_category" : predicted_class,
        "confidence" : round(confidence, 4),
        "class_probabilities" : class_probas
    }