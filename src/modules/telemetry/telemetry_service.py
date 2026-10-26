from datetime import datetime, timedelta, timezone
import time
import httpx
from config.settings import settings
from config.datadog_client import (
    track_telemetry_received,
    track_ml_call,
    track_event_created,
    track_db_error,
)
from models.telemetry import TelemetryInput, TelemetryRecord
from models.event import EventInput, EventRecord


async def calculate_derived_features(asset_id: int, current_time):
    """
    Tính 3 features phái sinh bằng MongoDB Aggregation.
    """
    six_hours_ago = current_time - timedelta(hours=6)

    pipeline = [
        {"$match": {
            "asset_id": asset_id,
            "time_stamp": {"$gte": six_hours_ago}
        }},
        {"$group": {
            "_id": None,
            "wind_speed_roll_mean_6h": {"$avg": "$wind_speed"},
            "power_roll_std_6h": {"$stdDevPop": "$power_output"}
        }}
    ]

    result = await TelemetryRecord.aggregate(pipeline).to_list()

    if not result:
        return {
            "wind_speed_roll_mean_6h": 0.0,
            "power_roll_std_6h": 0.0,
            "theoretical_power_index": 0.0
        }

    stats = result[0]

    # TODO: CÔNG THỨC CHÍNH XÁC. TẠM DÙNG CÔNG THỨC GIẢ LẬP
    theoretical_power_index = stats["wind_speed_roll_mean_6h"] * 10.0

    return {
        "wind_speed_roll_mean_6h": round(stats["wind_speed_roll_mean_6h"], 4),
        "power_roll_std_6h": round(stats["power_roll_std_6h"], 4),
        "theoretical_power_index": round(theoretical_power_index, 4)
    }


async def process_telemetry(data: TelemetryInput):
    t_total_start = time.perf_counter()

    # 1. Lưu dữ liệu thô vào DB
    try:
        record = TelemetryRecord(**data.model_dump())
        await record.insert()
        print(f"[BACKEND] Đã lưu Telemetry tuabin {data.asset_id}")
    except Exception as e:
        print(f"[BACKEND] Lỗi lưu DB telemetry: {e}")
        await track_db_error(data.asset_id, "telemetry_insert")
        raise

    # 2. Tính 3 features phái sinh
    derived = await calculate_derived_features(data.asset_id, data.time_stamp)

    # 3. Ghép thành 7 features để gửi sang ML
    ml_payload = {
        "asset_id": data.asset_id,
        "time_stamp": data.time_stamp.isoformat(),
        "wind_speed": data.wind_speed,
        "power_output": data.power_output,
        "ambient_temp": data.ambient_temp,
        "status_type_id": data.status_type_id,
        "wind_speed_roll_mean_6h": derived["wind_speed_roll_mean_6h"],
        "power_roll_std_6h": derived["power_roll_std_6h"],
        "theoretical_power_index": derived["theoretical_power_index"],
    }

    # 4. Ghi nhận telemetry đã nhận thành công lên Datadog
    telemetry_latency_ms = (time.perf_counter() - t_total_start) * 1000
    await track_telemetry_received(data.asset_id, telemetry_latency_ms)

    # 5. Gọi sang ML Service
    t_ml_start = time.perf_counter()
    ml_success = False
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/predict",
                json=ml_payload,
                headers={"ngrok-skip-browser-warning": "1"},
                timeout=10.0
            )
            result = response.json()
            ml_success = True
            print(f"[BACKEND] ML trả về: {result}")

            # 6. Nếu ML phát hiện anomaly, backend tự tạo event
            if result.get("is_anomaly"):
                try:
                    event = EventInput(
                        event_id=int(time.time()),
                        asset_id=data.asset_id,
                        event_label="anomaly",
                        event_start=data.time_stamp,
                        event_end=datetime.now(timezone.utc),
                        event_description=(
                            f"ML phát hiện bất thường. "
                            f"Gió: {data.wind_speed} m/s, "
                            f"Công suất: {data.power_output} kW, "
                            f"Nhiệt độ: {data.ambient_temp}°C"
                        ),
                    )
                    await EventRecord(**event.model_dump()).insert()
                    print(f"[BACKEND] Đã lưu Event anomaly cho tuabin {data.asset_id}")
                    await track_event_created(data.asset_id)
                except Exception as e:
                    print(f"[BACKEND] Lỗi lưu Event: {e}")
                    await track_db_error(data.asset_id, "event_insert")

        except Exception as e:
            print(f"[BACKEND] Lỗi gọi ML: {e}")
        finally:
            ml_latency_ms = (time.perf_counter() - t_ml_start) * 1000
            await track_ml_call(data.asset_id, ml_latency_ms, ml_success)

    return record
