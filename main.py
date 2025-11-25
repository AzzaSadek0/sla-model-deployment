import json
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------
# Load Model + Columns
# ---------------------------

model = joblib.load("sla_breach_model.joblib")

with open("model_columns.json", "r") as f:
    model_columns = json.load(f)

# ---------------------------
# FastAPI App
# ---------------------------

app = FastAPI(
    title="SLA Breach Prediction API",
    version="1.0.0",
    description="Predicts SLA Breach (0 = No Breach, 1 = Breach)",
)

# Allow everything (for JS tools / Railway)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Input Schema
# ---------------------------

class SLAInput(BaseModel):
    EVENT_NAME: float
    CRITICAL_EVENTS: float
    TOTAL_EVENTS: float
    pickup_delay: float
    dropoff_delay: float
    arrival_delay: float
    DELIVERY_DETAIL_ID: float
    DELIVERY_ID: float
    INVENTORY_ITEM_ID: float
    ORGANIZATION_ID: float
    SHIP_FROM_LOCATION_ID: float
    SHIP_TO_LOCATION_ID: float

# ---------------------------
# Prediction Endpoint
# ---------------------------

@app.post("/predict")
def predict_sla_breach(data: SLAInput):
    # Convert to dict
    data_dict = data.dict()

    # Arrange in correct model column order
    try:
        values = [data_dict[col] for col in model_columns]
    except KeyError as e:
        return {"error": f"Missing required field: {e}"}

    # Convert to numpy array
    final_input = np.array(values).reshape(1, -1)

    # Predict
    pred = model.predict(final_input)[0]

    return {
        "prediction": int(pred),
        "meaning": "Breach" if pred == 1 else "No Breach"
    }


@app.get("/")
def root():
    return {"message": "SLA Breach Prediction API is running."}
