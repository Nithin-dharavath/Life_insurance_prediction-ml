# Life Insurance Premium Predictor

A FastAPI service that predicts an insurance premium category (**High / Medium / Low**) from user demographic and lifestyle data, served via a scikit-learn `RandomForestClassifier` pipeline and a static HTML/CSS/JS frontend.

## Architecture

```
Browser ──HTTP──▶ FastAPI (app.py) ──▶ sklearn Pipeline (model.pkl)
                       │
                       └──▶ /static  +  /ui  (served by the same process)
```

## Project Structure

```
app.py                 # FastAPI application
templates/             # HTML templates (Jinja2)
static/                # CSS, JS, assets
model/
  train.py             # Training script (regenerates model.pkl)
  predict.py           # Model loading and inference
  model.pkl            # Trained pipeline (generated)
schema/                # Pydantic request / response models
city/                  # Tier 1 / Tier 2 city lists
features/              # Derived feature computations
dockerfile
requirements.txt
```

## Setup

```bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

- API: <http://localhost:8000>
- UI: <http://localhost:8000/ui>
- OpenAPI docs: <http://localhost:8000/docs>

### Docker

```bash
docker build -t insurance-predict .
docker run -p 8000:8000 insurance-predict
```

## API

| Method | Path       | Description                          |
| ------ | ---------- | ------------------------------------ |
| GET    | `/`        | Service greeting                     |
| GET    | `/health`  | Status and model version             |
| GET    | `/metrics` | Operational counters                 |
| POST   | `/predict` | Predict premium category             |

### `POST /predict`

**Request:**

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

**Response:**

```json
{
  "Response": {
    "predicted_category": "Low",
    "confidence": 0.85,
    "class_probabilities": { "High": 0.05, "Low": 0.85, "Medium": 0.10 }
  }
}
```

Derived features (`bmi`, `age_group`, `lifestyle_risk`, `city_tier`) are computed automatically from the raw input via Pydantic.

## Retrain

```bash
python model/train.py
```

Regenerates `model/model.pkl` and `model/model_metadata.json`. Bump `model_version` in the training script when changing features or hyperparameters.

## Tests & Lint

```bash
pytest --cov
ruff check .
```

## License

MIT