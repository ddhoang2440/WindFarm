from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import httpx
import joblib
import os
import time
from dotenv import load_dotenv
from pathlib import Path

# Load .env from root project directory
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Import helpers from datadog_client
from datadog_client import send_metrics_to_datadog, send_alert_to_datadog

app = FastAPI(title="ML Service")

# Probability threshold to classify anomaly
ANOMALY_THRESHOLD = 0.5

# 1. Load model
try:
    model = joblib.load(Path(__file__).parent / "wind_turbine_anomaly_model.joblib")
    print("[ML SERVICE] Model loaded successfully.")
except Exception as e:
    print(f"[ML SERVICE] ERROR LOADING MODEL: {e}")
    model = None

# Print Backend URL for verification
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
print(f"[ML SERVICE] Anomaly events will be sent to Backend: {BACKEND_URL}")

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

@app.post("/predict")
async def predict(data: TelemetryData):
    if model is None:
        return JSONResponse(status_code=503, content={"error": "Model is not loaded"})

    print(f"[ML SERVICE] Received telemetry for turbine {data.asset_id}")

    # 3. Create feature mapping in training order
    features = {
        "wind_speed": data.wind_speed,
        "power_output": data.power_output,
        "ambient_temp": data.ambient_temp,
        "status_type_id": data.status_type_id,
        "wind_speed_roll_mean_6h": data.wind_speed_roll_mean_6h,
        "power_roll_std_6h": data.power_roll_std_6h,
        "theoretical_power_index": data.theoretical_power_index,
    }
    row = [[
        features["wind_speed"],
        features["power_output"],
        features["ambient_temp"],
        features["status_type_id"],
        features["wind_speed_roll_mean_6h"],
        features["power_roll_std_6h"],
        features["theoretical_power_index"],
    ]]

    # 4. Run AI prediction & measure inference latency
    t0 = time.perf_counter()
    anomaly_probability = float(model.predict_proba(row)[0][1])
    inference_ms = (time.perf_counter() - t0) * 1000
    is_anomaly = anomaly_probability > ANOMALY_THRESHOLD
    print(f"[ML SERVICE] Prediction result: {'ANOMALY' if is_anomaly else 'NORMAL'} "
          f"(p={anomaly_probability:.2f}, {inference_ms:.1f} ms)")

    # 5. Send metrics to Datadog
    await send_metrics_to_datadog(
        asset_id=data.asset_id,
        features=features,
        is_anomaly=is_anomaly,
        anomaly_probability=anomaly_probability,
        inference_ms=inference_ms,
    )

    # 6. Handle detected anomalies
    if is_anomaly:
        alert_message = (
            f"ML detected anomaly (probability {anomaly_probability:.0%}). "
            f"Wind: {data.wind_speed} m/s, Power: {data.power_output} kW, "
            f"Temp: {data.ambient_temp} C, "
            f"Power Roll Std 6h: {data.power_roll_std_6h:.2f}"
        )

        # Send alert to Datadog
        await send_alert_to_datadog(data.asset_id, alert_message)

        # Create event payload to notify Backend
        event_payload = {
            "event_id": int(time.time()),
            "asset_id": data.asset_id,
            "event_label": "anomaly",
            "event_start": data.time_stamp.isoformat(),
            "event_end": datetime.now().isoformat(),
            "event_description": alert_message
        }

        api_token = os.getenv("API_TOKEN", "")

        # Post event to Backend
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{BACKEND_URL}/api/v1/events",
                    json=event_payload,
                    headers={
                        "Authorization": f"Bearer {api_token}",
                        "ngrok-skip-browser-warning": "true",
                        "User-Agent": "ML-Service/1.0"
                    },
                    timeout=15.0
                )
                print(f"[ML SERVICE] Reported Event to Backend. Status: {response.status_code}")
            except httpx.TimeoutException:
                print("[ML SERVICE] ERROR: Connection timeout to Backend.")
            except httpx.ConnectError:
                print("[ML SERVICE] ERROR: Cannot connect to Backend. Please verify Backend URL.")
            except Exception as e:
                print(f"[ML SERVICE] Error calling Backend API: {type(e).__name__} - {e}")

    return {"is_anomaly": is_anomaly, "anomaly_probability": round(anomaly_probability, 4)}

@app.get("/")
def root():
    return {"message": "ML Service is running"}

@app.get("/health")
def health():
    return {"status": "ML Service OK"}
