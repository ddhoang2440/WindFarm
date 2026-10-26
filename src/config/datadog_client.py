"""
Datadog client cho Backend service.
Gửi metrics về: telemetry ingestion, ML call latency/errors, event creation, DB errors.
"""
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.model.metrics_payload import MetricsPayload
from datadog_api_client.v1.model.point import Point
from datadog_api_client.v1.model.series import Series
from starlette.concurrency import run_in_threadpool

load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

configuration = Configuration()
configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY", "")
configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY", "")
configuration.server_variables["site"] = os.getenv("DD_SITE", "datadoghq.com")

BASE_TAGS = ["service:wind_turbine_backend"]


def _asset_tags(asset_id: int) -> list[str]:
    return BASE_TAGS + [f"asset_id:{asset_id}"]


def _series(metric: str, value: float, tags: list[str],
            mtype: str = "gauge", interval: int | None = None) -> Series:
    now = int(datetime.now().timestamp())
    kwargs = dict(metric=metric, type=mtype, points=[Point([now, float(value)])], tags=tags)
    if interval is not None:
        kwargs["interval"] = interval
    return Series(**kwargs)


def _send_sync(series_list: list[Series]):
    with ApiClient(configuration) as api_client:
        api_instance = MetricsApi(api_client)
        try:
            api_instance.submit_metrics(body=MetricsPayload(series=series_list))
        except Exception as e:
            print(f"[DATADOG-BACKEND] Lỗi gửi metrics: {e}")


async def _send(series_list: list[Series]):
    await run_in_threadpool(_send_sync, series_list)


# ── Public API ────────────────────────────────────────────────────────────────

async def track_telemetry_received(asset_id: int, latency_ms: float):
    """Gọi sau khi lưu telemetry thành công vào DB."""
    tags = _asset_tags(asset_id)
    await _send([
        _series("wind_turbine.backend.telemetry_count", 1,
                tags, mtype="count", interval=1),
        _series("wind_turbine.backend.telemetry_latency_ms", latency_ms,
                tags, mtype="gauge"),
    ])


async def track_ml_call(asset_id: int, latency_ms: float, success: bool):
    """Gọi sau mỗi lần gọi ML Service (dù thành công hay thất bại)."""
    tags = _asset_tags(asset_id)
    await _send([
        _series("wind_turbine.backend.ml_call_latency_ms", latency_ms,
                tags, mtype="gauge"),
        _series("wind_turbine.backend.ml_call_count", 1,
                tags, mtype="count", interval=1),
        _series("wind_turbine.backend.ml_call_error_count",
                0 if success else 1, tags, mtype="count", interval=1),
    ])


async def track_event_created(asset_id: int):
    """Gọi sau khi backend tạo event anomaly thành công."""
    tags = _asset_tags(asset_id)
    await _send([
        _series("wind_turbine.backend.event_created_count", 1,
                tags, mtype="count", interval=1),
    ])


async def track_db_error(asset_id: int, operation: str):
    """Gọi khi có lỗi lưu DB (telemetry hoặc event)."""
    tags = _asset_tags(asset_id) + [f"operation:{operation}"]
    await _send([
        _series("wind_turbine.backend.db_error_count", 1,
                tags, mtype="count", interval=1),
    ])
