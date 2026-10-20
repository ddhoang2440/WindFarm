from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import httpx
import joblib
import os
import time
# TODO: Import các hàm send_metrics_to_datadog và send_alert_to_datadog từ datadog_client

app = FastAPI(title="ML Service (Long)")

# TODO: Load model bằng joblib.load("wind_turbine_anomaly_model.joblib")

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
    # TODO: Tạo mảng features (7 phần tử theo đúng thứ tự) và chạy model.predict()
    # TODO: Gán kết quả vào biến is_anomaly (bool)
    
    is_anomaly = False # Tạm thời

    # TODO: Gọi hàm send_metrics_to_datadog(asset_id, wind_speed, power_output, is_anomaly)
    
    if is_anomaly:
        # TODO: Gọi hàm send_alert_to_datadog(asset_id, message)
        
        # TODO: Tạo payload Event (event_id, asset_id, event_label, event_start, event_end, event_description)
        # TODO: Dùng httpx gửi POST sang http://127.0.0.1:8000/api/v1/events
        # (Nhớ kèm Header Authorization: Bearer secret-token-123)
        pass

    return {"is_anomaly": is_anomaly}

@app.get("/health")
def health():
    return {"status": "ML Service OK"}