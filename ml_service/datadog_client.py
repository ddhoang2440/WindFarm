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

def _send_metrics_sync(asset_id: int, wind_speed: float, power_output: float, is_anomaly: bool):
    """Hàm đồng bộ gửi metrics lên Datadog"""
    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)
        tags = [f"asset_id:{asset_id}", "service:wind_turbine_ml"]
        
        current_time = int(datetime.now().timestamp())

        series = [
            Series(
                metric="wind_turbine.wind_speed",
                type="gauge",
                points=[Point([current_time, wind_speed])],
                tags=tags
            ),
            Series(
                metric="wind_turbine.power_output",
                type="gauge",
                points=[Point([current_time, power_output])],
                tags=tags
            ),
            Series(
                metric="wind_turbine.is_anomaly",
                type="gauge",
                points=[Point([current_time, 1 if is_anomaly else 0])],
                tags=tags
            )
        ]
        
        body = MetricsPayload(series=series)
        try:
            api_instance.submit_metrics(body=body)
            print(f"[DATADOG] Đã gửi metrics cho tuabin {asset_id}")
        except Exception as e:
            print(f"[DATADOG] Lỗi khi gửi metrics: {e}")

async def send_metrics_to_datadog(asset_id: int, wind_speed: float, power_output: float, is_anomaly: bool):
    """Hàm async bọc run_in_threadpool cho send metrics"""
    await run_in_threadpool(_send_metrics_sync, asset_id, wind_speed, power_output, is_anomaly)


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