import logging
import time
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from schema.user_input import UserInput
from model.predict import predict_output, Model_version

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_metrics_lock = Lock()
_metrics = {
    "requests_total": 0,
    "predict_success_total": 0,
    "predict_failure_total": 0,
}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency_ms = (time.time() - start) * 1000
    logger.info(
        "method=%s path=%s status=%d latency_ms=%.1f",
        request.method, request.url.path, response.status_code, latency_ms,
    )
    return response


@app.get("/")
def home():
    with _metrics_lock:
        _metrics["requests_total"] += 1
    return {"message": "insurance premium"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "version": Model_version,
    }


@app.get("/metrics")
def get_metrics():
    return _metrics


@app.post("/predict")
def predict_premium(data: UserInput):
    with _metrics_lock:
        _metrics["requests_total"] += 1

    user_input = {
        "bmi": data.bmi,
        "age_group": data.age_group,
        "lifestyle_risk": data.lifestyle_risk,
        "city_tier": data.city_tier,
        "income_lpa": data.income_lpa,
        "occupation": data.occupation,
    }

    try:
        prediction = predict_output(user_input)
        with _metrics_lock:
            _metrics["predict_success_total"] += 1
        logger.info(
            "income_lpa=%.1f occupation=%s city_tier=%s predicted=%s confidence=%.4f",
            data.income_lpa, data.occupation, data.city_tier,
            prediction["predicted_category"], prediction["confidence"],
        )
        return JSONResponse(status_code=200, content={"Response": prediction})
    except Exception:
        with _metrics_lock:
            _metrics["predict_failure_total"] += 1
        logger.exception("Prediction failed for input: %s", user_input)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )