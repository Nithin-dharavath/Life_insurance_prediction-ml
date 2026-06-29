# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A machine learning project that predicts an **insurance premium category** for a user. It exposes a FastAPI backend that serves a pickled scikit-learn pipeline and a static HTML/CSS/JS frontend (served by the same FastAPI process). The model is a `RandomForestClassifier` wrapped in a `ColumnTransformer` + `OneHotEncoder` preprocessing pipeline.

## Architecture

```
app.py                 # FastAPI app: /, /health, /predict (POST), /ui (static UI)
templates/index.html   # Glassmorphism HTML page (served at /ui)
static/                # CSS, JS, assets (served at /static/)
model/
  train.py             # One-shot training script: downloads CSV, engineers features,
                       # fits pipeline, evaluates, pickles to model.pkl
  predict.py           # Loads model.pkl, exposes `model`, `Model_version`,
                       # and `predict_output(user_input: dict)`
  model.pkl            # Trained sklearn Pipeline (regenerate via train.py)
schema/
  user_input.py        # Pydantic `UserInput` model with @computed_field features
                       # (bmi, lifestyle_risk, age_group, city_tier) derived from raw input
  prediction_validation.py  # Pydantic `Output` model for the API response
city/
  city_tier.py         # Lists `tier_1_cities` and `tier_2_cities` (used by both
                       # schema/user_input.py and model/train.py — keep them in sync)
dockerfile             # Container image: python:3.11-slim → uvicorn app:app on :8000
requirements.txt       # Pinned deps (FastAPI, scikit-learn, pydantic, …)
```

### Data flow (request lifecycle)

1. Browser (or curl) sends `age, weight, height, income_lpa, occupation, smoker, city` to `POST /predict`.
2. `app.py` validates the payload against `UserInput` (Pydantic). The model automatically computes `bmi`, `age_group`, `lifestyle_risk`, `city_tier` and exposes them on the validated object.
3. `app.py` extracts those derived fields into a dict and calls `predict_output(user_input)` in `model/predict.py`.
4. `predict_output` builds a one-row DataFrame, runs `model.predict` and `model.predict_proba`, and returns `{predicted_category, confidence, class_probabilities}`.
5. `app.py` wraps that in `JSONResponse` and returns it. (Note: `response_model=Output` is declared but the response is a dict containing `Response` key — clients should read `result["Response"]["predicted_category"]`.)

### Feature engineering (must match between training and serving)

These transforms are duplicated in two places and must stay consistent:

- `bmi = weight / height^2`
- `age_group`: `<18 young`, `<45 adult`, `<65 middle-aged`, else `senior`
- `lifestyle_risk`: `smoker & bmi>30 → high`; `smoker & bmi>27 → medium`; else `low`
  - Note: `train.py` uses `smoker or bmi>27` for medium, but `schema/user_input.py` uses `smoker and bmi>27`. This is an existing inconsistency — be aware of it when retraining.
- `city_tier`: 1/2/3 by membership in `tier_1_cities` / `tier_2_cities`

The final training feature order (set in `train.py` line 67) is:
`income_lpa, occupation, bmi, age_group, lifestyle_risk, city_tier` → target `insurance_premium_category`.

## Commands

### Local development (Windows / Git Bash)

```bash
# Activate the existing venv (already created at ./venv)
source venv/Scripts/activate

# Install / refresh deps
pip install -r requirements.txt

# Run the FastAPI backend (hot reload for development)
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Open the UI in your browser
# Frontend is served at http://localhost:8000/ui
```

### Docker

```bash
docker build -t insurance-predict .
docker run -p 8000:8000 insurance-predict
```

### Retrain the model

```bash
python model/train.py
# Reads CSV from a remote URL, fits the pipeline, prints classification_report,
# and overwrites model/model.pkl. Bump Model_version in model/predict.py
# if you change features or model hyperparameters.
```

### Useful endpoints once running

- `GET  /`         → `{"message": "insurance premium"}`
- `GET  /health`   → `{"status": "ok", "version": "<Model_version>"}`
- `POST /predict`  → see schema above; OpenAPI docs auto-generated at `/docs`

## Known gotchas

- `requirements.txt` is encoded in a way that renders as mojibake in some viewers but pip parses it correctly — don't re-encode it.
- `.gitignore` excludes `__pycache__/`, `venv/`. `model/model.pkl` and `__pycache__` directories are checked in despite being generated.
