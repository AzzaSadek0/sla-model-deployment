import joblib
import json
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# load model
model = joblib.load("slabreach_model.joblib")

# load model columns
with open("model_columns.json", "r") as f:
    model_columns = json.load(f)

app = FastAPI(title="SLA Breach Prediction API")

class InputData(BaseModel):
    data: dict

@app.post("/predict")
def predict(input_data: InputData):

    # convert input to DataFrame
    df = pd.DataFrame([input_data.data])

    # reindex so columns match model training
    df = df.reindex(columns=model_columns, fill_value=0)

    # prediction
    pred = model.predict(df)[0]

    return {"prediction": int(pred)}
