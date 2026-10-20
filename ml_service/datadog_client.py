import os
from datetime import datetime
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi
from datadog_api_client.v1.api.events_api import EventsApi
from datadog_api_client.v1.model.metrics_payload import MetricsPayload
from datadog_api_client.v1.model.point import Point
from datadog_api_client.v1.model.series import Series
from datadog_api_client.v1.model.event_create_request import EventCreateRequest
from starlette.concurrency import run_in_threadpool

# TODO: Khởi tạo Configuration cho Datadog
# - Đọc DD_API_KEY, DD_APP_KEY, DD_SITE từ file .env
# - Gán vào configuration.api_key và configuration.server_variables

# TODO: Viết hàm _send_metrics_sync để gửi wind_speed, power_output, is_anomaly
# TODO: Viết hàm async send_metrics_to_datadog (bọc run_in_threadpool)

# TODO: Viết hàm _send_alert_sync để gửi Event cảnh báo (alert_type="error")
# TODO: Viết hàm async send_alert_to_datadog (bọc run_in_threadpool)