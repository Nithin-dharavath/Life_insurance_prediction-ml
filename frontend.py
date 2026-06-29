"""Streamlit frontend for the Insurance Premium Predictor.

Allows users to enter demographic and lifestyle data, sends the data to
the FastAPI backend, and displays the prediction along with derived
features and class probabilities.
"""

import json
import os
import streamlit as st
import requests

from features import compute_bmi, compute_age_group, compute_lifestyle_risk, compute_city_tier

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_URL = f"{API_BASE_URL}/predict"

CATEGORY_EXPLANATIONS = {
    "Low": "You are in a **low** premium bracket. Your risk profile suggests minimal insurance cost.",
    "Medium": "You are in a **moderate** premium bracket. Your risk profile indicates average insurance cost.",
    "High": "You are in a **high** premium bracket. Your risk profile suggests elevated insurance cost.",
}

st.title("Insurance Premium Category Predictor")
st.markdown("Enter your details below:")

age = st.number_input("Age", min_value=1, max_value=119, value=30)
weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0)
height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7)
income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0)
smoker = st.selectbox("Are you a smoker?", options=[True, False])
city = st.text_input("City", value="Mumbai")
occupation = st.selectbox(
    "Occupation",
    ['retired', 'freelancer', 'student', 'government_job',
     'business_owner', 'unemployed', 'private_job']
)

if st.button("Predict Premium Category"):

    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation,
    }

    bmi = compute_bmi(weight, height)
    age_group = compute_age_group(age)
    lifestyle_risk = compute_lifestyle_risk(smoker, bmi)
    city_tier = compute_city_tier(city)

    with st.spinner("Predicting..."):
        try:
            response = requests.post(API_URL, json=input_data, timeout=15)

            if response.status_code == 200:
                try:
                    result = response.json()
                except json.JSONDecodeError:
                    st.error("Received malformed response from server (invalid JSON).")
                    st.stop()

                response_data = result.get("Response")
                if response_data is None:
                    st.error("Unexpected response format from server.")
                    st.stop()

                prediction = response_data.get("predicted_category", "Not Found")
                confidence = response_data.get("confidence", 0)
                probabilities = response_data.get("class_probabilities", {})

                with st.container(border=True):
                    st.subheader("Derived Features (used by model)")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("BMI", f"{bmi:.1f}")
                    col2.metric("Age Group", age_group.replace("_", " ").title())
                    col3.metric("Lifestyle Risk", lifestyle_risk.title())
                    col4.metric("City Tier", str(city_tier))

                st.success(f"Predicted Insurance Premium Category: **{prediction}**")
                st.info(f"Confidence: {confidence:.2%}")

                explanation = CATEGORY_EXPLANATIONS.get(prediction)
                if explanation:
                    st.markdown(explanation)

                if probabilities:
                    st.subheader("Class Probabilities")
                    st.json(probabilities)

            else:
                try:
                    body = response.json()
                    msg = body.get("error", body.get("detail", response.text))
                except (json.JSONDecodeError, ValueError):
                    msg = response.text or f"HTTP {response.status_code}"
                st.error(f"Server error ({response.status_code}): {msg}")

        except requests.exceptions.Timeout:
            st.error("Request timed out. The server may be overloaded — please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the API server. Make sure it is running.")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")
