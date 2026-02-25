import pandas as pd
import numpy as np
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, accuracy_score


# -----------------------------
# 1. Load Dataset
# -----------------------------
df = pd.read_csv("https://raw.githubusercontent.com/campusx-official/fastapi-demo-api/refs/heads/main/insurance.csv")

# -----------------------------
# 2. Feature Engineering
# -----------------------------
df["bmi"] = df["weight"] / (df["height"] ** 2)

def age_group(age):
    if age < 18:
        return "young"
    elif age < 45:
        return "adult"
    elif age < 65:
        return "middle-aged"
    return "senior"

df["age_group"] = df["age"].apply(age_group)


def lifestyle_risk(row):
    if row["smoker"] and row["bmi"] > 30:
        return "high"
    elif row["smoker"] or row["bmi"] > 27:
        return "medium"
    else:
        return "low"
    
df["lifestyle_risk"] = df.apply(lifestyle_risk, axis=1)


tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]

def city_tier(city):
    if city in tier_1_cities:
        return 1
    elif city in tier_2_cities:
        return 2
    else:
        return 3
     
df["city_tier"] = df["city"].apply(city_tier)
     
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


print("Model saved successfully as model.pkl")