"""
Tự động tạo Dashboard và Monitors trên Datadog qua API.
Đặt file này ở THƯ MỤC GỐC project (cùng chỗ với .env), rồi chạy:

    python setup_datadog.py

.env cần có:
    DD_API_KEY=...
    DD_APP_KEY=...
    DD_SITE=ap1.datadoghq.com
    DD_ALERT_EMAIL=ban@gmail.com  # email nhận cảnh báo từ monitor (tuỳ chọn)

Lưu ý: script XOÁ dashboard/monitor cũ cùng tên rồi tạo lại, nên chạy lại nhiều lần vẫn an toàn.
Metric mà dashboard dùng được gửi từ ml_service/datadog_client.py (phải chạy ML Service trước
để các metric xuất hiện).
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
from datadog_api_client.v1.model.widget_marker import WidgetMarker

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
SITE            = os.getenv("DD_SITE", "datadoghq.com")
ALERT_EMAIL     = os.getenv("DD_ALERT_EMAIL", "").strip()
DASHBOARD_TITLE = "🌬️ WindFarm Turbine Monitoring"
MONITOR_TAGS    = ["service:wind_turbine_ml", "env:production", "project:windfarm"]

configuration = Configuration()
configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY", "")
configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY", "")
configuration.server_variables["site"] = SITE

# Handle để monitor gửi thông báo (để trống nếu chưa khai báo email)
NOTIFY = f"\n\n@{ALERT_EMAIL}" if ALERT_EMAIL else ""


# ── Helpers: widgets ───────────────────────────────────────────────────────────
def _metric_query(name: str, metric: str, agg: str = "avg", by_asset: bool = True) -> FormulaAndFunctionMetricQueryDefinition:
    group = " by {asset_id}" if by_asset else ""
    return FormulaAndFunctionMetricQueryDefinition(
        data_source=FormulaAndFunctionMetricDataSource.METRICS,
        name=name,
        query=f"{agg}:{metric}{{*}}{group}",
    )


def make_timeseries(title: str, metric: str, palette: str,
                    x: int, y: int, w: int = 6, h: int = 3,
                    display=WidgetDisplayType.LINE, markers=None) -> Widget:
    return Widget(
        definition=TimeseriesWidgetDefinition(
            type=TimeseriesWidgetDefinitionType.TIMESERIES,
            title=title,
            requests=[
                TimeseriesWidgetRequest(
                    queries=[_metric_query("q1", metric)],
                    response_format=FormulaAndFunctionResponseFormat.TIMESERIES,
                    style=TimeseriesRequestStyle(
                        palette=palette,
                        line_type=WidgetLineType.SOLID,
                        line_width=WidgetLineWidth.NORMAL,
                    ),
                    display_type=display,
                )
            ],
            **({"markers": markers} if markers else {}),
        ),
        layout=WidgetLayout(x=x, y=y, width=w, height=h),
    )


def make_overlay(title: str, left_metric: str, right_metric: str,
                 x: int, y: int, w: int = 12, h: int = 3) -> Widget:
    """2 metric trên cùng biểu đồ, trục phải riêng — để soi quan hệ gió ↔ công suất."""
    def req(metric, palette, right):
        return TimeseriesWidgetRequest(
            queries=[_metric_query("q1", metric, by_asset=False)],
            response_format=FormulaAndFunctionResponseFormat.TIMESERIES,
            style=TimeseriesRequestStyle(palette=palette, line_type=WidgetLineType.SOLID,
                                         line_width=WidgetLineWidth.NORMAL),
            display_type=WidgetDisplayType.LINE,
            on_right_yaxis=right,
        )
    return Widget(
        definition=TimeseriesWidgetDefinition(
            type=TimeseriesWidgetDefinitionType.TIMESERIES,
            title=title,
            requests=[req(left_metric, "blue", False), req(right_metric, "green", True)],
            show_legend=True,
        ),
        layout=WidgetLayout(x=x, y=y, width=w, height=h),
    )


def make_query_value(title: str, query: str, x: int, y: int, w: int = 2, h: int = 3,
                     precision: int = 0, aggregator=FormulaAndFunctionMetricAggregation.SUM) -> Widget:
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
                            query=query,
                            aggregator=aggregator,
                        )
                    ],
                    response_format=FormulaAndFunctionResponseFormat.SCALAR,
                )
            ],
            text_align=WidgetTextAlign.CENTER,
            autoscale=True,
            precision=precision,
        ),
        layout=WidgetLayout(x=x, y=y, width=w, height=h),
    )


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
def build_widgets():
    P = "wind_turbine."
    return [
        # Hàng 1: tín hiệu chính
        make_timeseries("🌬️ Wind Speed (m/s)",  P + "wind_speed",   "blue",  x=0, y=0, w=6),
        make_timeseries("⚡ Power Output (kW)", P + "power_output", "green", x=6, y=0, w=6),

        # Hàng 2: gió ↔ công suất chung một biểu đồ + nhiệt độ (feature quan trọng #2 của model)
        make_overlay("🔁 Wind Speed vs Power Output", P + "wind_speed", P + "power_output",
                     x=0, y=3, w=8),
        make_timeseries("🌡️ Ambient Temp (°C)", P + "ambient_temp", "warm", x=8, y=3, w=4),

        # Hàng 3: các feature phái sinh (quan trọng #1, #3 và #5 của model)
        make_timeseries("📈 Power Std 6h (độ dao động công suất)", P + "power_roll_std_6h",
                        "purple", x=0, y=6, w=4),
        make_timeseries("🌀 Wind Speed Mean 6h", P + "wind_speed_roll_mean_6h", "cool", x=4, y=6, w=4),
        make_timeseries("🎯 Theoretical Power Index", P + "theoretical_power_index",
                        "grey", x=8, y=6, w=4),

        # Hàng 4: kết quả của model
        make_timeseries("🚨 Anomaly Probability", P + "anomaly_probability", "orange",
                        x=0, y=9, w=6,
                        markers=[WidgetMarker(value="y = 0.5", display_type="warning dashed", label="ngưỡng 0.5"),
                                 WidgetMarker(value="y = 0.7", display_type="error dashed", label="cảnh báo 0.7")]),
        make_timeseries("🚩 Anomaly Flag (0/1)", P + "is_anomaly", "red", x=6, y=9, w=3,
                        display=WidgetDisplayType.BARS),
        make_query_value("Anomalies (1h)", "sum:wind_turbine.ml.anomaly_count{*}.as_count()", x=9, y=9, w=3),

        # Hàng 5: sức khoẻ ML Service + trạng thái turbine
        make_timeseries("⏱️ ML Inference Time (ms)", P + "ml.inference_ms", "grey", x=0, y=12, w=4),
        make_query_value("Predictions (1h)", "sum:wind_turbine.ml.predictions{*}.as_count()", x=4, y=12, w=2),
        make_timeseries("🔧 Status Type ID", P + "status_type_id", "classic", x=6, y=12, w=6),

        # Hàng 6: event cảnh báo từ ML Service
        make_event_stream("📣 Anomaly Events", "tags:service:wind_turbine_ml", x=0, y=15, w=12, h=4),

        # Hàng 7: Backend health
        make_timeseries("📥 Telemetry Ingestion Rate", "wind_turbine.backend.telemetry_count",
                        "blue", x=0, y=19, w=4, display=WidgetDisplayType.BARS),
        make_timeseries("⏱️ Backend Processing Latency (ms)", "wind_turbine.backend.telemetry_latency_ms",
                        "cool", x=4, y=19, w=4),
        make_query_value("Events Created (1h)",
                         "sum:wind_turbine.backend.event_created_count{*}.as_count()",
                         x=8, y=19, w=2),
        make_query_value("DB Errors (1h)",
                         "sum:wind_turbine.backend.db_error_count{*}.as_count()",
                         x=10, y=19, w=2),

        # Hàng 8: ML call health từ phía backend
        make_timeseries("🔗 ML Call Latency (ms)", "wind_turbine.backend.ml_call_latency_ms",
                        "grey", x=0, y=22, w=4),
        make_timeseries("❌ ML Call Errors", "wind_turbine.backend.ml_call_error_count",
                        "red", x=4, y=22, w=4, display=WidgetDisplayType.BARS),
        make_query_value("ML Calls (1h)",
                         "sum:wind_turbine.backend.ml_call_count{*}.as_count()",
                         x=8, y=22, w=2),
        make_query_value("ML Errors (1h)",
                         "sum:wind_turbine.backend.ml_call_error_count{*}.as_count()",
                         x=10, y=22, w=2),
    ]


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
        description="Real-time monitoring of wind turbine telemetry, ML anomaly detection and ML service health",
        layout_type=DashboardLayoutType.ORDERED,
        widgets=build_widgets(),
    )

    result = api.create_dashboard(body=body)
    print(f"✅ Dashboard created!\n   URL: https://app.{SITE}/dashboard/{result.id}\n")
    return result.id


# ── 2. CREATE MONITORS ────────────────────────────────────────────────────────
def recreate_monitor(api: MonitorsApi, monitor: Monitor, label: str):
    """Xoá monitor cũ cùng tên (nếu có) rồi tạo lại, để định nghĩa luôn là bản mới nhất."""
    try:
        for m in api.list_monitors(name=monitor.name):
            if m.name == monitor.name:
                api.delete_monitor(monitor_id=m.id)
                print(f"🗑️  Đã xoá monitor cũ: {m.id}")
    except Exception as e:
        print(f"(Không kiểm tra được monitor cũ: {e})")
    created = api.create_monitor(body=monitor)
    print(f"✅ {label}: id={created.id}")


def create_monitors(api_client: ApiClient, dashboard_id: str):
    api = MonitorsApi(api_client)
    dash_url = f"https://app.{SITE}/dashboard/{dashboard_id}"

    # Monitor 1: có nhiều điểm bất thường trong 5 phút (giảm báo động giả)
    # warning khi >= 1, critical khi >= 3. Khi demo ít dữ liệu có thể hạ critical xuống 1.
    recreate_monitor(api, Monitor(
        name="[WindFarm] ⚠️ Anomaly detected on turbine {{asset_id.name}}",
        type=MonitorType.METRIC_ALERT,
        query="sum(last_5m):sum:wind_turbine.ml.anomaly_count{*} by {asset_id}.as_count() >= 3",
        message=(
            "🚨 ML model detected repeated anomalies on turbine **{{asset_id.name}}**.\n\n"
            f"- Xem chi tiết tại [WindFarm Dashboard]({dash_url}).\n"
            "- Xem các feature (Power Std 6h, Ambient Temp...) để biết nguyên nhân.\n\n"
            "{{#is_alert}}Anomaly is active.{{/is_alert}}"
            "{{#is_warning}}Anomaly detected, still below the alert threshold.{{/is_warning}}"
            "{{#is_recovery}}Turbine is back to normal.{{/is_recovery}}"
            f"{NOTIFY}"
        ),
        options=MonitorOptions(
            thresholds=MonitorThresholds(critical=3.0, warning=1.0),
            notify_no_data=False,
            renotify_interval=60,
            include_tags=True,
            new_group_delay=60,
        ),
        tags=MONITOR_TAGS,
    ), "Monitor 1 (Anomaly count)")

    # Monitor 2: cảnh báo sớm khi xác suất bất thường cao liên tục
    recreate_monitor(api, Monitor(
        name="[WindFarm] 📈 High anomaly probability on turbine {{asset_id.name}}",
        type=MonitorType.METRIC_ALERT,
        query="avg(last_5m):avg:wind_turbine.anomaly_probability{*} by {asset_id} > 0.7",
        message=(
            "⚠️ Anomaly probability on turbine **{{asset_id.name}}** is high "
            "(avg over 5 minutes > 70%). Turbine may be degrading.\n\n"
            f"Dashboard: {dash_url}"
            f"{NOTIFY}"
        ),
        options=MonitorOptions(
            thresholds=MonitorThresholds(critical=0.7, warning=0.5),
            notify_no_data=False,
            renotify_interval=60,
            include_tags=True,
            new_group_delay=60,
        ),
        tags=MONITOR_TAGS,
    ), "Monitor 2 (High probability)")

    # Monitor 3: mất dữ liệu — ML Service dừng / cảm biến mất kết nối
    # Điều kiện "< 0" không bao giờ đúng với tốc độ gió thực, nên monitor chỉ kêu
    # thông qua notify_no_data khi 10 phút không có điểm dữ liệu nào.
    recreate_monitor(api, Monitor(
        name="[WindFarm] 🔴 No telemetry from turbine {{asset_id.name}} — service may be down",
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
        tags=MONITOR_TAGS,
    ), "Monitor 3 (No data)")

    # Monitor 4: ML Service liên tục bị lỗi khi gọi từ backend
    recreate_monitor(api, Monitor(
        name="[WindFarm] 🔌 ML Service unreachable from backend",
        type=MonitorType.METRIC_ALERT,
        query="sum(last_5m):sum:wind_turbine.backend.ml_call_error_count{*}.as_count() >= 3",
        message=(
            "🔌 Backend không thể gọi ML Service trong 5 phút qua (>= 3 lần lỗi).\n\n"
            "Kiểm tra:\n"
            "- ML Service có đang chạy không?\n"
            "- Link ngrok có còn hiệu lực không?\n"
            "- Biến `ML_SERVICE_URL` trong `.env` có đúng không?\n\n"
            f"Dashboard: {dash_url}"
            f"{NOTIFY}"
        ),
        options=MonitorOptions(
            thresholds=MonitorThresholds(critical=3.0, warning=1.0),
            notify_no_data=False,
            renotify_interval=30,
            include_tags=True,
        ),
        tags=MONITOR_TAGS,
    ), "Monitor 4 (ML call errors)")

    # Monitor 5: Backend latency cao bất thường
    recreate_monitor(api, Monitor(
        name="[WindFarm] 🐢 Backend processing latency is high",
        type=MonitorType.METRIC_ALERT,
        query="avg(last_5m):avg:wind_turbine.backend.telemetry_latency_ms{*} > 2000",
        message=(
            "⚠️ Backend đang xử lý telemetry chậm (trung bình > 2s trong 5 phút).\n\n"
            "Nguyên nhân có thể:\n"
            "- MongoDB query chậm (kiểm tra index)\n"
            "- Aggregation pipeline 6h tốn tài nguyên\n\n"
            f"Dashboard: {dash_url}"
            f"{NOTIFY}"
        ),
        options=MonitorOptions(
            thresholds=MonitorThresholds(critical=2000.0, warning=1000.0),
            notify_no_data=False,
            renotify_interval=60,
            include_tags=True,
        ),
        tags=MONITOR_TAGS,
    ), "Monitor 5 (High backend latency)")
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