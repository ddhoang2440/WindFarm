import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.api.events_api import EventsApi
from datadog_api_client.v1.model.metrics_payload import MetricsPayload
from datadog_api_client.v1.model.point import Point
from datadog_api_client.v1.model.series import Series
from datadog_api_client.v1.model.event_create_request import EventCreateRequest
from starlette.concurrency import run_in_threadpool

# Load .env trước khi đọc biến môi trường — tránh fallback về datadoghq.com (US)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# 1. Khởi tạo Configuration cho Datadog
configuration = Configuration()
configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY", "")
configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY", "")
configuration.server_variables["site"] = os.getenv("DD_SITE", "datadoghq.com")

# Tên feature (đúng tên cột của model) -> tên metric trên Datadog
FEATURE_METRICS = {
    "wind_speed":              "wind_turbine.wind_speed",
    "power_output":            "wind_turbine.power_output",
    "ambient_temp":            "wind_turbine.ambient_temp",
    "status_type_id":          "wind_turbine.status_type_id",
    "wind_speed_roll_mean_6h": "wind_turbine.wind_speed_roll_mean_6h",
    "power_roll_std_6h":       "wind_turbine.power_roll_std_6h",
    "theoretical_power_index": "wind_turbine.theoretical_power_index",
}


def _send_metrics_sync(asset_id: int, features: dict, is_anomaly: bool,
                       anomaly_probability: float, inference_ms: float):
    """Gửi toàn bộ 7 feature + kết quả model + sức khoẻ ML Service lên Datadog."""
    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)
        tags = [f"asset_id:{asset_id}", "service:wind_turbine_ml"]
        now = int(datetime.now().timestamp())

        def gauge(metric: str, value: float) -> Series:
            return Series(metric=metric, type="gauge",
                          points=[Point([now, float(value)])], tags=tags)

        def count(metric: str, value: int) -> Series:
            # type=count + interval=1: dùng .as_count() trên Datadog để cộng đúng số lần
            return Series(metric=metric, type="count", interval=1,
                          points=[Point([now, float(value)])], tags=tags)

        # 7 feature đầu vào của model
        series = [gauge(metric, features[name]) for name, metric in FEATURE_METRICS.items()]

        # Kết quả của model
        series += [
            gauge("wind_turbine.is_anomaly", 1 if is_anomaly else 0),
            gauge("wind_turbine.anomaly_probability", anomaly_probability),
            count("wind_turbine.ml.anomaly_count", 1 if is_anomaly else 0),
        ]

        # Sức khoẻ của chính ML Service
        series += [
            gauge("wind_turbine.ml.inference_ms", inference_ms),
            count("wind_turbine.ml.predictions", 1),
        ]

        try:
            api_instance.submit_metrics(body=MetricsPayload(series=series))
            print(f"[DATADOG] Đã gửi {len(series)} metrics cho tuabin {asset_id}")
        except Exception as e:
            print(f"[DATADOG] Lỗi khi gửi metrics: {e}")


async def send_metrics_to_datadog(asset_id: int, features: dict, is_anomaly: bool,
                                  anomaly_probability: float, inference_ms: float):
    """Hàm async bọc run_in_threadpool cho send metrics"""
    await run_in_threadpool(_send_metrics_sync, asset_id, features, is_anomaly,
                            anomaly_probability, inference_ms)


def _send_alert_sync(asset_id: int, message: str):
    """Hàm đồng bộ gửi Event cảnh báo lên Datadog"""
    with ApiClient(configuration) as api_client:
        api_instance = EventsApi(api_client)

        body = EventCreateRequest(
            title=f"⚠️ Phát hiện bất thường tại Tuabin {asset_id}",
            text=message,
            alert_type="error",
            tags=[f"asset_id:{asset_id}", "service:wind_turbine_ml"]
        )

        try:
            api_instance.create_event(body=body)
            print(f"[DATADOG] Đã gửi alert cho tuabin {asset_id}")
        except Exception as e:
            print(f"[DATADOG] Lỗi khi gửi alert: {e}")


async def send_alert_to_datadog(asset_id: int, message: str):
    """Hàm async bọc run_in_threadpool cho send alert"""
    await run_in_threadpool(_send_alert_sync, asset_id, message)