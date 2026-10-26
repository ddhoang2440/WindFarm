"""
Tự động tạo Dashboard và Monitors trên Datadog qua API.
Đặt file này ở THƯ MỤC GỐC project (cùng chỗ với .env), rồi chạy:

    python setup_datadog.py

.env cần có:
    DD_API_KEY=...
    DD_APP_KEY=...
    DD_SITE=ap1.datadoghq.com
    DD_ALERT_EMAIL=ban@gmail.com  # email nhận cảnh báo từ monitor (tuỳ chọn)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.api.monitors_api import MonitorsApi

# Dashboard models
from datadog_api_client.v1.model.dashboard import Dashboard
from datadog_api_client.v1.model.dashboard_layout_type import DashboardLayoutType
from datadog_api_client.v1.model.widget import Widget
from datadog_api_client.v1.model.widget_layout import WidgetLayout
from datadog_api_client.v1.model.widget_time import WidgetTime
from datadog_api_client.v1.model.widget_live_span import WidgetLiveSpan

# Timeseries widget
from datadog_api_client.v1.model.timeseries_widget_definition import TimeseriesWidgetDefinition
from datadog_api_client.v1.model.timeseries_widget_definition_type import TimeseriesWidgetDefinitionType
from datadog_api_client.v1.model.timeseries_widget_request import TimeseriesWidgetRequest
from datadog_api_client.v1.model.timeseries_request_style import TimeseriesRequestStyle
from datadog_api_client.v1.model.widget_display_type import WidgetDisplayType
from datadog_api_client.v1.model.widget_line_type import WidgetLineType
from datadog_api_client.v1.model.widget_line_width import WidgetLineWidth

# Query value widget
from datadog_api_client.v1.model.query_value_widget_definition import QueryValueWidgetDefinition
from datadog_api_client.v1.model.query_value_widget_definition_type import QueryValueWidgetDefinitionType
from datadog_api_client.v1.model.query_value_widget_request import QueryValueWidgetRequest
from datadog_api_client.v1.model.formula_and_function_metric_aggregation import FormulaAndFunctionMetricAggregation
from datadog_api_client.v1.model.widget_text_align import WidgetTextAlign

# Event stream widget
from datadog_api_client.v1.model.event_stream_widget_definition import EventStreamWidgetDefinition
from datadog_api_client.v1.model.event_stream_widget_definition_type import EventStreamWidgetDefinitionType
from datadog_api_client.v1.model.widget_event_size import WidgetEventSize

# Metric query
from datadog_api_client.v1.model.formula_and_function_metric_query_definition import FormulaAndFunctionMetricQueryDefinition
from datadog_api_client.v1.model.formula_and_function_metric_data_source import FormulaAndFunctionMetricDataSource
from datadog_api_client.v1.model.formula_and_function_response_format import FormulaAndFunctionResponseFormat

# Monitor models
from datadog_api_client.v1.model.monitor import Monitor
from datadog_api_client.v1.model.monitor_type import MonitorType
from datadog_api_client.v1.model.monitor_options import MonitorOptions
from datadog_api_client.v1.model.monitor_thresholds import MonitorThresholds

# ── Configuration ──────────────────────────────────────────────────────────────
SITE          = os.getenv("DD_SITE", "datadoghq.com")
ALERT_EMAIL   = os.getenv("DD_ALERT_EMAIL", "").strip()
DASHBOARD_TITLE = "🌬️ WindFarm Turbine Monitoring"

configuration = Configuration()
configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY", "")
configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY", "")
configuration.server_variables["site"] = SITE

# Handle để monitor gửi thông báo (để trống nếu chưa khai báo email)
NOTIFY = f"\n\n@{ALERT_EMAIL}" if ALERT_EMAIL else ""


# ── Helper: timeseries widget ──────────────────────────────────────────────────
def make_timeseries(title: str, metric: str, palette: str,
                    x: int, y: int, w: int = 6, h: int = 3,
                    display=WidgetDisplayType.LINE) -> Widget:
    return Widget(
        definition=TimeseriesWidgetDefinition(
            type=TimeseriesWidgetDefinitionType.TIMESERIES,
            title=title,
            requests=[
                TimeseriesWidgetRequest(
                    queries=[
                        FormulaAndFunctionMetricQueryDefinition(
                            data_source=FormulaAndFunctionMetricDataSource.METRICS,
                            name="q1",
                            query=f"avg:{metric}{{*}} by {{asset_id}}",
                        )
                    ],
                    response_format=FormulaAndFunctionResponseFormat.TIMESERIES,
                    style=TimeseriesRequestStyle(
                        palette=palette,
                        line_type=WidgetLineType.SOLID,
                        line_width=WidgetLineWidth.NORMAL,
                    ),
                    display_type=display,
                )
            ],
        ),
        layout=WidgetLayout(x=x, y=y, width=w, height=h),
    )


# ── Helper: query value (big number) widget ────────────────────────────────────
def make_query_value(title: str, metric: str,
                     x: int, y: int, w: int = 4, h: int = 3) -> Widget:
    return Widget(
        definition=QueryValueWidgetDefinition(
            type=QueryValueWidgetDefinitionType.QUERY_VALUE,
            title=title,
            time=WidgetTime(live_span=WidgetLiveSpan.PAST_ONE_HOUR),
            requests=[
                QueryValueWidgetRequest(
                    queries=[
                        FormulaAndFunctionMetricQueryDefinition(
                            data_source=FormulaAndFunctionMetricDataSource.METRICS,
                            name="q1",
                            query=f"sum:{metric}{{*}}",
                            aggregator=FormulaAndFunctionMetricAggregation.SUM,
                        )
                    ],
                    response_format=FormulaAndFunctionResponseFormat.SCALAR,
                )
            ],
            text_align=WidgetTextAlign.CENTER,
            autoscale=True,
            precision=0,
        ),
        layout=WidgetLayout(x=x, y=y, width=w, height=h),
    )


# ── Helper: event stream widget ────────────────────────────────────────────────
def make_event_stream(title: str, query: str,
                      x: int, y: int, w: int = 12, h: int = 4) -> Widget:
    return Widget(
        definition=EventStreamWidgetDefinition(
            type=EventStreamWidgetDefinitionType.EVENT_STREAM,
            title=title,
            query=query,
            event_size=WidgetEventSize.LARGE,
        ),
        layout=WidgetLayout(x=x, y=y, width=w, height=h),
    )


# ── 1. CREATE DASHBOARD ────────────────────────────────────────────────────────
def create_dashboard(api_client: ApiClient) -> str:
    api = DashboardsApi(api_client)

    # Xoá dashboard cũ cùng tên nếu tồn tại (tránh tạo trùng)
    try:
        for d in api.list_dashboards().dashboards or []:
            if d.title == DASHBOARD_TITLE:
                api.delete_dashboard(dashboard_id=d.id)
                print(f"🗑️  Đã xoá dashboard cũ: {d.id}")
    except Exception as e:
        print(f"(Không kiểm tra được dashboard cũ: {e})")

    body = Dashboard(
        title=DASHBOARD_TITLE,
        description="Real-time monitoring of wind turbine telemetry and ML anomaly detection",
        layout_type=DashboardLayoutType.ORDERED,
        widgets=[
            # Hàng 1: tốc độ gió & công suất
            make_timeseries("🌬️ Wind Speed (m/s)",   "wind_turbine.wind_speed",   "blue",   x=0, y=0, w=6, h=3),
            make_timeseries("⚡ Power Output (kW)",   "wind_turbine.power_output", "green",  x=6, y=0, w=6, h=3),

            # Hàng 2: anomaly timeseries (bars) + tổng số lần bất thường
            make_timeseries("🚨 Anomaly Detection",   "wind_turbine.is_anomaly",   "orange", x=0, y=3, w=8, h=3,
                            display=WidgetDisplayType.BARS),
            make_query_value("Total Anomalies (1h)", "wind_turbine.is_anomaly",               x=8, y=3, w=4, h=3),

            # Hàng 3: event stream — các cảnh báo từ ML Service
            make_event_stream("📣 Anomaly Events", "service:wind_turbine_ml",                 x=0, y=6, w=12, h=4),
        ],
    )

    result = api.create_dashboard(body=body)
    url = f"https://app.{SITE}/dashboard/{result.id}"
    print(f"✅ Dashboard created!\n   URL: {url}\n")
    return result.id


# ── 2. CREATE MONITORS ────────────────────────────────────────────────────────
def monitor_exists(api: MonitorsApi, name: str) -> bool:
    try:
        return any(m.name == name for m in api.list_monitors(name=name))
    except Exception:
        return False


def create_monitors(api_client: ApiClient, dashboard_id: str):
    api = MonitorsApi(api_client)
    dash_url = f"https://app.{SITE}/dashboard/{dashboard_id}"

    # Monitor 1: ML phát hiện bất thường trên bất kỳ tuabin nào
    name1 = "[WindFarm] ⚠️ Anomaly detected on turbine {{asset_id.name}}"
    if monitor_exists(api, name1):
        print("⏭️  Monitor 1 đã tồn tại, bỏ qua")
    else:
        r1 = api.create_monitor(body=Monitor(
            name=name1,
            type=MonitorType.METRIC_ALERT,
            query="sum(last_5m):sum:wind_turbine.is_anomaly{*} by {asset_id} > 0",
            message=(
                "🚨 ML model detected an anomaly on turbine **{{asset_id.name}}**.\n\n"
                f"- Xem chi tiết tại [WindFarm Dashboard]({dash_url}).\n"
                "- Kiểm tra log của ML Service để biết thêm.\n\n"
                "{{#is_alert}}Anomaly is active.{{/is_alert}}"
                "{{#is_recovery}}Turbine is back to normal.{{/is_recovery}}"
                f"{NOTIFY}"
            ),
            options=MonitorOptions(
                thresholds=MonitorThresholds(critical=0.0),
                notify_no_data=False,
                renotify_interval=60,
                include_tags=True,
                new_group_delay=60,
            ),
            tags=["service:wind_turbine_ml", "env:production", "project:windfarm"],
        ))
        print(f"✅ Monitor 1 created (Anomaly Alert): id={r1.id}")

    # Monitor 2: mất dữ liệu — ML Service dừng / cảm biến mất kết nối
    name2 = "[WindFarm] 🔴 No telemetry from turbine {{asset_id.name}} — service may be down"
    if monitor_exists(api, name2):
        print("⏭️  Monitor 2 đã tồn tại, bỏ qua")
    else:
        r2 = api.create_monitor(body=Monitor(
            name=name2,
            type=MonitorType.METRIC_ALERT,
            query="avg(last_10m):avg:wind_turbine.wind_speed{*} by {asset_id} < 0",
            message=(
                "⚠️ Turbine **{{asset_id.name}}** has stopped sending telemetry data for 10+ minutes.\n\n"
                "Possible causes:\n"
                "- ML Service crashed or was stopped\n"
                "- Sensor disconnected\n"
                "- Network issue between Backend and ML Service (kiểm tra link ngrok)\n\n"
                f"Dashboard: {dash_url}"
                f"{NOTIFY}"
            ),
            options=MonitorOptions(
                thresholds=MonitorThresholds(critical=0.0),
                notify_no_data=True,
                no_data_timeframe=10,
                renotify_interval=30,
                include_tags=True,
            ),
            tags=["service:wind_turbine_ml", "env:production", "project:windfarm"],
        ))
        print(f"✅ Monitor 2 created (No Data Alert):  id={r2.id}")


# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not configuration.api_key["apiKeyAuth"] or not configuration.api_key["appKeyAuth"]:
        raise SystemExit("❌ Thiếu DD_API_KEY hoặc DD_APP_KEY trong .env")

    if not ALERT_EMAIL:
        print("⚠️  Chưa có DD_ALERT_EMAIL trong .env — monitor sẽ không gửi email.\n"
              "   Thêm dòng: DD_ALERT_EMAIL=ban@gmail.com\n")

    print(f"🚀 Setting up Datadog for WindFarm (site: {SITE})...\n")

    with ApiClient(configuration) as api_client:
        dash_id = create_dashboard(api_client)
        create_monitors(api_client, dash_id)

    print("\n🎉 All done! Check your Datadog account.")
