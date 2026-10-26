from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import joblib
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

    # Ngưỡng xác suất để coi là bất thường.
    # Model bị bias về lớp "normal" nên dùng predict_proba thay vì predict().
    # 0.15 bắt được các case bất thường rõ (p~0.15-0.25) mà không false-positive case normal (p~0.025).
    ANOMALY_THRESHOLD = 0.15

    # Chạy dự đoán bằng xác suất
    t_start = time.perf_counter()
    try:
        anomaly_probability = float(model.predict_proba(features)[0][1])
    except AttributeError:
        # Fallback nếu model không hỗ trợ predict_proba
        anomaly_probability = float(model.predict(features)[0])

    is_anomaly = anomaly_probability >= ANOMALY_THRESHOLD
    inference_ms = (time.perf_counter() - t_start) * 1000

    print(f"[ML SERVICE] Kết quả: {'BẤT THƯỜNG' if is_anomaly else 'BÌNH THƯỜNG'} "
          f"(p={anomaly_probability:.3f}, threshold={ANOMALY_THRESHOLD})")

    # Gửi metrics lên Datadog cho mọi request
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

    # Nếu bất thường -> chỉ gửi alert lên Datadog (backend tự tạo event)
    if is_anomaly:
        await send_alert_to_datadog(
            asset_id=data.asset_id,
            message=(
                f"Anomaly detected on turbine {data.asset_id}. "
                f"Wind: {data.wind_speed} m/s, Power: {data.power_output} kW, "
                f"Temp: {data.ambient_temp}°C"
            )
        )
        print("[ML SERVICE] -> Phát hiện bất thường, đã gửi alert Datadog.")

    return {"is_anomaly": is_anomaly, "anomaly_probability": round(anomaly_probability, 4)}

@app.get("/")
def root():
    return {"message": "ML Service is running"}

@app.get("/health")
def health():
    return {"status": "ML Service OK"}