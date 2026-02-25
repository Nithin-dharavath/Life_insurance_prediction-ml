import os
import pickle
import pandas as pd
from schema.user_input import UserInput

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "model.pkl")

with open(model_path, "rb") as f:
    model = pickle.load(f)

Model_version = "1.0.0"

class_labels = model.classes_.tolist()

def predict_output(user_input : dict):
    df = pd.DataFrame([user_input])
    predicted_class = model.predict(df)[0]

    probabilities = model.predict_proba(df)[0]
    confience = max(probabilities)
    class_probas = dict(zip(class_labels, map(lambda p: round(p,4), probabilities)))

    return {
        "predicted_category" : predicted_class,
        "confiendence" : round(confience, 4),
        "class_probabilities" : class_probas
    }