from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import httpx
import joblib
import os
import time
from dotenv import load_dotenv
from pathlib import Path

# Load .env từ thư mục gốc project (một cấp trên ml_service/)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

from datadog_client import send_metrics_to_datadog, send_alert_to_datadog

app = FastAPI(title="ML Service (Long)")

# ==========================================
# 1. LOAD MODEL (BỎ COMMENT ĐỂ CHẠY THẬT)
# ==========================================
# YÊU CẦU: Đảm bảo file .joblib nằm cùng thư mục với file main.py này.
# YÊU CẦU: Cài đúng phiên bản scikit-learn (1.6.1) để không bị lỗi load.
model = joblib.load("wind_turbine_anomaly_model.joblib") 
print("[ML SERVICE] Sẵn sàng nhận request")

# ==========================================
# 2. KHUÔN DỮ LIỆU NHẬN TỪ HOÀNG
# (ĐÃ SỬA: Nhận đủ 7 features thay vì 4)
# ==========================================
class TelemetryData(BaseModel):
    asset_id: int
    time_stamp: datetime
    wind_speed: float
    power_output: float
    ambient_temp: float
    status_type_id: int
    # 3 features phái sinh mà Hoàng sẽ tính và gửi sang:
    wind_speed_roll_mean_6h: float
    power_roll_std_6h: float
    theoretical_power_index: float

# ==========================================
# 3. API CHÍNH: NHẬN DỮ LIỆU & DỰ ĐOÁN
# ==========================================
@app.post("/predict")
async def predict(data: TelemetryData):
    print(f"[ML SERVICE] Nhận dữ liệu tuabin {data.asset_id}")

    # TODO 1: CHẠY MODEL AI THẬT
    # YÊU CẦU: Truyền đúng 7 features theo đúng thứ tự lúc train model.
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

    # Chạy dự đoán (1 là bất thường, 0 là bình thường)
    is_anomaly = bool(model.predict(features)[0] == 1)
    
    print(f"[ML SERVICE] Kết quả dự đoán: {'BẤT THƯỜNG' if is_anomaly else 'BÌNH THƯỜNG'}")

    # Gửi metrics lên Datadog cho mọi request
    await send_metrics_to_datadog(
        asset_id=data.asset_id,
        wind_speed=data.wind_speed,
        power_output=data.power_output,
        is_anomaly=is_anomaly
    )

    # Nếu bất thường -> gửi alert lên Datadog + gọi API backend
    if is_anomaly:
        await send_alert_to_datadog(
            asset_id=data.asset_id,
            message=(
                f"Anomaly detected on turbine {data.asset_id}. "
                f"Wind: {data.wind_speed} m/s, Power: {data.power_output} kW, "
                f"Temp: {data.ambient_temp}°C"
            )
        )
        print("[ML SERVICE] -> Phát hiện bất thường, gọi API /events của Hoàng...")
        
        # ĐÃ SỬA: Tự sinh event_id theo timestamp thay vì fix cứng 999
        # ĐÃ SỬA: event_end là thời điểm hiện tại
        event_payload = {
            "event_id": int(time.time()), 
            "asset_id": data.asset_id,
            "event_label": "anomaly",
            "event_start": data.time_stamp.isoformat(),
            "event_end": datetime.now().isoformat(),
            "event_description": f"ML phát hiện bất thường. Gió: {data.wind_speed} m/s"
        }

        backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
        api_token = os.getenv("API_TOKEN", "")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{backend_url}/api/v1/events",
                    json=event_payload,
                    headers={
                        "Authorization": f"Bearer {api_token}",
                        "ngrok-skip-browser-warning": "true"
                    },
                    timeout=5.0
                )
                print(f"[ML SERVICE] Đã báo Event. Status: {response.status_code}")
            except Exception as e:
                print(f"[ML SERVICE] Lỗi khi gọi Backend: {e}")

    return {"is_anomaly": is_anomaly}

@app.get("/")
def root():
    return {"message": "ML Service is running"}

@app.get("/health")
def health():
    return {"status": "ML Service OK"}