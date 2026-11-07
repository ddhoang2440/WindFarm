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

# Import các hàm từ datadog_client
from datadog_client import send_metrics_to_datadog, send_alert_to_datadog

app = FastAPI(title="ML Service (Long)")

# 1. Load model
try:
    model = joblib.load("wind_turbine_anomaly_model.joblib")
    print("[ML SERVICE] Load model thành công.")
except Exception as e:
    print(f"[ML SERVICE] LỖI LOAD MODEL: {e}")
    model = None

# In ra URL Backend để kiểm tra xem .env đã nạp đúng chưa
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
print(f"[ML SERVICE] Sẽ gửi Event bất thường tới Backend: {BACKEND_URL}")

# 2. Khai báo Schema dữ liệu (7 features)
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
    if not model:
        return {"error": "Model chưa được load"}, 500

    print(f"[ML SERVICE] Nhận dữ liệu tuabin {data.asset_id}")

    # 3. Tạo mảng features
    features = [[
        data.wind_speed, 
        data.power_output, 
        data.ambient_temp, 
        data.status_type_id,
        data.wind_speed_roll_mean_6h,
        data.power_roll_std_6h,
        data.theoretical_power_index
    ]]
    
    # 4. Chạy dự đoán AI
    is_anomaly = bool(model.predict(features)[0] == 1)
    print(f"[ML SERVICE] Kết quả: {'BẤT THƯỜNG' if is_anomaly else 'BÌNH THƯỜNG'}")

    # 5. Gửi metrics lên Datadog (Luôn gửi để làm dashboard)
    await send_metrics_to_datadog(
        asset_id=data.asset_id, 
        wind_speed=data.wind_speed, 
        power_output=data.power_output, 
        is_anomaly=is_anomaly
    )
    
    # 6. Xử lý khi phát hiện bất thường
    if is_anomaly:
        alert_message = f"ML phát hiện bất thường. Gió: {data.wind_speed} m/s, Công suất: {data.power_output} kW"
        
        # Gửi Alert lên Datadog
        await send_alert_to_datadog(data.asset_id, alert_message)
        
        # Tạo payload Event báo ngược về Backend của Hoàng
        event_payload = {
            "event_id": int(time.time()), 
            "asset_id": data.asset_id,
            "event_label": "anomaly",
            "event_start": data.time_stamp.isoformat(),
            "event_end": datetime.now().isoformat(),
            "event_description": alert_message
        }

        api_token = os.getenv("API_TOKEN", "")

        # Gửi POST sang API của Hoàng qua Ngrok
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{BACKEND_URL}/api/v1/events",
                    json=event_payload,
                    headers={
                        "Authorization": f"Bearer {api_token}",
                        "ngrok-skip-browser-warning": "true",  # Vượt qua trang cảnh báo của Ngrok
                        "User-Agent": "ML-Service/1.0"         # Giả lập User-Agent
                    },
                    timeout=15.0 # Tăng timeout lên 15s để đợi Ngrok phản hồi
                )
                print(f"[ML SERVICE] Đã báo Event cho Backend. Status: {response.status_code}")
            except httpx.TimeoutException:
                print("[ML SERVICE] LỖI: Quá thời gian kết nối tới Backend (Timeout).")
            except httpx.ConnectError:
                print("[ML SERVICE] LỖI: Không thể kết nối tới Backend. Kiểm tra lại link Ngrok.")
            except Exception as e:
                print(f"[ML SERVICE] Lỗi khác khi gọi Backend API: {type(e).__name__} - {e}")

    return {"is_anomaly": is_anomaly}

@app.get("/")
def root():
    return {"message": "ML Service is running"}

@app.get("/health")
def health():
    return {"status": "ML Service OK"}