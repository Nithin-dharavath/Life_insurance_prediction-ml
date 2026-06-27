import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from schema.user_input import UserInput
from model.predict import predict_output, Model_version

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.get("/")
def home():
    return {"message" : "insurance premium"}

#machine Readable
@app.get("/health")
def health_check():
    return {
        "status" : "ok",
        "version" : Model_version
    }


@app.post("/predict")
def predict_premium(data : UserInput):
    user_input = {
        "bmi" : data.bmi,
        "age_group" : data.age_group,
        "lifestyle_risk" : data.lifestyle_risk,
        "city_tier" : data.city_tier,
        "income_lpa" : data.income_lpa,
        "occupation" : data.occupation
    }

    try:
        prediction = predict_output(user_input)
        return JSONResponse(status_code=200, content={"Response" : prediction})
    except Exception:
        logger.exception("Prediction failed for input: %s", user_input)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"},
        )