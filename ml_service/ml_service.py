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

# Load .env từ thư mục gốc project (một cấp trên ml_service/)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Import các hàm từ datadog_client
from datadog_client import send_metrics_to_datadog, send_alert_to_datadog

app = FastAPI(title="ML Service (Long)")

# Ngưỡng xác suất để coi là bất thường (khớp với model.predict() của RandomForest 2 lớp)
ANOMALY_THRESHOLD = 0.5

# 1. Load model
try:
    model = joblib.load(Path(__file__).parent / "wind_turbine_anomaly_model.joblib")
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
    if model is None:
        return JSONResponse(status_code=503, content={"error": "Model chưa được load"})

    print(f"[ML SERVICE] Nhận dữ liệu tuabin {data.asset_id}")

    # 3. Tạo mảng features (đúng thứ tự lúc train model)
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

    # 4. Chạy dự đoán AI + đo thời gian suy luận
    t0 = time.perf_counter()
    anomaly_probability = float(model.predict_proba(row)[0][1])   # xác suất lớp 1 (bất thường)
    inference_ms = (time.perf_counter() - t0) * 1000
    is_anomaly = anomaly_probability > ANOMALY_THRESHOLD
    print(f"[ML SERVICE] Kết quả: {'BẤT THƯỜNG' if is_anomaly else 'BÌNH THƯỜNG'} "
          f"(p={anomaly_probability:.2f}, {inference_ms:.1f} ms)")

    # 5. Gửi metrics lên Datadog (Luôn gửi để làm dashboard)
    await send_metrics_to_datadog(
        asset_id=data.asset_id,
        features=features,
        is_anomaly=is_anomaly,
        anomaly_probability=anomaly_probability,
        inference_ms=inference_ms,
    )

    # 6. Xử lý khi phát hiện bất thường
    if is_anomaly:
        alert_message = (
            f"ML phát hiện bất thường (xác suất {anomaly_probability:.0%}). "
            f"Gió: {data.wind_speed} m/s, Công suất: {data.power_output} kW, "
            f"Nhiệt độ: {data.ambient_temp}°C, "
            f"Độ dao động công suất 6h: {data.power_roll_std_6h:.2f}"
        )

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
                        "ngrok-skip-browser-warning": "true",
                        "User-Agent": "ML-Service/1.0"
                    },
                    timeout=15.0
                )
                print(f"[ML SERVICE] Đã báo Event cho Backend. Status: {response.status_code}")
            except httpx.TimeoutException:
                print("[ML SERVICE] LỖI: Quá thời gian kết nối tới Backend (Timeout).")
            except httpx.ConnectError:
                print("[ML SERVICE] LỖI: Không thể kết nối tới Backend. Kiểm tra lại link Ngrok.")
            except Exception as e:
                print(f"[ML SERVICE] Lỗi khác khi gọi Backend API: {type(e).__name__} - {e}")

    return {"is_anomaly": is_anomaly, "anomaly_probability": round(anomaly_probability, 4)}

@app.get("/")
def root():
    return {"message": "ML Service is running"}

@app.get("/health")
def health():
    return {"status": "ML Service OK"}