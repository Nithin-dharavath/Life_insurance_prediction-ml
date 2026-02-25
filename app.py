from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from schema.user_input import UserInput
from schema.prediction_validation import Output
from model.predict import predict_output, Model_version, model

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
        

@app.post("/predict", response_model = Output)
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
    except Exception as e:
        return JSONResponse(status_code=500, content=str(e))