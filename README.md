# Life Insurance Premium Predictor

A machine learning service that predicts an insurance premium category (High / Medium / Low) based on user demographic and lifestyle inputs. The project uses a **FastAPI** backend serving a scikit-learn `RandomForestClassifier` pipeline, with a static HTML/CSS/JS frontend served by the same FastAPI process.

## Architecture

```
┌──────────┐  GET /ui ─────→ ┌──────────────────┐     ┌───────────────┐
│ Browser  │  static/*  ←──  │   FastAPI App    │ ──→ │  sklearn      │
│ (HTML/JS)│  POST /predict  │   (app.py)       │ ←── │  Pipeline     │
└──────────┘  ←── JSON resp  └──────────────────┘     │  (model.pkl)  │
                                                       └───────────────┘
```

### Data flow

1. Client sends `age, weight, height, income_lpa, occupation, smoker, city` to `POST /predict`
2. FastAPI validates the payload with Pydantic (`UserInput`), which automatically computes derived features: `bmi`, `age_group`, `lifestyle_risk`, `city_tier`
3. The validated features are passed to the model pipeline for prediction
4. Response includes the predicted category, confidence score, and per-class probabilities

### Derived features

| Feature | Computation |
|---|---|
| **bmi** | `weight / height²` |
| **age_group** | `<18 → young`, `<45 → adult`, `<65 → middle-aged`, else `senior` |
| **lifestyle_risk** | `smoker & bmi>30 → high`; `smoker or bmi>27 → medium`; else `low` |
| **city_tier** | Lookup in `tier_1_cities` / `tier_2_cities`; defaults to tier 3 |

## Project structure

```
.
├── app.py                 # FastAPI application (endpoints, middleware, static UI routes)
├── templates/             # Jinja2 HTML templates
├── static/                # CSS, JS, and assets served by FastAPI
├── model/
│   ├── train.py           # Training script (downloads CSV, fits pipeline)
│   ├── predict.py         # Model loading and inference
│   ├── model.pkl          # Trained sklearn pipeline (generated)
│   └── model_metadata.json# Training metrics and version info (generated)
├── schema/
│   ├── user_input.py      # Pydantic model for request validation
│   └── prediction_validation.py  # Pydantic model for response
├── features/
│   └── __init__.py        # Feature engineering functions (bmi, age_group, etc.)
├── city/
│   └── city_tier.py       # City tier classification lists
├── tests/                 # Test suite (pytest)
├── data/
│   └── insurance.csv      # Training dataset
├── pyproject.toml         # Project metadata and dependencies
├── requirements.txt       # Pinned dependencies
├── dockerfile             # Container build instructions
└── .github/workflows/ci.yml  # CI pipeline
```

## Setup

### Prerequisites

- Python 3.11+
- pip

### Local installation

```bash
# Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install with dev extras (for testing/lint)
pip install -e ".[dev]"
```

## Running

### Start the API server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Open the UI

Open `http://localhost:8000/ui` in your browser. The frontend is served directly by the FastAPI process — no separate server needed.

### Docker

```bash
docker build -t insurance-predict .
docker run -p 8000:8000 insurance-predict
```

## API Reference

### `GET /`

Health check endpoint.

**Response:**
```json
{"message": "insurance premium"}
```

---

### `GET /health`

Detailed health status including model version.

**Response:**
```json
{
  "status": "ok",
  "version": "1.1.0"
}
```

---

### `GET /metrics`

Operational counters.

**Response:**
```json
{
  "requests_total": 42,
  "predict_success_total": 40,
  "predict_failure_total": 2
}
```

---

### `POST /predict`

Predict the insurance premium category.

**Request body:**

| Field | Type | Constraints | Description |
|---|---|---|---|
| `age` | integer | 1–119 | Age of the user |
| `weight` | number | > 0 | Weight in kg |
| `height` | number | > 0 | Height in meters |
| `income_lpa` | number | > 0 | Annual income in lakhs per annum |
| `occupation` | string | One of: `retired`, `freelancer`, `student`, `government_job`, `business_owner`, `unemployed`, `private_job` | Employment type |
| `smoker` | boolean | — | Smoking status |
| `city` | string | Recognized Indian city | City name (case-insensitive, see `city/city_tier.py` for full list) |

**Example request:**
```json
{
  "age": 30,
  "weight": 70.0,
  "height": 1.75,
  "income_lpa": 10.0,
  "occupation": "private_job",
  "smoker": false,
  "city": "Mumbai"
}
```

**Response (200):**

| Field | Type | Description |
|---|---|---|
| `Response.predicted_category` | string | `"High"`, `"Medium"`, or `"Low"` |
| `Response.confidence` | number | Confidence score (0–1) |
| `Response.class_probabilities` | object | Per-class probabilities |

**Example response:**
```json
{
  "Response": {
    "predicted_category": "Low",
    "confidence": 0.85,
    "class_probabilities": {
      "High": 0.05,
      "Low": 0.85,
      "Medium": 0.10
    }
  }
}
```

**Error response (400 — validation error):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "city"],
      "msg": "Value error, Unsupported city: 'Unknown'. Must be one of the recognized cities."
    }
  ]
}
```

**Error response (500 — server error):**
```json
{
  "error": "Internal server error"
}
```

## Retraining the model

```bash
python model/train.py
```

This will:
1. Load training data from `data/insurance.csv` (falls back to remote URL if missing)
2. Engineer features (bmi, age_group, lifestyle_risk, city_tier)
3. Fit a `RandomForestClassifier` pipeline with one-hot encoding
4. Evaluate on a 20% test split
5. Run post-training validation (label alignment, accuracy threshold, class coverage)
6. Save `model/model.pkl` and `model/model_metadata.json`

Bump the version in `model/train.py` (`model_version` in the metadata dict) when retraining with significant changes.

## Testing

```bash
# Run all tests
pytest

# With coverage report
pytest --cov --cov-report=term-missing
```

## Linting

```bash
ruff check .
```

## CI

The project uses GitHub Actions (`.github/workflows/ci.yml`) to run lint, tests with coverage, and a Docker build on pushes to `main`.

## License

MIT
