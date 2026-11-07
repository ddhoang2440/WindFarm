import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import joblib
import time
from dotenv import load_dotenv
from pathlib import Path

# Load .env from root project directory
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

from datadog_client import send_metrics_to_datadog, send_alert_to_datadog

app = FastAPI(title="ML Service")

# 1. Load model
model = joblib.load("wind_turbine_anomaly_model.joblib") 
print("[ML SERVICE] Ready to receive requests")

# 2. Telemetry data schema (7 features)
class TelemetryData(BaseModel):
    asset_id: int
    time_stamp: datetime
    wind_speed: float
    power_output: float
    ambient_temp: float
    status_type_id: int
    wind_speed_roll_mean_6h: float
    power_roll_std_6h: float
    theoretical_power_index: float

# 3. Main prediction endpoint
@app.post("/predict")
async def predict(data: TelemetryData):
    print(f"[ML SERVICE] Received telemetry for turbine {data.asset_id}")

    import pandas as pd
    features = pd.DataFrame([{
        "wind_speed": data.wind_speed,
        "power_output": data.power_output,
        "ambient_temp": data.ambient_temp,
        "status_type_id": data.status_type_id,
        "wind_speed_roll_mean_6h": data.wind_speed_roll_mean_6h,
        "power_roll_std_6h": data.power_roll_std_6h,
        "theoretical_power_index": data.theoretical_power_index,
    }])

    ANOMALY_THRESHOLD = 0.25

    t_start = time.perf_counter()
    try:
        anomaly_probability = float(model.predict_proba(features)[0][1])
    except AttributeError:
        anomaly_probability = float(model.predict(features)[0])

    is_anomaly = anomaly_probability >= ANOMALY_THRESHOLD
    inference_ms = (time.perf_counter() - t_start) * 1000

    print(f"[ML SERVICE] Prediction result: {'ANOMALY' if is_anomaly else 'NORMAL'} "
          f"(p={anomaly_probability:.3f}, threshold={ANOMALY_THRESHOLD})")

    # Send metrics to Datadog
    features_dict = {
        "wind_speed": data.wind_speed,
        "power_output": data.power_output,
        "ambient_temp": data.ambient_temp,
        "status_type_id": data.status_type_id,
        "wind_speed_roll_mean_6h": data.wind_speed_roll_mean_6h,
        "power_roll_std_6h": data.power_roll_std_6h,
        "theoretical_power_index": data.theoretical_power_index,
    }
    await send_metrics_to_datadog(
        asset_id=data.asset_id,
        features=features_dict,
        is_anomaly=is_anomaly,
        anomaly_probability=anomaly_probability,
        inference_ms=inference_ms,
    )

    # If anomaly, send Datadog alert
    if is_anomaly:
        await send_alert_to_datadog(
            asset_id=data.asset_id,
            message=(
                f"Anomaly detected on turbine {data.asset_id}. "
                f"Wind: {data.wind_speed} m/s, Power: {data.power_output} kW, "
                f"Temp: {data.ambient_temp} C"
            )
        )
        print(f"[ML SERVICE] -> Anomaly detected on turbine {data.asset_id}, Datadog alert sent.")

    return {"is_anomaly": is_anomaly, "anomaly_probability": round(anomaly_probability, 4)}

@app.get("/")
def root():
    return {"message": "ML Service is running"}

@app.get("/health")
def health():
    return {"status": "ML Service OK"}
